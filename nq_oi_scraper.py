#!/usr/bin/env python3
"""NQ Options Open Interest Scraper for CME QuikStrike"""

import os
import json
import hashlib
from datetime import datetime, date
from typing import List, Dict, Optional
from dataclasses import dataclass
import asyncio
import asyncpg
from playwright.async_api import async_playwright
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

@dataclass
class OIStrike:
    expiry_date: date
    dte: int
    strike: float
    call_oi: int
    put_oi: int
    total_oi: int

@dataclass
class OIFeatures:
    nearest_expiry_date: date
    nearest_dte: int
    top_put_strikes: List[Dict]
    top_call_strikes: List[Dict]
    pin_candidate_strike: Optional[float]
    spot_at_compute: Optional[float]

class NQOIScraper:
    def __init__(self):
        self.qs_url = os.getenv('QS_URL', 'https://www.cmegroup.com/markets/equities/nasdaq/e-mini-nasdaq-100.html')
        self.nq_product_value = os.getenv('NQ_PRODUCT_VALUE', 'NQ')
        self.timeout_ms = int(os.getenv('TIMEOUT_MS', '30000'))
        self.db_url = os.getenv('DB_URL', 'postgresql://localhost/trading')
        self.min_oi_threshold = int(os.getenv('MIN_OI_THRESHOLD', '1000'))
        self.top_n_strikes = int(os.getenv('TOP_N_STRIKES', '3'))

    async def scrape_nq_oi(self) -> List[OIStrike]:
        """Scrape NQ options OI from CME QuikStrike"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--disable-blink-features=AutomationControlled', '--disable-dev-shm-usage', '--no-sandbox']
                )
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    extra_http_headers={
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "en-US,en;q=0.5",
                        "Connection": "keep-alive"
                    }
                )
                page = await context.new_page()
                
                try:
                    # Navigate to QuikStrike directly
                    qs_url = 'https://www.cmegroup.com/tools-information/quikstrike/options-calendar.html'
                    print(f"Attempting to reach CME QuikStrike: {qs_url}")
                    await page.goto(qs_url, wait_until="domcontentloaded", timeout=60000)
                    
                    # Wait for QuikStrike iframe
                    print("Waiting for QuikStrike iframe...")
                    await page.wait_for_selector("iframe", timeout=30000)
                    iframe = page.frame_locator("iframe").first
                    
                    # Select NQ product
                    print("Selecting NQ product...")
                    await iframe.locator('select[name="product"]').wait_for(state="visible", timeout=30000)
                    await iframe.locator('select[name="product"]').select_option(self.nq_product_value)
                    await page.wait_for_timeout(2000)
                    
                    # Navigate to Open Interest
                    print("Navigating to Open Interest section...")
                    await iframe.locator('button:has-text("Open Interest"), a:has-text("Open Interest")').first.click()
                    await iframe.wait_for_load_state("networkidle")
                    
                    # Extract OI data
                    print("Extracting OI data...")
                    strikes_data = []
                    rows = await iframe.locator('table tbody tr').all()
                    
                    for row in rows:
                        cells = await row.locator('td').all()
                        if len(cells) >= 5:
                            strike = float(await cells[0].text_content())
                            call_oi = int((await cells[1].text_content()).replace(',', '') or '0')
                            put_oi = int((await cells[2].text_content()).replace(',', '') or '0')
                            dte = int(await cells[3].text_content() or '0')
                            
                            strikes_data.append(OIStrike(
                                expiry_date=date.today(),
                                dte=dte,
                                strike=strike,
                                call_oi=call_oi,
                                put_oi=put_oi,
                                total_oi=call_oi + put_oi
                            ))
                    
                    print(f"Successfully extracted {len(strikes_data)} strikes")
                    return strikes_data
                    
                finally:
                    await browser.close()
                    
        except Exception as e:
            print(f"Scraping failed: {e}")
            print("This may work when deployed to Railway cloud due to different IP ranges")
            raise e

    def compute_features(self, strikes: List[OIStrike]) -> OIFeatures:
        """Compute OI features from raw strikes"""
        if not strikes:
            return OIFeatures(date.today(), 0, [], [], None, None)
        
        # Find nearest expiry (smallest DTE >= 0)
        valid_strikes = [s for s in strikes if s.dte >= 0]
        nearest_dte = min(s.dte for s in valid_strikes)
        nearest_strikes = [s for s in valid_strikes if s.dte == nearest_dte]
        
        # Filter by minimum OI threshold
        filtered_strikes = [s for s in nearest_strikes if s.total_oi >= self.min_oi_threshold]
        
        # Top put strikes (highest put OI)
        top_puts = sorted(filtered_strikes, key=lambda x: x.put_oi, reverse=True)[:self.top_n_strikes]
        top_put_strikes = [{"strike": s.strike, "oi": s.put_oi} for s in top_puts]
        
        # Top call strikes (highest call OI)
        top_calls = sorted(filtered_strikes, key=lambda x: x.call_oi, reverse=True)[:self.top_n_strikes]
        top_call_strikes = [{"strike": s.strike, "oi": s.call_oi} for s in top_calls]
        
        # Pin candidate (max total OI for DTE 0, soft for DTE 1)
        pin_candidate = None
        if nearest_dte == 0:
            max_total_oi_strike = max(filtered_strikes, key=lambda x: x.total_oi, default=None)
            pin_candidate = max_total_oi_strike.strike if max_total_oi_strike else None
        
        return OIFeatures(
            nearest_expiry_date=date.today(),
            nearest_dte=nearest_dte,
            top_put_strikes=top_put_strikes,
            top_call_strikes=top_call_strikes,
            pin_candidate_strike=pin_candidate,
            spot_at_compute=None  # Would get from market data
        )

    async def store_data(self, strikes: List[OIStrike], features: OIFeatures):
        """Store data in PostgreSQL"""
        conn = await asyncpg.connect(self.db_url)
        try:
            # Store raw snapshot
            payload = json.dumps([s.__dict__ for s in strikes], default=str)
            payload_hash = hashlib.md5(payload.encode()).hexdigest()
            
            snapshot_id = await conn.fetchval("""
                INSERT INTO raw_quikstrike_snapshots (scraped_at, source_url, instrument, payload, hash)
                VALUES ($1, $2, $3, $4, $5) RETURNING id
            """, datetime.now(), self.qs_url, 'NQ', payload, payload_hash)
            
            # Store strikes
            for strike in strikes:
                await conn.execute("""
                    INSERT INTO oi_strikes (scraped_at, instrument, expiry_date, dte, strike, call_oi, put_oi, total_oi, source_snapshot_id)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """, datetime.now(), 'NQ', strike.expiry_date, strike.dte, strike.strike, 
                strike.call_oi, strike.put_oi, strike.total_oi, snapshot_id)
            
            # Store features
            await conn.execute("""
                INSERT INTO oi_features (computed_at, instrument, nearest_expiry_date, nearest_dte, 
                                       top_put_strikes, top_call_strikes, pin_candidate_strike, spot_at_compute, rules_version)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, datetime.now(), 'NQ', features.nearest_expiry_date, features.nearest_dte,
            json.dumps(features.top_put_strikes), json.dumps(features.top_call_strikes),
            features.pin_candidate_strike, features.spot_at_compute, 'v1.0')
            
        finally:
            await conn.close()

