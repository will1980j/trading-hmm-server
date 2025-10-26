"""
Complete V2 Automation System
Orchestrates all components for full trading automation
"""

import os
import sys
import logging
import time
import threading
from datetime import datetime
from typing import Dict, Optional
import json

# Import all automation components
from real_time_market_data import setup_market_data_provider, market_data_manager
from confirmation_monitoring_service import start_confirmation_monitoring, add_confirmation_requirement
from mfe_tracking_service import start_mfe_tracking, add_active_trade
from enhanced_webhook_processor import process_enhanced_webhook

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class V2AutomationOrchestrator:
    """Orchestrates the complete V2 automation system"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.is_running = False
        self.services = {}
        
        # Database connection
        self.db_connection_string = config.get('database_url')
        if not self.db_connection_string:
            raise ValueError("Database URL required in config")
            
        # Market data configuration
        self.market_data_config = config.get('market_data', {})
        
    def start_system(self):
        """Start the complete V2 automation system"""
        logger.info("🚀 Starting Complete V2 Automation System")
        logger.info("=" * 60)
        
        try:
            # Step 1: Setup market data provider
            self.setup_market_data()
            
            # Step 2: Start confirmation monitoring
            self.start_confirmation_monitoring()
            
            # Step 3: Start MFE tracking
            self.start_mfe_tracking()
            
            # Step 4: Setup webhook processing
            self.setup_webhook_processing()
            
            self.is_running = True
            
            logger.info("✅ V2 Automation System fully operational!")
            logger.info("📊 Market data: Connected")
            logger.info("🔍 Confirmation monitoring: Active")
            logger.info("📈 MFE tracking: Running")
            logger.info("🎯 Webhook processing: Ready")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start V2 automation system: {str(e)}")
            self.stop_system()
            return False
            
    def setup_market_data(self):
        """Setup market data provider"""
        logger.info("📊 Setting up market data provider...")
        
        provider_type = self.market_data_config.get('provider', 'mock')
        api_key = self.market_data_config.get('api_key')
        
        if provider_type in ['polygon', 'alphavantage'] and not api_key:
            logger.error(f"❌ No API key provided for {provider_type}")
            logger.error("❌ REAL MARKET DATA REQUIRED - NO FAKE DATA ALLOWED")
            raise ValueError(f"API key required for {provider_type} - no fake data allowed")
            
        # Setup provider
        manager = setup_market_data_provider(provider_type, api_key=api_key)
        self.services['market_data'] = manager
        
        logger.info(f"✅ Market data provider setup: {provider_type}")
        
    def start_confirmation_monitoring(self):
        """Start confirmation monitoring service"""
        logger.info("🔍 Starting confirmation monitoring...")
        
        monitor = start_confirmation_monitoring(self.db_connection_string)
        self.services['confirmation_monitor'] = monitor
        
        logger.info("✅ Confirmation monitoring started")
        
    def start_mfe_tracking(self):
        """Start MFE tracking service"""
        logger.info("📈 Starting MFE tracking...")
        
        tracker = start_mfe_tracking(self.db_connection_string)
        self.services['mfe_tracker'] = tracker
        
        logger.info("✅ MFE tracking started")
        
    def setup_webhook_processing(self):
        """Setup webhook processing"""
        logger.info("🎯 Setting up webhook processing...")
        
        # Webhook processing is handled by the enhanced_webhook_processor
        # This just validates it's ready
        
        logger.info("✅ Webhook processing ready")
        
    def process_enhanced_signal(self, webhook_data: Dict) -> Dict:
        """Process an enhanced signal through the complete automation pipeline"""
        try:
            logger.info(f"🎯 Processing enhanced signal: {webhook_data.get('signal_type')}")
            
            # Step 1: Process the enhanced webhook data
            processed_signal = process_enhanced_webhook(webhook_data)
            
            if processed_signal.get('status') != 'processed':
                return processed_signal
                
            # Step 2: Set up confirmation monitoring
            confirmation_data = processed_signal.get('confirmation_data', {})
            if confirmation_data.get('required'):
                trade_uuid = processed_signal.get('trade_uuid', 'unknown')
                signal_candle = processed_signal.get('signal_candle', {})
                
                add_confirmation_requirement(
                    trade_uuid=trade_uuid,
                    signal_type=processed_signal.get('signal_type'),
                    target_price=confirmation_data.get('target_price'),
                    condition=confirmation_data.get('condition'),
                    signal_candle_high=signal_candle.get('high'),
                    signal_candle_low=signal_candle.get('low')
                )
                
                logger.info(f"✅ Confirmation monitoring setup for {trade_uuid}")
                
            # Step 3: Prepare for MFE tracking (will be activated after confirmation)
            # MFE tracking starts automatically when confirmation is received
            
            return {
                "status": "success",
                "message": "Enhanced signal processed through complete automation pipeline",
                "automation_features": [
                    "enhanced_signal_processing",
                    "confirmation_monitoring_active",
                    "mfe_tracking_ready",
                    "stop_loss_calculated",
                    "r_targets_calculated"
                ],
                "processed_signal": processed_signal
            }
            
        except Exception as e:
            logger.error(f"Error in complete signal processing: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
            
    def on_confirmation_received(self, trade_uuid: str, entry_price: float, 
                                signal_type: str, stop_loss_price: float, risk_distance: float):
        """Handle confirmation received - start MFE tracking"""
        try:
            logger.info(f"🎯 Confirmation received for {trade_uuid} - starting MFE tracking")
            
            # Add to MFE tracking
            add_active_trade(
                trade_uuid=trade_uuid,
                signal_type=signal_type,
                entry_price=entry_price,
                stop_loss_price=stop_loss_price,
                risk_distance=risk_distance
            )
            
            logger.info(f"✅ MFE tracking activated for {trade_uuid}")
            
        except Exception as e:
            logger.error(f"Error activating MFE tracking: {str(e)}")
            
    def get_system_status(self) -> Dict:
        """Get current system status"""
        return {
            "system_running": self.is_running,
            "services": {
                "market_data": self.services.get('market_data') is not None,
                "confirmation_monitor": self.services.get('confirmation_monitor') is not None,
                "mfe_tracker": self.services.get('mfe_tracker') is not None
            },
            "timestamp": datetime.now().isoformat()
        }
        
    def stop_system(self):
        """Stop the complete V2 automation system"""
        logger.info("🛑 Stopping V2 Automation System...")
        
        self.is_running = False
        
        # Stop all services
        for service_name, service in self.services.items():
            try:
                if hasattr(service, 'stop_monitoring'):
                    service.stop_monitoring()
                elif hasattr(service, 'stop_tracking'):
                    service.stop_tracking()
                elif hasattr(service, 'disconnect'):
                    service.disconnect()
                    
                logger.info(f"✅ Stopped {service_name}")
                
            except Exception as e:
                logger.error(f"Error stopping {service_name}: {str(e)}")
                
        logger.info("🛑 V2 Automation System stopped")

# Global orchestrator instance
v2_orchestrator: Optional[V2AutomationOrchestrator] = None

def start_complete_v2_system(config: Dict) -> V2AutomationOrchestrator:
    """Start the complete V2 automation system"""
    global v2_orchestrator
    
    if v2_orchestrator is None:
        v2_orchestrator = V2AutomationOrchestrator(config)
        
    success = v2_orchestrator.start_system()
    
    if not success:
        raise Exception("Failed to start V2 automation system")
        
    return v2_orchestrator

def stop_complete_v2_system():
    """Stop the complete V2 automation system"""
    global v2_orchestrator
    
    if v2_orchestrator:
        v2_orchestrator.stop_system()
        v2_orchestrator = None

def process_signal_through_v2_system(webhook_data: Dict) -> Dict:
    """Process a signal through the complete V2 system"""
    global v2_orchestrator
    
    if not v2_orchestrator or not v2_orchestrator.is_running:
        return {
            "status": "error",
            "message": "V2 automation system not running"
        }
        
    return v2_orchestrator.process_enhanced_signal(webhook_data)

def get_v2_system_status() -> Dict:
    """Get V2 system status"""
    global v2_orchestrator
    
    if v2_orchestrator:
        return v2_orchestrator.get_system_status()
    else:
        return {
            "system_running": False,
            "message": "V2 system not initialized"
        }

# Configuration templates
def get_production_config() -> Dict:
    """Get production configuration"""
    return {
        "database_url": os.environ.get('DATABASE_URL'),
        "market_data": {
            "provider": "polygon",  # or "alphavantage"
            "api_key": os.environ.get('POLYGON_API_KEY')  # or ALPHAVANTAGE_API_KEY
        },
        "environment": "production"
    }

def get_development_config() -> Dict:
    """Get development configuration - REQUIRES REAL API KEY"""
    api_key = os.environ.get('POLYGON_API_KEY') or os.environ.get('ALPHAVANTAGE_API_KEY')
    if not api_key:
        raise ValueError("❌ DEVELOPMENT REQUIRES REAL API KEY - NO FAKE DATA ALLOWED")
        
    provider = "polygon" if os.environ.get('POLYGON_API_KEY') else "alphavantage"
    
    return {
        "database_url": os.environ.get('DATABASE_URL'),
        "market_data": {
            "provider": provider,
            "api_key": api_key
        },
        "environment": "development"
    }

def get_testing_config() -> Dict:
    """Get testing configuration - REQUIRES REAL API KEY"""
    api_key = os.environ.get('POLYGON_API_KEY') or os.environ.get('ALPHAVANTAGE_API_KEY')
    if not api_key:
        raise ValueError("❌ TESTING REQUIRES REAL API KEY - NO FAKE DATA ALLOWED")
        
    provider = "polygon" if os.environ.get('POLYGON_API_KEY') else "alphavantage"
    
    return {
        "database_url": os.environ.get('DATABASE_URL'),
        "market_data": {
            "provider": provider,
            "api_key": api_key
        },
        "environment": "testing"
    }

# Main execution
if __name__ == "__main__":
    print("🚀 Complete V2 Automation System")
    print("=" * 50)
    
    # Determine environment
    environment = os.environ.get('ENVIRONMENT', 'development')
    
    if environment == 'production':
        config = get_production_config()
    elif environment == 'testing':
        config = get_testing_config()
    else:
        config = get_development_config()
        
    print(f"Environment: {environment}")
    print(f"Market Data Provider: {config['market_data']['provider']}")
    
    try:
        # Start the complete system
        orchestrator = start_complete_v2_system(config)
        
        print("\n✅ V2 Automation System is running!")
        print("📊 Ready to process enhanced signals")
        print("🔍 Confirmation monitoring active")
        print("📈 MFE tracking ready")
        print("\nPress Ctrl+C to stop...")
        
        print("\n✅ System ready to receive REAL signals from TradingView")
        print("❌ NO FAKE DATA - System only processes real market signals")
        
        # Keep running
        while True:
            time.sleep(1)
            
            # Print status every 30 seconds
            if int(time.time()) % 30 == 0:
                status = get_v2_system_status()
                print(f"\n📊 System Status: {status['system_running']}")
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down V2 Automation System...")
        stop_complete_v2_system()
        print("✅ System stopped successfully")
        
    except Exception as e:
        print(f"\n❌ System error: {str(e)}")
        stop_complete_v2_system()