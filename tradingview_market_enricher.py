"""
TradingView Market Data Enricher - Real-time data from TradingView
Uses TradingView's actual data feeds for market context
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class TradingViewMarketEnricher:
    """Real-time market data from TradingView"""
    
    def __init__(self):
        self.base_url = "https://scanner.tradingview.com"
        self.cache = {}
        self.cache_duration = 30  # 30 seconds cache
        
    def get_market_context(self) -> Dict[str, Any]:
        """Get real-time market context from TradingView"""
        try:
            # Try multiple approaches to get real data
            market_data = None
            
            # Approach 1: TradingView scanner API
            symbols = ["CBOE:VIX", "AMEX:SPY", "NASDAQ:QQQ", "CME_MINI:NQ1!", "CME_MINI:ES1!", "CME_MINI:YM1!", "TVC:DXY"]
            market_data = self._get_tradingview_data(symbols)
            
            # Approach 2: Try alternative API if first fails
            if not market_data:
                logger.warning("Primary TradingView API failed, trying alternative...")
                market_data = self._get_alternative_data(symbols)
            
            # Approach 3: Try simplified request
            if not market_data:
                logger.warning("Alternative API failed, trying simplified request...")
                essential_symbols = ["CBOE:VIX", "CME_MINI:NQ1!", "TVC:DXY"]
                market_data = self._get_tradingview_data(essential_symbols)
            
            # If we still don't have data, return fallback
            if not market_data:
                logger.error("All TradingView data sources failed")
                return self._get_fallback_context()
            
            # Validate we have essential data
            has_essential_data = (
                "CBOE:VIX" in market_data or 
                "CME_MINI:NQ1!" in market_data or 
                "TVC:DXY" in market_data
            )
            
            if not has_essential_data:
                logger.error("No essential market data received")
                return self._get_fallback_context()
            
            # Extract key metrics with better defaults
            vix = market_data.get("CBOE:VIX", {}).get("close")
            spy_volume = market_data.get("AMEX:SPY", {}).get("volume")
            qqq_volume = market_data.get("NASDAQ:QQQ", {}).get("volume")
            
            nq_price = market_data.get("CME_MINI:NQ1!", {}).get("close")
            es_price = market_data.get("CME_MINI:ES1!", {}).get("close")
            ym_price = market_data.get("CME_MINI:YM1!", {}).get("close")
            dxy_price = market_data.get("TVC:DXY", {}).get("close")
            
            # Calculate changes
            nq_change = market_data.get("CME_MINI:NQ1!", {}).get("change_abs", 0)
            dxy_change = market_data.get("TVC:DXY", {}).get("change_abs", 0)
            
            # Only use real data - if key metrics are None, return fallback
            if vix is None and nq_price is None and dxy_price is None:
                logger.error("No valid price data received from TradingView")
                return self._get_fallback_context()
            
            # Use real data where available, reasonable defaults where not
            context = {
                'vix': vix if vix is not None else 20.0,
                'spy_volume': spy_volume if spy_volume is not None else 50000000,
                'qqq_volume': qqq_volume if qqq_volume is not None else 30000000,
                'nq_price': nq_price if nq_price is not None else 15000,
                'es_price': es_price if es_price is not None else 4500,
                'ym_price': ym_price if ym_price is not None else 35000,
                'dxy_price': dxy_price if dxy_price is not None else 103.5,
                'dxy_change': dxy_change,
                'nq_change': nq_change,
                'correlation_nq_es': 0.85,  # Would calculate from price movements
                'volatility_regime': self._get_volatility_regime(vix if vix is not None else 20.0),
                'market_session': self._get_current_session(),
                'trend_strength': abs(nq_change / nq_price) * 1000 if nq_price and nq_price > 0 else 0,
                'sector_rotation': self._get_sector_rotation(
                    spy_volume if spy_volume is not None else 50000000,
                    qqq_volume if qqq_volume is not None else 30000000
                ),
                'timestamp': datetime.now().isoformat(),
                'data_source': 'TradingView' if any(v is not None for v in [vix, nq_price, dxy_price]) else 'Fallback'
            }
            
            # Log what real data we got
            real_data_points = [k for k, v in {
                'VIX': vix, 'NQ': nq_price, 'DXY': dxy_price, 
                'SPY_VOL': spy_volume, 'QQQ_VOL': qqq_volume
            }.items() if v is not None]
            
            logger.info(f"TradingView data retrieved: {', '.join(real_data_points)} ({len(real_data_points)}/5 metrics)")
            
            return context
            
        except Exception as e:
            logger.error(f"TradingView data error: {str(e)}")
            return self._get_fallback_context()
    
    def _get_tradingview_data(self, symbols: list) -> Dict[str, Dict]:
        """Get real-time data from TradingView scanner API"""
        try:
            # TradingView scanner request
            payload = {
                "filter": [{"left": "name", "operation": "in_range", "right": symbols}],
                "options": {"lang": "en"},
                "symbols": {"query": {"types": []}, "tickers": symbols},
                "columns": ["name", "close", "change", "change_abs", "volume", "high", "low"],
                "sort": {"sortBy": "name", "sortOrder": "asc"},
                "range": [0, len(symbols)]
            }
            
            response = requests.post(
                f"{self.base_url}/america/scan",
                json=payload,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Content-Type': 'application/json'
                },
                timeout=15  # Increased timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse response
                result = {}
                if 'data' in data:
                    for item in data['data']:
                        if 'd' in item and len(item['d']) >= 7:
                            symbol = item['d'][0]
                            # Validate data is not null/zero
                            close_price = item['d'][1]
                            if close_price is not None and close_price > 0:
                                result[symbol] = {
                                    'close': close_price,
                                    'change': item['d'][2],
                                    'change_abs': item['d'][3],
                                    'volume': item['d'][4],
                                    'high': item['d'][5],
                                    'low': item['d'][6]
                                }
                
                logger.info(f"TradingView primary API: {len(result)} valid symbols retrieved")
                return result
            else:
                logger.error(f"TradingView API error: {response.status_code} - {response.text[:200]}")
                return {}
                
        except Exception as e:
            logger.error(f"TradingView request error: {str(e)}")
            return {}
    
    def _get_alternative_data(self, symbols: list) -> Dict[str, Dict]:
        """Alternative data source when primary TradingView API fails"""
        try:
            # Try different TradingView endpoint
            result = {}
            
            # Try individual symbol requests for critical data
            critical_symbols = ["CBOE:VIX", "CME_MINI:NQ1!", "TVC:DXY"]
            
            for symbol in critical_symbols:
                if symbol in symbols:
                    try:
                        # Simplified request for individual symbol
                        payload = {
                            "filter": [{"left": "name", "operation": "equal", "right": symbol}],
                            "columns": ["name", "close", "change_abs", "volume"],
                            "range": [0, 1]
                        }
                        
                        response = requests.post(
                            f"{self.base_url}/america/scan",
                            json=payload,
                            headers={'User-Agent': 'Mozilla/5.0'},
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            if 'data' in data and data['data']:
                                item = data['data'][0]
                                if 'd' in item and len(item['d']) >= 4:
                                    close_price = item['d'][1]
                                    if close_price is not None and close_price > 0:
                                        result[symbol] = {
                                            'close': close_price,
                                            'change_abs': item['d'][2],
                                            'volume': item['d'][3]
                                        }
                                        logger.info(f"Alternative API got {symbol}: {close_price}")
                    except Exception as e:
                        logger.error(f"Alternative request failed for {symbol}: {str(e)}")
                        continue
            
            return result
            
        except Exception as e:
            logger.error(f"Alternative data source error: {str(e)}")
            return {}
    
    def _get_volatility_regime(self, vix: float) -> str:
        """Classify volatility regime based on VIX"""
        if vix < 15:
            return "LOW"
        elif vix < 25:
            return "NORMAL"
        elif vix < 35:
            return "HIGH"
        else:
            return "EXTREME"
    
    def _get_current_session(self) -> str:
        """Determine current trading session"""
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
    
    def _get_sector_rotation(self, spy_volume: int, qqq_volume: int) -> str:
        """Determine sector rotation based on volume"""
        if qqq_volume > spy_volume * 0.8:  # QQQ volume high relative to SPY
            return "TECH_LEADERSHIP"
        elif spy_volume > qqq_volume * 1.5:  # SPY volume much higher
            return "VALUE_ROTATION"
        else:
            return "BALANCED"
    
    def _get_fallback_context(self) -> Dict[str, Any]:
        """Fallback context when TradingView is unavailable"""
        return {
            'vix': 20.0,
            'spy_volume': 50000000,
            'qqq_volume': 30000000,
            'nq_price': 15000,
            'es_price': 4500,
            'ym_price': 35000,
            'dxy_price': 103.5,
            'dxy_change': 0.0,
            'nq_change': 0.0,
            'correlation_nq_es': 0.85,
            'volatility_regime': "NORMAL",
            'market_session': self._get_current_session(),
            'trend_strength': 0.5,
            'sector_rotation': "BALANCED",
            'timestamp': datetime.now().isoformat(),
            'data_source': 'Fallback'
        }
    
    def enrich_signal_with_context(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich signal with TradingView market context"""
        try:
            context = self.get_market_context()
            
            # Add market context to signal
            enriched_signal = signal_data.copy()
            enriched_signal['market_context'] = context
            
            # Calculate signal quality based on TradingView data
            quality_score = self._calculate_signal_quality(signal_data, context)
            enriched_signal['context_quality_score'] = quality_score
            
            # Generate recommendations
            recommendations = self._generate_recommendations(signal_data, context)
            enriched_signal['context_recommendations'] = recommendations
            
            logger.info(f"Signal enriched with TradingView data: VIX={context['vix']:.1f}, Session={context['market_session']}, Quality={quality_score:.2f}")
            
            return enriched_signal
            
        except Exception as e:
            logger.error(f"Error enriching with TradingView data: {str(e)}")
            return signal_data
    
    def _calculate_signal_quality(self, signal_data: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate signal quality based on TradingView market context"""
        base_score = 0.5
        
        # VIX factor
        vix = context.get('vix', 20)
        if vix < 15:
            base_score += 0.1  # Low VIX = good
        elif vix > 30:
            base_score -= 0.2  # High VIX = bad
        
        # Session factor
        session = context.get('market_session', 'Unknown')
        if session in ['London', 'NY Regular']:
            base_score += 0.2
        elif session == 'NY Pre Market':
            base_score += 0.1
        else:
            base_score -= 0.1
        
        # Volume factor
        spy_volume = context.get('spy_volume', 50000000)
        if spy_volume > 80000000:  # High volume
            base_score += 0.1
        elif spy_volume < 40000000:  # Low volume
            base_score -= 0.1
        
        # DXY factor for NQ
        if signal_data.get('symbol') == 'NQ1!':
            dxy_change = context.get('dxy_change', 0)
            bias = signal_data.get('bias', 'Bullish')
            
            if abs(dxy_change) > 0.5:  # Significant DXY move
                if (dxy_change < 0 and bias == 'Bullish') or (dxy_change > 0 and bias == 'Bearish'):
                    base_score += 0.15  # DXY supports signal
                else:
                    base_score -= 0.1   # DXY opposes signal
        
        return max(0.0, min(1.0, base_score))
    
    def _generate_recommendations(self, signal_data: Dict[str, Any], context: Dict[str, Any]) -> list:
        """Generate trading recommendations based on TradingView context"""
        recommendations = []
        
        vix = context.get('vix', 20)
        session = context.get('market_session', 'Unknown')
        spy_volume = context.get('spy_volume', 50000000)
        
        # VIX recommendations
        if vix > 30:
            recommendations.append("HIGH VIX: Consider smaller position sizes")
        elif vix < 15:
            recommendations.append("LOW VIX: Favorable for trend following")
        
        # Session recommendations
        if session == 'London':
            recommendations.append("LONDON SESSION: Optimal liquidity for breakouts")
        elif session == 'Asia':
            recommendations.append("ASIA SESSION: Lower liquidity - use tighter stops")
        
        # Volume recommendations
        if spy_volume < 40000000:
            recommendations.append("LOW VOLUME: Avoid breakout trades")
        elif spy_volume > 100000000:
            recommendations.append("HIGH VOLUME: Strong moves likely")
        
        return recommendations[:3]  # Top 3 recommendations

# Global instance
tradingview_enricher = TradingViewMarketEnricher()