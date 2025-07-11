#!/usr/bin/env python3
"""
Startup script for Institutional Trading System
"""

import os
import sys
import logging
from datetime import datetime
import argparse

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from institutional_trading_system import InstitutionalTradingSystem
from config import TradingConfig

def setup_logging():
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, TradingConfig.LOG_LEVEL),
        format=TradingConfig.LOG_FORMAT,
        handlers=[
            logging.FileHandler(TradingConfig.LOG_FILE_PATH),
            logging.StreamHandler(sys.stdout)
        ]
    )

def create_directories():
    """Create necessary directories"""
    directories = [
        TradingConfig.MODEL_SAVE_PATH,
        TradingConfig.DATA_SAVE_PATH,
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def print_banner():
    """Print system banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🏛️  INSTITUTIONAL TRADING SYSTEM v1.0  🏛️             ║
    ║                                                              ║
    ║        📊 ICT Concepts + AI/ML Learning Engine               ║
    ║        🎯 Daily Profit Extraction System                     ║
    ║        🤖 Continuous Learning & Optimization                 ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_system_info():
    """Print system configuration info"""
    print(f"📈 Trading Symbols: {', '.join(TradingConfig.SYMBOLS)}")
    print(f"💰 Daily Profit Target: ${TradingConfig.MAX_DAILY_PROFIT}")
    print(f"🛡️  Daily Loss Limit: ${abs(TradingConfig.MAX_DAILY_LOSS)}")
    print(f"🎯 Risk per Trade: ${TradingConfig.RISK_PER_TRADE}")
    print(f"📊 Min Confidence: {TradingConfig.MIN_CONFIDENCE * 100}%")
    print(f"🌐 API Port: {TradingConfig.API_PORT}")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)

def main():
    """Main startup function"""
    parser = argparse.ArgumentParser(description='Institutional Trading System')
    parser.add_argument('--symbols', nargs='+', help='Trading symbols', default=TradingConfig.SYMBOLS)
    parser.add_argument('--paper-trading', action='store_true', help='Enable paper trading mode')
    parser.add_argument('--no-ai', action='store_true', help='Disable AI learning')
    parser.add_argument('--config-file', help='Path to configuration file')
    
    args = parser.parse_args()
    
    # Load configuration from environment
    TradingConfig.from_env()
    
    # Override symbols if provided
    if args.symbols:
        TradingConfig.SYMBOLS = args.symbols
    
    # Setup system
    print_banner()
    setup_logging()
    create_directories()
    print_system_info()
    
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize trading system
        logger.info("🚀 Initializing Institutional Trading System...")
        
        trading_system = InstitutionalTradingSystem(
            symbols=TradingConfig.SYMBOLS
        )
        
        # Configure paper trading if enabled
        if args.paper_trading:
            logger.info("📝 Paper trading mode enabled")
            trading_system.paper_trading = True
        
        # Disable AI if requested
        if args.no_ai:
            logger.info("🤖 AI learning disabled")
            trading_system.ai_learning_enabled = False
        
        # Start the system
        logger.info("🎯 Starting all system components...")
        trading_system.start_system()
        
        # System status check
        logger.info("✅ System startup complete!")
        logger.info("🌐 Dashboard available at: http://localhost:5001")
        logger.info("📊 API endpoints:")
        logger.info("   - GET /           - System dashboard")
        logger.info("   - GET /signals    - Current signals")
        logger.info("   - GET /trades     - Active and recent trades")
        logger.info("   - GET /performance - Performance statistics")
        logger.info("   - GET /ai_status  - AI learning status")
        
        # Keep system running
        logger.info("🔄 System is now operational. Press Ctrl+C to stop.")
        
        import time
        while True:
            time.sleep(60)
            
            # Hourly status update
            if datetime.now().minute == 0:
                logger.info(f"📊 Hourly Status - Daily P&L: ${trading_system.daily_pnl:.2f} | "
                           f"Active Trades: {len(trading_system.active_trades)} | "
                           f"Win Rate: {trading_system.performance_stats['win_rate']:.1f}%")
                
                # Check if daily targets met
                if trading_system.daily_pnl >= TradingConfig.MAX_DAILY_PROFIT:
                    logger.info("🎉 Daily profit target achieved!")
                elif trading_system.daily_pnl <= TradingConfig.MAX_DAILY_LOSS:
                    logger.warning("⚠️  Daily loss limit reached!")
    
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown signal received...")
        
        # Graceful shutdown
        if 'trading_system' in locals():
            logger.info("💾 Saving system state...")
            trading_system.data_feed_active = False
            
            # Close any open trades (in paper trading mode)
            if hasattr(trading_system, 'paper_trading') and trading_system.paper_trading:
                for symbol, trade in trading_system.active_trades.items():
                    logger.info(f"📝 Closing paper trade: {symbol}")
            
            # Save AI models
            if trading_system.ai_engine.is_trained:
                model_path = os.path.join(TradingConfig.MODEL_SAVE_PATH, 'trading_models.pkl')
                trading_system.ai_engine.save_models(model_path)
                logger.info(f"🤖 AI models saved to {model_path}")
        
        logger.info("✅ System shutdown complete")
        
    except Exception as e:
        logger.error(f"❌ System error: {e}")
        logger.error("🔧 Check logs for detailed error information")
        sys.exit(1)

if __name__ == '__main__':
    main()