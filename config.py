#!/usr/bin/env python3
"""
Configuration settings for Institutional Trading System
"""

import os
from datetime import time

class TradingConfig:
    # Trading Parameters
    SYMBOLS = ['ES=F', 'NQ=F']  # E-mini S&P 500 and Nasdaq futures
    
    # Risk Management
    MAX_DAILY_LOSS = -500.0
    MAX_DAILY_PROFIT = 1000.0
    MAX_POSITION_SIZE = 1000.0
    MAX_CONCURRENT_TRADES = 3
    RISK_PER_TRADE = 100.0  # Risk $100 per trade
    
    # Signal Filtering
    MIN_CONFIDENCE = 0.65
    MIN_RISK_REWARD = 1.5
    MAX_TRADES_PER_DAY = 10
    
    # Market Hours (EST)
    MARKET_OPEN = time(9, 30)
    MARKET_CLOSE = time(16, 0)
    
    # ICT Settings
    ICT_SESSIONS = {
        'london_open_kz': {'start': 2, 'end': 4},    # 2-4 AM UTC
        'ny_open_kz': {'start': 12, 'end': 14},      # 7-9 AM EST
        'london_close': {'start': 15, 'end': 17},    # 10 AM-12 PM EST
        'am_session': {'start': 14.5, 'end': 16.5},  # 9:30-11:30 AM EST
        'pm_session': {'start': 18.5, 'end': 21}     # 1:30-4 PM EST
    }
    
    # Macro Windows (minutes from midnight EST)
    MACRO_WINDOWS = [
        {'name': 'Opening_Range', 'start': 590, 'end': 610},      # 9:50-10:10 AM
        {'name': 'Pre_Lunch', 'start': 650, 'end': 670},         # 10:50-11:10 AM
        {'name': 'Lunch_Entry', 'start': 710, 'end': 730},       # 11:50 AM-12:10 PM
        {'name': 'Lunch_Exit', 'start': 770, 'end': 790},        # 12:50-1:10 PM
        {'name': 'PM_Start', 'start': 830, 'end': 850},          # 1:50-2:10 PM
        {'name': 'PM_Mid', 'start': 890, 'end': 910},            # 2:50-3:10 PM
        {'name': 'Final_Hour', 'start': 915, 'end': 945},        # 3:15-3:45 PM
        {'name': 'MOC', 'start': 945, 'end': 960}                # 3:45-4:00 PM
    ]
    
    # AI/ML Settings
    AI_RETRAIN_INTERVAL = 3600  # Retrain every hour
    MIN_SAMPLES_FOR_TRAINING = 50
    FEATURE_IMPORTANCE_THRESHOLD = 0.01
    
    # Data Settings
    DATA_UPDATE_INTERVAL = 60  # Update every minute
    HISTORICAL_BARS = 1000
    
    # API Settings
    API_PORT = 5001
    API_HOST = '0.0.0.0'
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # File Paths
    MODEL_SAVE_PATH = 'models/'
    DATA_SAVE_PATH = 'data/'
    LOG_FILE_PATH = 'logs/trading_system.log'
    
    # Environment Variables
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        try:
            cls.MAX_DAILY_LOSS = cls._get_float_env('MAX_DAILY_LOSS', cls.MAX_DAILY_LOSS)
            cls.MAX_DAILY_PROFIT = cls._get_float_env('MAX_DAILY_PROFIT', cls.MAX_DAILY_PROFIT)
            cls.RISK_PER_TRADE = cls._get_float_env('RISK_PER_TRADE', cls.RISK_PER_TRADE)
            cls.MIN_CONFIDENCE = cls._get_float_env('MIN_CONFIDENCE', cls.MIN_CONFIDENCE)
            cls.API_PORT = cls._get_int_env('PORT', cls.API_PORT)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid environment variable configuration: {e}")
        
        # Symbols from environment (comma-separated)
        symbols_env = os.getenv('TRADING_SYMBOLS')
        if symbols_env:
            cls.SYMBOLS = [s.strip() for s in symbols_env.split(',')]
        
        return cls
    
    @staticmethod
    def _get_float_env(key: str, default: float) -> float:
        """Safely get float environment variable"""
        try:
            return float(os.getenv(key, str(default)))
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def _get_int_env(key: str, default: int) -> int:
        """Safely get integer environment variable"""
        try:
            return int(os.getenv(key, str(default)))
        except (ValueError, TypeError):
            return default

# Gap Analysis Rules (NQ-specific)
class GapAnalysisConfig:
    # NQ Gap Rules
    SMALL_GAP_RANGE = (20, 75)      # Usually trades to overnight high/low then 50% retrace
    MEDIUM_GAP_RANGE = (75, 120)    # Sweet spot, wait for 10 AM direction
    LARGE_GAP_THRESHOLD = 120       # May leave unfilled or use 25% level
    
    # Gap Fill Probabilities
    SMALL_GAP_FILL_PROB = 0.85
    MEDIUM_GAP_FILL_PROB = 0.65
    LARGE_GAP_FILL_PROB = 0.35
    
    # Retracement Levels
    RETRACEMENT_LEVELS = [0.25, 0.50, 0.75]

# Pattern Recognition Settings
class PatternConfig:
    # Fair Value Gap Settings
    FVG_MIN_SIZE = 0.001  # Minimum gap size as percentage of price
    FVG_MAX_AGE_HOURS = 24  # Maximum age before FVG expires
    
    # Liquidity Levels
    LIQUIDITY_TOUCH_TOLERANCE = 0.0005  # 0.05% tolerance for level touches
    MIN_LIQUIDITY_STRENGTH = 3  # Minimum touches to consider strong level
    
    # Order Blocks
    ORDER_BLOCK_MIN_SIZE = 0.002  # Minimum size as percentage
    ORDER_BLOCK_MAX_AGE_HOURS = 48
    
    # Imbalances
    IMBALANCE_MIN_SIZE = 0.001
    IMBALANCE_FILL_THRESHOLD = 0.5  # 50% fill to consider partially filled

# Performance Targets
class PerformanceTargets:
    TARGET_WIN_RATE = 65.0  # Target 65% win rate
    TARGET_PROFIT_FACTOR = 2.0  # Target 2:1 profit factor
    TARGET_SHARPE_RATIO = 1.5  # Target Sharpe ratio
    TARGET_MAX_DRAWDOWN = 0.05  # Target max 5% drawdown
    
    # Daily Targets
    DAILY_PROFIT_TARGET = 500.0
    DAILY_TRADE_TARGET = 5  # Target 5 trades per day
    
    # Weekly Targets
    WEEKLY_PROFIT_TARGET = 2500.0
    WEEKLY_WIN_RATE_TARGET = 60.0

# Notification Settings
class NotificationConfig:
    ENABLE_TRADE_ALERTS = True
    ENABLE_PERFORMANCE_ALERTS = True
    ENABLE_ERROR_ALERTS = True
    
    # Alert Thresholds
    LARGE_LOSS_THRESHOLD = -200.0
    LARGE_PROFIT_THRESHOLD = 300.0
    LOW_WIN_RATE_THRESHOLD = 40.0
    
    # Webhook URLs (set via environment variables)
    DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK_URL')
    SLACK_WEBHOOK = os.getenv('SLACK_WEBHOOK_URL')
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')