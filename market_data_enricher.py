"""
Real-time market data enrichment for trading signals
Captures VIX, volume, market conditions, and other valuable context data
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
from dataclasses import dataclass
import yfinance as yf
import pandas as pd

logger = logging.getLogger(__name__)

@dataclass
class MarketContext:
    """Market context data structure"""
    vix: float
    spy_volume: int
    qqq_volume: int
    market_session: str
    volatility_regime: str
    trend_strength: float
    correlation_nq_es: float
    correlation_nq_ym: float
    dxy_price: float
    dxy_change: float
    sector_rotation: str
    news_sentiment: str
    economic_events: list
    timestamp: datetime

class MarketDataEnricher:
    """Real-time market data enrichment engine"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 60  # Cache for 60 seconds
        
    def get_market_context(self) -> MarketContext:
        """Get comprehensive market context"""
        try:
            # Check cache first
            cache_key = "market_context"
            now = datetime.now()
            
            if (cache_key in self.cache and 
                now - self.cache[cache_key]['timestamp'] < timedelta(seconds=self.cache_duration)):
                return self.cache[cache_key]['data']
            
            # Fetch fresh data
            context = self._fetch_market_context()
            
            # Cache the result
            self.cache[cache_key] = {
                'data': context,
                'timestamp': now
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting market context: {str(e)}")
            return self._get_fallback_context()
    
    def _fetch_market_context(self) -> MarketContext:
        """Fetch real-time market context data"""
        
        # Get VIX data
        vix_data = self._get_vix_data()
        
        # Get volume data
        volume_data = self._get_volume_data()
        
        # Get correlation data
        correlation_data = self._get_correlation_data()
        
        # Get DXY data
        dxy_data = self._get_dxy_data()
        
        # Determine market session
        market_session = self._get_current_session()
        
        # Calculate volatility regime
        volatility_regime = self._calculate_volatility_regime(vix_data['current'])
        
        # Get trend strength
        trend_strength = self._calculate_trend_strength()
        
        # Get sector rotation
        sector_rotation = self._get_sector_rotation()
        
        # Get news sentiment
        news_sentiment = self._get_news_sentiment()
        
        # Get economic events
        economic_events = self._get_economic_events()
        
        return MarketContext(
            vix=vix_data['current'],
            spy_volume=volume_data['spy_volume'],
            qqq_volume=volume_data['qqq_volume'],
            market_session=market_session,
            volatility_regime=volatility_regime,
            trend_strength=trend_strength,
            correlation_nq_es=correlation_data['nq_es'],
            correlation_nq_ym=correlation_data['nq_ym'],
            dxy_price=dxy_data['price'],
            dxy_change=dxy_data['change'],
            sector_rotation=sector_rotation,
            news_sentiment=news_sentiment,
            economic_events=economic_events,
            timestamp=datetime.now()
        )
    
    def _get_vix_data(self) -> Dict[str, float]:
        """Get VIX data"""
        try:
            vix = yf.Ticker("^VIX")
            hist = vix.history(period="2d", interval="1m")
            
            if not hist.empty:
                current_vix = float(hist['Close'].iloc[-1])
                prev_close = float(hist['Close'].iloc[-2])
                change = current_vix - prev_close
                
                return {
                    'current': current_vix,
                    'change': change,
                    'change_pct': (change / prev_close) * 100 if prev_close != 0 else 0
                }
        except Exception as e:
            logger.error(f"Error fetching VIX data: {str(e)}")
        
        return {'current': 20.0, 'change': 0.0, 'change_pct': 0.0}
    
    def _get_volume_data(self) -> Dict[str, int]:
        """Get volume data for major ETFs"""
        try:
            # Get SPY and QQQ volume
            spy = yf.Ticker("SPY")
            qqq = yf.Ticker("QQQ")
            
            spy_hist = spy.history(period="1d", interval="1m")
            qqq_hist = qqq.history(period="1d", interval="1m")
            
            spy_volume = int(spy_hist['Volume'].sum()) if not spy_hist.empty else 0
            qqq_volume = int(qqq_hist['Volume'].sum()) if not qqq_hist.empty else 0
            
            return {
                'spy_volume': spy_volume,
                'qqq_volume': qqq_volume
            }
        except Exception as e:
            logger.error(f"Error fetching volume data: {str(e)}")
        
        return {'spy_volume': 50000000, 'qqq_volume': 30000000}
    
    def _get_correlation_data(self) -> Dict[str, float]:
        """Calculate correlations between futures"""
        try:
            # Get recent price data for NQ, ES, YM
            symbols = ["NQ=F", "ES=F", "YM=F"]
            data = {}
            
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="5d", interval="1h")
                if not hist.empty:
                    data[symbol] = hist['Close'].pct_change().dropna()
            
            if len(data) >= 2:
                nq_data = data.get("NQ=F")
                es_data = data.get("ES=F")
                ym_data = data.get("YM=F")
                
                correlations = {}
                if nq_data is not None and es_data is not None:
                    correlations['nq_es'] = float(nq_data.corr(es_data))
                else:
                    correlations['nq_es'] = 0.85
                    
                if nq_data is not None and ym_data is not None:
                    correlations['nq_ym'] = float(nq_data.corr(ym_data))
                else:
                    correlations['nq_ym'] = 0.80
                
                return correlations
                
        except Exception as e:
            logger.error(f"Error calculating correlations: {str(e)}")
        
        return {'nq_es': 0.85, 'nq_ym': 0.80}
    
    def _get_dxy_data(self) -> Dict[str, float]:
        """Get DXY (Dollar Index) data"""
        try:
            dxy = yf.Ticker("DX-Y.NYB")
            hist = dxy.history(period="2d", interval="1h")
            
            if not hist.empty:
                current_price = float(hist['Close'].iloc[-1])
                prev_close = float(hist['Close'].iloc[0])
                change = current_price - prev_close
                
                return {
                    'price': current_price,
                    'change': change,
                    'change_pct': (change / prev_close) * 100 if prev_close != 0 else 0
                }
        except Exception as e:
            logger.error(f"Error fetching DXY data: {str(e)}")
        
        return {'price': 103.5, 'change': 0.0, 'change_pct': 0.0}
    
    def _get_current_session(self) -> str:
        """Determine current trading session"""
        from datetime import datetime
        import pytz
        
        ny_tz = pytz.timezone('America/New_York')
        ny_time = datetime.now(ny_tz)
        hour = ny_time.hour
        
        if 18 <= hour <= 23:
            return "Asia"
        elif 0 <= hour <= 5:
            return "London"
        elif 6 <= hour <= 9:
            return "NY Pre Market"
        elif 9 <= hour <= 16:
            return "NY Regular"
        else:
            return "After Hours"
    
    def _calculate_volatility_regime(self, vix_value: float) -> str:
        """Calculate volatility regime based on VIX"""
        if vix_value < 15:
            return "LOW"
        elif vix_value < 25:
            return "NORMAL"
        elif vix_value < 35:
            return "HIGH"
        else:
            return "EXTREME"
    
    def _calculate_trend_strength(self) -> float:
        """Calculate overall market trend strength"""
        try:
            # Use SPY as market proxy
            spy = yf.Ticker("SPY")
            hist = spy.history(period="5d", interval="1h")
            
            if not hist.empty:
                # Calculate 20-period moving average slope
                ma20 = hist['Close'].rolling(20).mean()
                if len(ma20) >= 2:
                    slope = (ma20.iloc[-1] - ma20.iloc[-2]) / ma20.iloc[-2]
                    return abs(float(slope)) * 1000  # Scale for readability
            
        except Exception as e:
            logger.error(f"Error calculating trend strength: {str(e)}")
        
        return 0.5  # Neutral trend strength
    
    def _get_sector_rotation(self) -> str:
        """Determine sector rotation pattern"""
        try:
            # Compare tech (QQQ) vs broad market (SPY) performance
            qqq = yf.Ticker("QQQ")
            spy = yf.Ticker("SPY")
            
            qqq_hist = qqq.history(period="5d", interval="1d")
            spy_hist = spy.history(period="5d", interval="1d")
            
            if not qqq_hist.empty and not spy_hist.empty:
                qqq_return = (qqq_hist['Close'].iloc[-1] / qqq_hist['Close'].iloc[0] - 1) * 100
                spy_return = (spy_hist['Close'].iloc[-1] / spy_hist['Close'].iloc[0] - 1) * 100
                
                if qqq_return > spy_return + 0.5:
                    return "TECH_LEADERSHIP"
                elif spy_return > qqq_return + 0.5:
                    return "VALUE_ROTATION"
                else:
                    return "BALANCED"
            
        except Exception as e:
            logger.error(f"Error determining sector rotation: {str(e)}")
        
        return "BALANCED"
    
    def _get_news_sentiment(self) -> str:
        """Get overall news sentiment"""
        # Simplified sentiment based on VIX and market conditions
        # In production, this would integrate with news APIs
        try:
            vix_data = self._get_vix_data()
            
            if vix_data['current'] > 25:
                return "BEARISH"
            elif vix_data['current'] < 15:
                return "BULLISH"
            else:
                return "NEUTRAL"
                
        except Exception as e:
            logger.error(f"Error getting news sentiment: {str(e)}")
        
        return "NEUTRAL"
    
    def _get_economic_events(self) -> list:
        """Get upcoming economic events"""
        # Simplified - in production would integrate with economic calendar APIs
        return [
            {"time": "10:00", "event": "CPI Data", "impact": "HIGH"},
            {"time": "14:00", "event": "Fed Minutes", "impact": "MEDIUM"}
        ]
    
    def _get_fallback_context(self) -> MarketContext:
        """Get fallback context when data fetching fails"""
        return MarketContext(
            vix=20.0,
            spy_volume=50000000,
            qqq_volume=30000000,
            market_session=self._get_current_session(),
            volatility_regime="NORMAL",
            trend_strength=0.5,
            correlation_nq_es=0.85,
            correlation_nq_ym=0.80,
            dxy_price=103.5,
            dxy_change=0.0,
            sector_rotation="BALANCED",
            news_sentiment="NEUTRAL",
            economic_events=[],
            timestamp=datetime.now()
        )
    
    def enrich_signal_with_context(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich signal with market context"""
        try:
            context = self.get_market_context()
            
            # Add market context to signal
            enriched_signal = signal_data.copy()
            enriched_signal.update({
                'market_context': {
                    'vix': context.vix,
                    'vix_regime': context.volatility_regime,
                    'spy_volume': context.spy_volume,
                    'qqq_volume': context.qqq_volume,
                    'session': context.market_session,
                    'trend_strength': context.trend_strength,
                    'nq_es_correlation': context.correlation_nq_es,
                    'nq_ym_correlation': context.correlation_nq_ym,
                    'dxy_price': context.dxy_price,
                    'dxy_change': context.dxy_change,
                    'sector_rotation': context.sector_rotation,
                    'news_sentiment': context.news_sentiment,
                    'economic_events': context.economic_events
                }
            })
            
            # Calculate signal quality score based on context
            quality_score = self._calculate_signal_quality(signal_data, context)
            enriched_signal['context_quality_score'] = quality_score
            
            # Add context-based recommendations
            recommendations = self._generate_context_recommendations(signal_data, context)
            enriched_signal['context_recommendations'] = recommendations
            
            logger.info(f"Signal enriched with market context: VIX={context.vix:.1f}, Session={context.market_session}, Quality={quality_score:.2f}")
            
            return enriched_signal
            
        except Exception as e:
            logger.error(f"Error enriching signal with context: {str(e)}")
            return signal_data
    
    def _calculate_signal_quality(self, signal_data: Dict[str, Any], context: MarketContext) -> float:
        """Calculate signal quality based on market context"""
        base_score = 0.5
        
        # VIX factor
        if context.volatility_regime == "NORMAL":
            base_score += 0.2
        elif context.volatility_regime == "LOW":
            base_score += 0.1
        elif context.volatility_regime == "HIGH":
            base_score -= 0.1
        else:  # EXTREME
            base_score -= 0.3
        
        # Session factor
        if context.market_session in ["London", "NY Regular"]:
            base_score += 0.2
        elif context.market_session == "NY Pre Market":
            base_score += 0.1
        else:
            base_score -= 0.1
        
        # Volume factor
        avg_spy_volume = 80000000  # Typical SPY volume
        if context.spy_volume > avg_spy_volume * 1.2:
            base_score += 0.1
        elif context.spy_volume < avg_spy_volume * 0.8:
            base_score -= 0.1
        
        # Correlation factor
        if context.correlation_nq_es > 0.8:
            base_score += 0.1
        
        # DXY factor for NQ signals
        if signal_data.get('symbol') == 'NQ1!':
            if abs(context.dxy_change) > 0.5:  # Strong DXY move
                if (context.dxy_change > 0 and signal_data.get('bias') == 'Bearish') or \
                   (context.dxy_change < 0 and signal_data.get('bias') == 'Bullish'):
                    base_score += 0.15  # DXY supports the signal
                else:
                    base_score -= 0.1   # DXY against the signal
        
        return max(0.0, min(1.0, base_score))
    
    def _generate_context_recommendations(self, signal_data: Dict[str, Any], context: MarketContext) -> list:
        """Generate context-based trading recommendations"""
        recommendations = []
        
        # VIX-based recommendations
        if context.volatility_regime == "EXTREME":
            recommendations.append("CAUTION: Extreme volatility - consider smaller position size")
        elif context.volatility_regime == "LOW":
            recommendations.append("LOW VIX: Consider larger position size in trending moves")
        
        # Session-based recommendations
        if context.market_session == "Asia":
            recommendations.append("ASIA SESSION: Lower liquidity - tighter stops recommended")
        elif context.market_session == "London":
            recommendations.append("LONDON SESSION: High liquidity - optimal for breakout trades")
        elif context.market_session == "NY Regular":
            recommendations.append("NY SESSION: Peak volume - good for trend following")
        
        # Volume-based recommendations
        avg_spy_volume = 80000000
        if context.spy_volume < avg_spy_volume * 0.7:
            recommendations.append("LOW VOLUME: Avoid breakout trades, focus on mean reversion")
        elif context.spy_volume > avg_spy_volume * 1.3:
            recommendations.append("HIGH VOLUME: Strong moves likely - trail stops wider")
        
        # DXY-based recommendations for NQ
        if signal_data.get('symbol') == 'NQ1!' and abs(context.dxy_change) > 0.3:
            if context.dxy_change > 0:
                recommendations.append("DXY STRENGTH: Headwind for NQ - consider reduced targets")
            else:
                recommendations.append("DXY WEAKNESS: Tailwind for NQ - consider extended targets")
        
        # Correlation-based recommendations
        if context.correlation_nq_es < 0.7:
            recommendations.append("LOW NQ/ES CORRELATION: Divergence trade opportunity")
        
        return recommendations[:3]  # Limit to top 3 recommendations

# Global instance
market_enricher = MarketDataEnricher()