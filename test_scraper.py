#!/usr/bin/env python3
"""Test NQ OI Scraper"""

import asyncio
from nq_oi_scraper import NQOIScraper

async def test_scraper():
    scraper = NQOIScraper()
    try:
        print("Testing scraper...")
        strikes = await scraper.scrape_nq_oi()
        print(f"Found {len(strikes)} strikes")
        
        if strikes:
            print("Sample strikes:")
            for strike in strikes[:5]:
                print(f"  Strike {strike.strike}: Call OI {strike.call_oi}, Put OI {strike.put_oi}")
        
        features = scraper.compute_features(strikes)
        print(f"Features: DTE {features.nearest_dte}, Pin candidate: {features.pin_candidate_strike}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_scraper())