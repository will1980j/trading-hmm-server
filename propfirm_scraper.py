#!/usr/bin/env python3
"""
PropFirmMatch Scraper - Auto-updates prop firm database
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from database.railway_db import RailwayDB

class PropFirmScraper:
    def __init__(self):
        self.db = RailwayDB()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_propfirmmatch(self):
        """Scrape PropFirmMatch for latest deals"""
        response = None
        try:
            url = "https://propfirmmatch.com/prop-firms"
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            firms = []
            
            # Find prop firm cards/listings
            firm_cards = soup.find_all(['div', 'article'], class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['firm', 'card', 'listing', 'company']
            ))
            
            for card in firm_cards[:20]:  # Limit to first 20
                try:
                    firm_data = self.extract_firm_data(card)
                    if firm_data:
                        firms.append(firm_data)
                except Exception as e:
                    continue
            
            return firms
            
        except Exception as e:
            print(f"PropFirmMatch scraping failed: {e}")
            return []
        finally:
            if response:
                response.close()
    
    def extract_firm_data(self, card):
        """Extract firm data from HTML card"""
        try:
            # Extract firm name
            name_elem = card.find(['h1', 'h2', 'h3', 'h4'], string=lambda x: x and len(x) > 2)
            if not name_elem:
                name_elem = card.find('a', href=lambda x: x and 'firm' in x.lower())
            
            firm_name = name_elem.get_text().strip() if name_elem else None
            if not firm_name or len(firm_name) < 3:
                return None
            
            # Extract website
            website_elem = card.find('a', href=lambda x: x and x.startswith('http'))
            website = website_elem.get('href') if website_elem else None
            
            # Extract funding amount
            funding_text = card.get_text()
            max_funding = self.extract_funding_amount(funding_text)
            
            # Extract profit split
            profit_split = self.extract_profit_split(funding_text)
            
            # Determine market type
            market_type = 'Forex'
            if any(word in funding_text.lower() for word in ['futures', 'es', 'nq', 'ym', 'rtY']):
                market_type = 'Futures'
            elif any(word in funding_text.lower() for word in ['both', 'forex and futures']):
                market_type = 'Both'
            
            return {
                'firm_name': firm_name,
                'website': website,
                'status': 'challenge',
                'market_type': market_type,
                'account_size': max_funding // 10 if max_funding else 100000,  # Estimate starting size
                'max_funding': max_funding or 1000000,
                'profit_split': profit_split or 80,
                'currency': 'USD',
                'monthly_profit': 0,
                'month_year': datetime.now().strftime('%Y-%m')
            }
            
        except Exception as e:
            return None
    
    def extract_funding_amount(self, text):
        """Extract max funding amount from text"""
        import re
        
        # Look for patterns like $2M, $500K, $1,000,000
        patterns = [
            r'\$(\d+(?:,\d{3})*(?:\.\d+)?)\s*[Mm](?:illion)?',
            r'\$(\d+(?:,\d{3})*(?:\.\d+)?)\s*[Kk](?:thousand)?',
            r'\$(\d{1,3}(?:,\d{3})*)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                amount_str = matches[-1].replace(',', '')  # Get last/largest match
                amount = float(amount_str)
                
                if 'M' in text or 'million' in text.lower():
                    return int(amount * 1000000)
                elif 'K' in text or 'thousand' in text.lower():
                    return int(amount * 1000)
                else:
                    return int(amount)
        
        return None
    
    def extract_profit_split(self, text):
        """Extract profit split percentage"""
        import re
        
        # Look for patterns like 80%, 90% split
        matches = re.findall(r'(\d{2})%', text)
        if matches:
            splits = [int(m) for m in matches if 50 <= int(m) <= 95]
            return max(splits) if splits else None
        
        return None
    
    def update_database(self, firms):
        """Update database with scraped firms"""
        updated_count = 0
        
        for firm in firms:
            try:
                cursor = self.db.conn.cursor()
                cursor.execute("""
                    INSERT INTO prop_firms 
                    (firm_name, website, status, market_type, account_size, max_funding, 
                     profit_split, currency, monthly_profit, month_year)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (firm_name, month_year) DO UPDATE SET
                    max_funding = EXCLUDED.max_funding,
                    profit_split = EXCLUDED.profit_split,
                    website = EXCLUDED.website,
                    updated_at = NOW()
                """, (
                    firm['firm_name'],
                    firm['website'],
                    firm['status'],
                    firm['market_type'],
                    firm['account_size'],
                    firm['max_funding'],
                    firm['profit_split'],
                    firm['currency'],
                    firm['monthly_profit'],
                    firm['month_year']
                ))
                self.db.conn.commit()
                updated_count += 1
                
            except Exception as e:
                self.db.conn.rollback()
                print(f"Failed to update {firm['firm_name']}: {e}")
        
        return updated_count
    
    def run_scraper(self):
        """Run the complete scraping process"""
        try:
            print(f"🔍 Starting PropFirmMatch scraper at {datetime.now()}")
            
            # Scrape PropFirmMatch
            firms = self.scrape_propfirmmatch()
            print(f"📊 Found {len(firms)} prop firms")
            
            if firms:
                updated = self.update_database(firms)
                print(f"✅ Updated {updated} firms in database")
            
            return len(firms)
        except Exception as e:
            print(f"Scraper error: {e}")
            return 0

def run_daily_scraper():
    """Run scraper - called by scheduler"""
    scraper = PropFirmScraper()
    return scraper.run_scraper()

if __name__ == "__main__":
    run_daily_scraper()