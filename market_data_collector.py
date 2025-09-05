"""
Real-time Market Data Collector
Collects multi-asset data for ML feature engineering
"""

import asyncio
import aiohttp
import pandas as pd
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Optional
import logging
import json
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class MarketDataPoint:
    """Single market data point"""
    symbol: str
    price: float
    volume: float
    timestamp: datetime
    bid: Optional[float] = None
    ask: Optional[float] = None
    spread: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)

class MarketDataCollector:
    """
    Real-time market data collector for ML features
    
    Collects data from multiple sources:
    - Futures prices (NQ, ES, YM, RTY)
    - Forex (DXY)
    - Indices (VIX, TNX)
    - Alternative data sources
    """
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self.data_cache = {}
        self.collection_active = False
        
        # Symbols to track
        self.symbols = {
            'futures': ['NQ1!', 'ES1!', 'YM1!', 'RTY1!'],
            'forex': ['DXY'],
            'indices': ['VIX', 'TNX'],
            'crypto': ['BTCUSD', 'ETHUSD']  # For correlation analysis
        }
        
        # Data sources
        self.data_sources = {
            'tradingview': 'https://scanner.tradingview.com/america/scan',
            'yahoo': 'https://query1.finance.yahoo.com/v8/finance/chart/',
            'alpha_vantage': 'https://www.alphavantage.co/query',
            'polygon': 'https://api.polygon.io/v2/aggs/ticker/'
        }
        
        # Rate limiting
        self.last_request_time = {}
        self.min_request_interval = 1.0  # Seconds between requests
        
    async def start_collection(self):
        """Start real-time data collection"""
        
        if self.collection_active:
            return
        
        self.collection_active = True
        logger.info("🚀 Starting market data collection...")
        
        # Start collection tasks
        tasks = [
            self._collect_futures_data(),
            self._collect_forex_data(),
            self._collect_indices_data(),
            self._collect_alternative_data(),
            self._cleanup_old_data()
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stop_collection(self):
        """Stop data collection"""
        self.collection_active = False
        logger.info("⏹️ Market data collection stopped")
    
    async def _collect_futures_data(self):
        """Collect futures data (NQ, ES, YM, RTY)"""
        
        while self.collection_active:
            try:
                for symbol in self.symbols['futures']:
                    data_point = await self._fetch_symbol_data(symbol)
                    if data_point:
                        await self._store_data_point(data_point)
                
                await asyncio.sleep(5)  # 5-second intervals for futures
                
            except Exception as e:
                logger.error(f"❌ Futures data collection error: {str(e)}")
                await asyncio.sleep(10)
    
    async def _collect_forex_data(self):
        """Collect forex data (DXY)"""
        
        while self.collection_active:
            try:
                for symbol in self.symbols['forex']:
                    data_point = await self._fetch_symbol_data(symbol)
                    if data_point:
                        await self._store_data_point(data_point)
                
                await asyncio.sleep(10)  # 10-second intervals for forex
                
            except Exception as e:
                logger.error(f"❌ Forex data collection error: {str(e)}")
                await asyncio.sleep(15)
    
    async def _collect_indices_data(self):
        """Collect indices data (VIX, TNX)"""
        
        while self.collection_active:
            try:
                for symbol in self.symbols['indices']:
                    data_point = await self._fetch_symbol_data(symbol)
                    if data_point:
                        await self._store_data_point(data_point)
                
                await asyncio.sleep(15)  # 15-second intervals for indices
                
            except Exception as e:
                logger.error(f"❌ Indices data collection error: {str(e)}")
                await asyncio.sleep(20)
    
    async def _collect_alternative_data(self):
        """Collect alternative data sources"""
        
        while self.collection_active:
            try:
                # Economic calendar events
                await self._fetch_economic_events()
                
                # Market sentiment indicators
                await self._fetch_sentiment_data()
                
                # Crypto correlations
                for symbol in self.symbols['crypto']:
                    data_point = await self._fetch_symbol_data(symbol)
                    if data_point:
                        await self._store_data_point(data_point)
                
                await asyncio.sleep(60)  # 1-minute intervals for alternative data
                
            except Exception as e:
                logger.error(f"❌ Alternative data collection error: {str(e)}")
                await asyncio.sleep(60)
    
    async def _fetch_symbol_data(self, symbol: str) -> Optional[MarketDataPoint]:
        """Fetch data for a specific symbol"""
        
        try:
            # Rate limiting
            now = datetime.now()
            if symbol in self.last_request_time:
                time_diff = (now - self.last_request_time[symbol]).total_seconds()
                if time_diff < self.min_request_interval:
                    return None
            
            self.last_request_time[symbol] = now
            
            # Try multiple data sources
            data_point = None
            
            # Try Yahoo Finance first (free and reliable)
            data_point = await self._fetch_from_yahoo(symbol)
            
            if not data_point:
                # Try TradingView scanner
                data_point = await self._fetch_from_tradingview(symbol)
            
            return data_point
            
        except Exception as e:
            logger.error(f"❌ Error fetching {symbol}: {str(e)}")
            return None
    
    async def _fetch_from_yahoo(self, symbol: str) -> Optional[MarketDataPoint]:
        """Fetch data from Yahoo Finance"""
        
        try:
            # Convert symbol to Yahoo format
            yahoo_symbol = self._convert_to_yahoo_symbol(symbol)
            
            url = f"{self.data_sources['yahoo']}{yahoo_symbol}"
            params = {
                'interval': '1m',
                'range': '1d',
                'includePrePost': 'true'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_yahoo_response(symbol, data)
            
            return None
            
        except Exception as e:
            logger.debug(f"Yahoo fetch error for {symbol}: {str(e)}")
            return None
    
    async def _fetch_from_tradingview(self, symbol: str) -> Optional[MarketDataPoint]:
        """Fetch data from TradingView scanner"""
        
        try:
            # TradingView scanner request
            payload = {
                "filter": [{"left": "name", "operation": "match", "right": symbol}],
                "columns": ["name", "close", "volume", "bid", "ask"],
                "sort": {"sortBy": "name", "sortOrder": "asc"},
                "range": [0, 1]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.data_sources['tradingview'],
                    json=payload,
                    timeout=5
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_tradingview_response(symbol, data)
            
            return None
            
        except Exception as e:
            logger.debug(f"TradingView fetch error for {symbol}: {str(e)}")
            return None
    

    
    async def _store_data_point(self, data_point: MarketDataPoint):
        """Store data point in database and cache"""
        
        try:
            # Store in cache
            if data_point.symbol not in self.data_cache:
                self.data_cache[data_point.symbol] = []
            
            self.data_cache[data_point.symbol].append(data_point)
            
            # Keep only last 1000 points per symbol
            if len(self.data_cache[data_point.symbol]) > 1000:
                self.data_cache[data_point.symbol] = self.data_cache[data_point.symbol][-1000:]
            
            # Store in database if available
            if self.db:
                await self._store_in_database(data_point)
            
        except Exception as e:
            logger.error(f"❌ Error storing data point: {str(e)}")
    
    async def _store_in_database(self, data_point: MarketDataPoint):
        """Store data point in database"""
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO market_data 
                (symbol, price, volume, bid, ask, spread, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                data_point.symbol,
                data_point.price,
                data_point.volume,
                data_point.bid,
                data_point.ask,
                data_point.spread,
                data_point.timestamp
            ))
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"❌ Database storage error: {str(e)}")
            if self.db:
                self.db.rollback()
    
    async def _fetch_economic_events(self):
        """Fetch economic calendar events"""
        
        try:
            # Fetch from ForexFactory or similar
            url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        events = await response.json()
                        await self._process_economic_events(events)
            
        except Exception as e:
            logger.debug(f"Economic events fetch error: {str(e)}")
    
    async def _fetch_sentiment_data(self):
        """Fetch market sentiment indicators"""
        
        try:
            # Fear & Greed Index, Put/Call ratios, etc.
            # This would integrate with sentiment data providers
            
            sentiment_data = {
                'fear_greed_index': 50,  # Placeholder
                'put_call_ratio': 0.8,
                'vix_term_structure': 'normal',
                'timestamp': datetime.now(pytz.UTC)
            }
            
            # Store sentiment data
            if self.db:
                await self._store_sentiment_data(sentiment_data)
            
        except Exception as e:
            logger.debug(f"Sentiment data fetch error: {str(e)}")
    
    async def _cleanup_old_data(self):
        """Clean up old data from cache and database"""
        
        while self.collection_active:
            try:
                # Clean cache (keep last 4 hours)
                cutoff_time = datetime.now(pytz.UTC) - timedelta(hours=4)
                
                for symbol in self.data_cache:
                    self.data_cache[symbol] = [
                        dp for dp in self.data_cache[symbol]
                        if dp.timestamp > cutoff_time
                    ]
                
                # Clean database (keep last 24 hours)
                if self.db:
                    cursor = self.db.cursor()
                    cursor.execute("""
                        DELETE FROM market_data 
                        WHERE timestamp < NOW() - INTERVAL '24 hours'
                    """)
                    self.db.commit()
                
                await asyncio.sleep(3600)  # Clean every hour
                
            except Exception as e:
                logger.error(f"❌ Cleanup error: {str(e)}")
                await asyncio.sleep(3600)
    
    def get_recent_data(self, symbol: str, minutes: int = 60) -> List[Dict]:
        """Get recent data for a symbol"""
        
        if symbol not in self.data_cache:
            return []
        
        cutoff_time = datetime.now(pytz.UTC) - timedelta(minutes=minutes)
        
        recent_data = [
            dp.to_dict() for dp in self.data_cache[symbol]
            if dp.timestamp > cutoff_time
        ]
        
        return sorted(recent_data, key=lambda x: x['timestamp'])
    
    def get_all_recent_data(self, minutes: int = 60) -> Dict[str, List[Dict]]:
        """Get recent data for all symbols"""
        
        result = {}
        for symbol in self.symbols['futures'] + self.symbols['forex'] + self.symbols['indices']:
            result[symbol] = self.get_recent_data(symbol, minutes)
        
        return result
    
    def calculate_correlations(self, lookback_minutes: int = 60) -> Dict[str, float]:
        """Calculate real-time correlations between symbols"""
        
        try:
            # Get recent data for correlation calculation
            nq_data = self.get_recent_data('NQ1!', lookback_minutes)
            es_data = self.get_recent_data('ES1!', lookback_minutes)
            ym_data = self.get_recent_data('YM1!', lookback_minutes)
            dxy_data = self.get_recent_data('DXY', lookback_minutes)
            
            if len(nq_data) < 10:  # Need minimum data
                return self._default_correlations()
            
            # Convert to pandas for correlation calculation
            nq_prices = [dp['price'] for dp in nq_data]
            es_prices = [dp['price'] for dp in es_data] if len(es_data) == len(nq_data) else nq_prices
            ym_prices = [dp['price'] for dp in ym_data] if len(ym_data) == len(nq_data) else nq_prices
            dxy_prices = [dp['price'] for dp in dxy_data] if len(dxy_data) == len(nq_data) else [103] * len(nq_data)
            
            # Calculate correlations
            df = pd.DataFrame({
                'NQ': nq_prices,
                'ES': es_prices,
                'YM': ym_prices,
                'DXY': dxy_prices
            })
            
            corr_matrix = df.corr()
            
            return {
                'nq_es_corr': corr_matrix.loc['NQ', 'ES'],
                'nq_ym_corr': corr_matrix.loc['NQ', 'YM'],
                'nq_dxy_corr': corr_matrix.loc['NQ', 'DXY'],
                'es_ym_corr': corr_matrix.loc['ES', 'YM'],
                'correlation_strength': abs(corr_matrix.loc['NQ', 'ES']),
                'timestamp': datetime.now(pytz.UTC).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Correlation calculation error: {str(e)}")
            return self._default_correlations()
    
    # Helper methods
    def _convert_to_yahoo_symbol(self, symbol: str) -> str:
        """Convert symbol to Yahoo Finance format"""
        
        conversions = {
            'NQ1!': 'NQ=F',
            'ES1!': 'ES=F',
            'YM1!': 'YM=F',
            'RTY1!': 'RTY=F',
            'DXY': 'DX=F',
            'VIX': '^VIX',
            'TNX': '^TNX',
            'BTCUSD': 'BTC-USD',
            'ETHUSD': 'ETH-USD'
        }
        
        return conversions.get(symbol, symbol)
    
    def _parse_yahoo_response(self, symbol: str, data: Dict) -> Optional[MarketDataPoint]:
        """Parse Yahoo Finance response"""
        
        try:
            result = data['chart']['result'][0]
            meta = result['meta']
            
            # Get latest price
            price = meta.get('regularMarketPrice', meta.get('previousClose', 0))
            
            # Get volume if available
            volume = 0
            if 'volume' in result['indicators']:
                volumes = result['indicators']['volume'][0]['volume']
                volume = volumes[-1] if volumes and volumes[-1] else 0
            
            return MarketDataPoint(
                symbol=symbol,
                price=float(price),
                volume=float(volume) if volume else 0,
                timestamp=datetime.now(pytz.UTC)
            )
            
        except Exception as e:
            logger.debug(f"Yahoo parse error for {symbol}: {str(e)}")
            return None
    
    def _parse_tradingview_response(self, symbol: str, data: Dict) -> Optional[MarketDataPoint]:
        """Parse TradingView response"""
        
        try:
            if 'data' in data and len(data['data']) > 0:
                row = data['data'][0]
                
                return MarketDataPoint(
                    symbol=symbol,
                    price=float(row['d'][1]),  # close price
                    volume=float(row['d'][2]) if len(row['d']) > 2 else 0,
                    timestamp=datetime.now(pytz.UTC),
                    bid=float(row['d'][3]) if len(row['d']) > 3 else None,
                    ask=float(row['d'][4]) if len(row['d']) > 4 else None
                )
            
            return None
            
        except Exception as e:
            logger.debug(f"TradingView parse error for {symbol}: {str(e)}")
            return None
    
    def _default_correlations(self) -> Dict[str, float]:
        """Return empty correlations when no real data available"""
        
        return {
            'timestamp': datetime.now(pytz.UTC).isoformat()
        }
    
    async def _process_economic_events(self, events: List[Dict]):
        """Process economic calendar events"""
        
        # Filter high-impact events
        high_impact_events = [
            event for event in events
            if event.get('impact') in ['High', 'RED', 'high']
        ]
        
        # Store in database or cache for ML features
        logger.info(f"📅 Processed {len(high_impact_events)} high-impact economic events")
    
    async def _store_sentiment_data(self, sentiment_data: Dict):
        """Store sentiment data in database"""
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO sentiment_data 
                (fear_greed_index, put_call_ratio, vix_term_structure, timestamp)
                VALUES (%s, %s, %s, %s)
            """, (
                sentiment_data['fear_greed_index'],
                sentiment_data['put_call_ratio'],
                sentiment_data['vix_term_structure'],
                sentiment_data['timestamp']
            ))
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"❌ Sentiment data storage error: {str(e)}")

# Global collector instance
market_collector = None

def get_market_collector(db_connection=None):
    """Get or create market data collector"""
    global market_collector
    if market_collector is None:
        market_collector = MarketDataCollector(db_connection)
    return market_collector

async def start_market_data_collection(db_connection=None):
    """Start market data collection"""
    collector = get_market_collector(db_connection)
    await collector.start_collection()

def get_market_data_for_ml(symbol: str = 'NQ1!', minutes: int = 60) -> List[Dict]:
    """Get market data for ML analysis"""
    collector = get_market_collector()
    return collector.get_recent_data(symbol, minutes)