# FastAPI App
app = FastAPI(title="NQ Options OI API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/nq/levels/daily")
async def get_daily_levels():
    """Get daily NQ OI levels for overlay"""
    conn = await asyncpg.connect(os.getenv('DB_URL', 'postgresql://localhost/trading'))
    try:
        row = await conn.fetchrow("""
            SELECT * FROM oi_features WHERE instrument = 'NQ' 
            ORDER BY computed_at DESC LIMIT 1
        """)
        
        if not row:
            raise HTTPException(status_code=404, detail="No data available")
        
        return {
            "date": row['computed_at'].date().isoformat(),
            "nearest_dte": row['nearest_dte'],
            "top_puts": json.loads(row['top_put_strikes']),
            "top_calls": json.loads(row['top_call_strikes']),
            "pin_candidate": row['pin_candidate_strike'],
            "rules_version": row['rules_version'],
            "generated_at": row['computed_at'].isoformat()
        }
    finally:
        await conn.close()

@app.get("/nq/oi/latest")
async def get_latest_oi():
    """Get latest OI features"""
    conn = await asyncpg.connect(os.getenv('DB_URL', 'postgresql://localhost/trading'))
    try:
        row = await conn.fetchrow("""
            SELECT * FROM oi_features WHERE instrument = 'NQ' 
            ORDER BY computed_at DESC LIMIT 1
        """)
        
        if not row:
            raise HTTPException(status_code=404, detail="No data available")
        
        return dict(row)
    finally:
        await conn.close()

async def run_scraper():
    """Main scraper execution"""
    try:
        scraper = NQOIScraper()
        strikes = await scraper.scrape_nq_oi()
        features = scraper.compute_features(strikes)
        await scraper.store_data(strikes, features)
        print(f"SUCCESS: Scraped {len(strikes)} strikes, computed features for DTE {features.nearest_dte}")
        return True
    except Exception as e:
        print(f"SCRAPER FAILED: {e}")
        print("Deploy to Railway cloud - local networks may be blocked by CME")
        return False

if __name__ == "__main__":
    if len(os.sys.argv) > 1 and os.sys.argv[1] == "scrape":
        asyncio.run(run_scraper())
    else:
        port = int(os.getenv("PORT", 8001))
        print(f"Starting NQ OI API server on port {port}")
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")