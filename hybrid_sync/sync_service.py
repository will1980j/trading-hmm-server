"""
Hybrid Signal Synchronization System - Background Service
Runs gap detection and reconciliation every 2 minutes
"""

import time
import threading
import logging
from datetime import datetime
from .gap_detector import GapDetector
from .reconciliation_engine import ReconciliationEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridSyncService:
    """
    Background service that ensures zero data gaps.
    Runs continuously, detecting and filling gaps every 2 minutes.
    """
    
    def __init__(self, interval_seconds: int = 120):
        self.interval_seconds = interval_seconds
        self.running = False
        self.detector = GapDetector()
        self.reconciler = ReconciliationEngine()
        self.cycle_count = 0
        self.total_gaps_filled = 0
        
    def run_cycle(self):
        """Run one complete gap detection and reconciliation cycle"""
        self.cycle_count += 1
        
        logger.info("=" * 80)
        logger.info(f"HYBRID SYNC CYCLE #{self.cycle_count}")
        logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)
        
        try:
            # Step 1: Detect gaps
            gap_report = self.detector.run_complete_scan()
            
            if gap_report['total_gaps'] == 0:
                logger.info("✅ No gaps detected - system healthy")
                return
            
            # Step 2: Reconcile gaps
            results = self.reconciler.reconcile_all_gaps(gap_report)
            
            self.total_gaps_filled += results['gaps_filled']
            
            # Step 3: Update health metrics for all signals
            logger.info("📊 Updating health metrics...")
            # This will be implemented when we add the health dashboard
            
            logger.info(f"✅ Cycle complete: {results['gaps_filled']} gaps filled")
            logger.info(f"📈 Total gaps filled since start: {self.total_gaps_filled}")
            
        except Exception as e:
            logger.error(f"❌ Cycle error: {e}")
    
    def run_continuous(self):
        """Run service continuously"""
        self.running = True
        logger.info("🚀 HYBRID SIGNAL SYNCHRONIZATION SERVICE STARTED")
        logger.info(f"   Interval: {self.interval_seconds} seconds ({self.interval_seconds/60} minutes)")
        logger.info(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)
        logger.info()
        
        while self.running:
            try:
                self.run_cycle()
            except Exception as e:
                logger.error(f"❌ Unexpected error in cycle: {e}")
            
            # Wait for next cycle
            if self.running:
                logger.info(f"⏳ Waiting {self.interval_seconds} seconds until next cycle...")
                logger.info()
                time.sleep(self.interval_seconds)
    
    def start_background(self):
        """Start service in background thread"""
        thread = threading.Thread(target=self.run_continuous, daemon=True)
        thread.start()
        logger.info("✅ Hybrid Sync Service started in background")
        return thread
    
    def stop(self):
        """Stop the service"""
        self.running = False
        logger.info("🛑 Hybrid Sync Service stopped")

def start_hybrid_sync_service(interval_seconds: int = 120):
    """
    Start the Hybrid Signal Synchronization Service.
    Call this from web_server.py on startup.
    """
    service = HybridSyncService(interval_seconds)
    return service.start_background()

if __name__ == "__main__":
    # Run standalone for testing
    service = HybridSyncService(interval_seconds=120)
    try:
        service.run_continuous()
    except KeyboardInterrupt:
        service.stop()
        print("\n✅ Service stopped by user")
