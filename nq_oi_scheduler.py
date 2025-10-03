#!/usr/bin/env python3
"""NQ OI Scraper Scheduler - Runs daily pre-market"""

import asyncio
import schedule
import time
import logging
from datetime import datetime
from nq_oi_scraper import run_scraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nq_oi_scraper.log'),
        logging.StreamHandler()
    ]
)

async def scheduled_scrape():
    """Run the scraper with error handling and logging"""
    try:
        logging.info("Starting scheduled NQ OI scrape")
        await run_scraper()
        logging.info("NQ OI scrape completed successfully")
    except Exception as e:
        logging.error(f"NQ OI scrape failed: {str(e)}")

def run_scheduled_scrape():
    """Wrapper to run async scraper in sync context"""
    asyncio.run(scheduled_scrape())

# Schedule daily runs
schedule.every().day.at("06:00").do(run_scheduled_scrape)  # Pre-market
schedule.every().day.at("10:00").do(run_scheduled_scrape)  # Market open
schedule.every().day.at("14:00").do(run_scheduled_scrape)  # Mid-day
schedule.every().day.at("18:00").do(run_scheduled_scrape)  # After close

if __name__ == "__main__":
    logging.info("NQ OI Scheduler started")
    
    # Run once immediately
    run_scheduled_scrape()
    
    # Keep running scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(60)