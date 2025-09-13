"""
Signal Context Analyzer - Analyze signal performance based on market context
Identifies which market conditions produce the best trading signals
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import statistics
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class ContextPerformance:
    """Performance metrics for specific market context"""
    condition: str
    total_signals: int
    avg_mfe: float
    win_rate: float
    best_session: str
    avg_quality_score: float
    recommendations: List[str]

class SignalContextAnalyzer:
    """Analyze signal performance based on market context"""
    
    def __init__(self, db):
        self.db = db
    
    def analyze_vix_performance(self, days_back: int = 30) -> Dict[str, ContextPerformance]:
        """Analyze signal performance across different VIX regimes"""
        try:
            cursor = self.db.conn.cursor()
            
            # Get signals with market context from last N days
            cursor.execute("""
                SELECT s.bias, s.session, s.market_context, s.context_quality_score,
                       COALESCE(st.mfe_none, st.mfe, 0) as mfe
                FROM live_signals s
                LEFT JOIN signal_lab_trades st ON (
                    s.symbol = 'NQ1!' AND 
                    DATE(s.timestamp AT TIME ZONE 'America/New_York') = st.date AND
                    ABS(EXTRACT(EPOCH FROM (s.timestamp AT TIME ZONE 'America/New_York')::time - st.time::time)) < 300
                )
                WHERE s.timestamp > NOW() - INTERVAL '%s days'
                AND s.market_context IS NOT NULL
                AND s.symbol = 'NQ1!'
                ORDER BY s.timestamp DESC
            """, (days_back,))
            
            signals = cursor.fetchall()
            
            if not signals:
                return {}
            
            # Group by VIX regime
            vix_groups = {
                'LOW_VIX': [],      # VIX < 15
                'NORMAL_VIX': [],   # VIX 15-25
                'HIGH_VIX': [],     # VIX 25-35
                'EXTREME_VIX': []   # VIX > 35
            }
            
            for signal in signals:
                try:
                    market_ctx = json.loads(signal['market_context']) if signal['market_context'] else {}
                    vix = market_ctx.get('vix', 20)
                    
                    if vix < 15:
                        group = 'LOW_VIX'
                    elif vix < 25:
                        group = 'NORMAL_VIX'
                    elif vix < 35:
                        group = 'HIGH_VIX'
                    else:
                        group = 'EXTREME_VIX'
                    
                    vix_groups[group].append({
                        'mfe': float(signal['mfe']) if signal['mfe'] else 0,
                        'session': signal['session'],
                        'quality': float(signal['context_quality_score']) if signal['context_quality_score'] else 0.5,
                        'vix': vix
                    })
                    
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    continue
            
            # Calculate performance for each VIX regime
            results = {}
            for regime, signals_data in vix_groups.items():
                if len(signals_data) >= 3:  # Minimum sample size
                    results[regime] = self._calculate_context_performance(
                        regime, signals_data, f"VIX {regime.replace('_', ' ').lower()}"
                    )
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing VIX performance: {str(e)}")
            return {}
    
    def analyze_session_performance(self, days_back: int = 30) -> Dict[str, ContextPerformance]:
        """Analyze signal performance across different trading sessions"""
        try:
            cursor = self.db.conn.cursor()
            
            cursor.execute("""
                SELECT s.bias, s.session, s.market_context, s.context_quality_score,
                       COALESCE(st.mfe_none, st.mfe, 0) as mfe
                FROM live_signals s
                LEFT JOIN signal_lab_trades st ON (
                    s.symbol = 'NQ1!' AND 
                    DATE(s.timestamp AT TIME ZONE 'America/New_York') = st.date AND
                    ABS(EXTRACT(EPOCH FROM (s.timestamp AT TIME ZONE 'America/New_York')::time - st.time::time)) < 300
                )
                WHERE s.timestamp > NOW() - INTERVAL '%s days'
                AND s.symbol = 'NQ1!'
                ORDER BY s.timestamp DESC
            """, (days_back,))
            
            signals = cursor.fetchall()
            
            if not signals:
                return {}
            
            # Group by session
            session_groups = defaultdict(list)
            
            for signal in signals:
                session = signal['session'] or 'Unknown'
                market_ctx = json.loads(signal['market_context']) if signal['market_context'] else {}
                
                session_groups[session].append({
                    'mfe': float(signal['mfe']) if signal['mfe'] else 0,
                    'session': session,
                    'quality': float(signal['context_quality_score']) if signal['context_quality_score'] else 0.5,
                    'vix': market_ctx.get('vix', 20),
                    'volume': market_ctx.get('spy_volume', 50000000)
                })
            
            # Calculate performance for each session
            results = {}
            for session, signals_data in session_groups.items():
                if len(signals_data) >= 3:
                    results[session] = self._calculate_context_performance(
                        session, signals_data, f"{session} session"
                    )
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing session performance: {str(e)}")
            return {}
    
    def analyze_volume_performance(self, days_back: int = 30) -> Dict[str, ContextPerformance]:
        """Analyze signal performance across different volume conditions"""
        try:
            cursor = self.db.conn.cursor()
            
            cursor.execute("""
                SELECT s.bias, s.session, s.market_context, s.context_quality_score,
                       COALESCE(st.mfe_none, st.mfe, 0) as mfe
                FROM live_signals s
                LEFT JOIN signal_lab_trades st ON (
                    s.symbol = 'NQ1!' AND 
                    DATE(s.timestamp AT TIME ZONE 'America/New_York') = st.date AND
                    ABS(EXTRACT(EPOCH FROM (s.timestamp AT TIME ZONE 'America/New_York')::time - st.time::time)) < 300
                )
                WHERE s.timestamp > NOW() - INTERVAL '%s days'
                AND s.market_context IS NOT NULL
                AND s.symbol = 'NQ1!'
                ORDER BY s.timestamp DESC
            """, (days_back,))
            
            signals = cursor.fetchall()
            
            if not signals:
                return {}
            
            # Calculate average volume for comparison
            volumes = []
            for signal in signals:
                try:
                    market_ctx = json.loads(signal['market_context'])
                    volume = market_ctx.get('spy_volume', 0)
                    if volume > 0:
                        volumes.append(volume)
                except:
                    continue
            
            if not volumes:
                return {}
            
            avg_volume = statistics.mean(volumes)
            
            # Group by volume regime
            volume_groups = {
                'LOW_VOLUME': [],     # < 80% of average
                'NORMAL_VOLUME': [],  # 80-120% of average
                'HIGH_VOLUME': []     # > 120% of average
            }
            
            for signal in signals:
                try:
                    market_ctx = json.loads(signal['market_context'])
                    volume = market_ctx.get('spy_volume', avg_volume)
                    
                    if volume < avg_volume * 0.8:
                        group = 'LOW_VOLUME'
                    elif volume < avg_volume * 1.2:
                        group = 'NORMAL_VOLUME'
                    else:
                        group = 'HIGH_VOLUME'
                    
                    volume_groups[group].append({
                        'mfe': float(signal['mfe']) if signal['mfe'] else 0,
                        'session': signal['session'],
                        'quality': float(signal['context_quality_score']) if signal['context_quality_score'] else 0.5,
                        'volume': volume
                    })
                    
                except:
                    continue
            
            # Calculate performance for each volume regime
            results = {}
            for regime, signals_data in volume_groups.items():
                if len(signals_data) >= 3:
                    results[regime] = self._calculate_context_performance(
                        regime, signals_data, f"{regime.replace('_', ' ').lower()}"
                    )
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing volume performance: {str(e)}")
            return {}
    
    def analyze_dxy_correlation_performance(self, days_back: int = 30) -> Dict[str, ContextPerformance]:
        """Analyze NQ signal performance based on DXY correlation"""
        try:
            cursor = self.db.conn.cursor()
            
            cursor.execute("""
                SELECT s.bias, s.session, s.market_context, s.context_quality_score,
                       COALESCE(st.mfe_none, st.mfe, 0) as mfe
                FROM live_signals s
                LEFT JOIN signal_lab_trades st ON (
                    s.symbol = 'NQ1!' AND 
                    DATE(s.timestamp AT TIME ZONE 'America/New_York') = st.date AND
                    ABS(EXTRACT(EPOCH FROM (s.timestamp AT TIME ZONE 'America/New_York')::time - st.time::time)) < 300
                )
                WHERE s.timestamp > NOW() - INTERVAL '%s days'
                AND s.market_context IS NOT NULL
                AND s.symbol = 'NQ1!'
                ORDER BY s.timestamp DESC
            """, (days_back,))
            
            signals = cursor.fetchall()
            
            if not signals:
                return {}
            
            # Group by DXY correlation
            dxy_groups = {
                'DXY_SUPPORTIVE': [],  # DXY move supports NQ bias
                'DXY_NEUTRAL': [],     # DXY flat or small move
                'DXY_OPPOSING': []     # DXY move opposes NQ bias
            }
            
            for signal in signals:
                try:
                    market_ctx = json.loads(signal['market_context'])
                    dxy_change = market_ctx.get('dxy_change', 0)
                    bias = signal['bias']
                    
                    # Determine DXY relationship to NQ bias
                    if abs(dxy_change) < 0.2:  # Small DXY move
                        group = 'DXY_NEUTRAL'
                    elif (dxy_change < 0 and bias == 'Bullish') or (dxy_change > 0 and bias == 'Bearish'):
                        group = 'DXY_SUPPORTIVE'  # DXY supports NQ bias
                    else:
                        group = 'DXY_OPPOSING'    # DXY opposes NQ bias
                    
                    dxy_groups[group].append({
                        'mfe': float(signal['mfe']) if signal['mfe'] else 0,
                        'session': signal['session'],
                        'quality': float(signal['context_quality_score']) if signal['context_quality_score'] else 0.5,
                        'dxy_change': dxy_change,
                        'bias': bias
                    })
                    
                except:
                    continue
            
            # Calculate performance for each DXY correlation
            results = {}
            for correlation, signals_data in dxy_groups.items():
                if len(signals_data) >= 3:
                    results[correlation] = self._calculate_context_performance(
                        correlation, signals_data, f"{correlation.replace('_', ' ').lower()}"
                    )
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing DXY correlation performance: {str(e)}")
            return {}
    
    def _calculate_context_performance(self, condition: str, signals_data: List[Dict], description: str) -> ContextPerformance:
        """Calculate performance metrics for a specific context condition"""
        
        if not signals_data:
            return ContextPerformance(condition, 0, 0, 0, "Unknown", 0, [])
        
        # Calculate metrics
        total_signals = len(signals_data)
        mfes = [s['mfe'] for s in signals_data]
        avg_mfe = statistics.mean(mfes) if mfes else 0
        
        wins = len([mfe for mfe in mfes if mfe > 0])
        win_rate = (wins / total_signals * 100) if total_signals > 0 else 0
        
        # Find best session
        session_performance = defaultdict(list)
        for signal in signals_data:
            session_performance[signal['session']].append(signal['mfe'])
        
        best_session = "Unknown"
        best_session_avg = -999
        for session, session_mfes in session_performance.items():
            if len(session_mfes) >= 2:  # Minimum sample
                session_avg = statistics.mean(session_mfes)
                if session_avg > best_session_avg:
                    best_session_avg = session_avg
                    best_session = session
        
        # Average quality score
        quality_scores = [s['quality'] for s in signals_data if s['quality'] > 0]
        avg_quality = statistics.mean(quality_scores) if quality_scores else 0.5
        
        # Generate recommendations
        recommendations = self._generate_context_recommendations(
            condition, avg_mfe, win_rate, best_session, avg_quality, signals_data
        )
        
        return ContextPerformance(
            condition=condition,
            total_signals=total_signals,
            avg_mfe=avg_mfe,
            win_rate=win_rate,
            best_session=best_session,
            avg_quality_score=avg_quality,
            recommendations=recommendations
        )
    
    def _generate_context_recommendations(self, condition: str, avg_mfe: float, win_rate: float, 
                                        best_session: str, avg_quality: float, signals_data: List[Dict]) -> List[str]:
        """Generate actionable recommendations based on context performance"""
        
        recommendations = []
        
        # Performance-based recommendations
        if avg_mfe > 1.5:
            recommendations.append(f"EXCELLENT: {condition} shows strong performance ({avg_mfe:.2f}R avg)")
        elif avg_mfe > 0.5:
            recommendations.append(f"GOOD: {condition} shows positive expectancy ({avg_mfe:.2f}R avg)")
        elif avg_mfe > 0:
            recommendations.append(f"MARGINAL: {condition} barely profitable ({avg_mfe:.2f}R avg)")
        else:
            recommendations.append(f"AVOID: {condition} shows negative expectancy ({avg_mfe:.2f}R avg)")
        
        # Win rate recommendations
        if win_rate > 70:
            recommendations.append(f"High win rate ({win_rate:.1f}%) - consider larger position sizes")
        elif win_rate < 40:
            recommendations.append(f"Low win rate ({win_rate:.1f}%) - focus on risk management")
        
        # Session-specific recommendations
        if best_session != "Unknown":
            recommendations.append(f"Best performance during {best_session} session")
        
        # Quality-based recommendations
        if avg_quality > 0.7:
            recommendations.append("High-quality signals - maintain current filtering")
        elif avg_quality < 0.4:
            recommendations.append("Low-quality signals - tighten filtering criteria")
        
        # Context-specific recommendations
        if 'VIX' in condition:
            if 'LOW' in condition:
                recommendations.append("Low VIX: Consider trend-following strategies")
            elif 'HIGH' in condition or 'EXTREME' in condition:
                recommendations.append("High VIX: Focus on mean reversion, smaller sizes")
        
        elif 'VOLUME' in condition:
            if 'LOW' in condition:
                recommendations.append("Low volume: Avoid breakouts, focus on ranges")
            elif 'HIGH' in condition:
                recommendations.append("High volume: Good for momentum trades")
        
        elif 'DXY' in condition:
            if 'SUPPORTIVE' in condition:
                recommendations.append("DXY supportive: Consider extended targets")
            elif 'OPPOSING' in condition:
                recommendations.append("DXY opposing: Use tighter stops and targets")
        
        return recommendations[:4]  # Limit to top 4 recommendations
    
    def get_comprehensive_analysis(self, days_back: int = 30) -> Dict[str, Any]:
        """Get comprehensive market context analysis"""
        try:
            analysis = {
                'analysis_period': f"Last {days_back} days",
                'timestamp': datetime.now().isoformat(),
                'vix_performance': self.analyze_vix_performance(days_back),
                'session_performance': self.analyze_session_performance(days_back),
                'volume_performance': self.analyze_volume_performance(days_back),
                'dxy_correlation_performance': self.analyze_dxy_correlation_performance(days_back)
            }
            
            # Generate overall insights
            analysis['key_insights'] = self._generate_key_insights(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {str(e)}")
            return {'error': str(e)}
    
    def _generate_key_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate key insights from comprehensive analysis"""
        insights = []
        
        try:
            # Find best VIX regime
            vix_performance = analysis.get('vix_performance', {})
            if vix_performance:
                best_vix = max(vix_performance.items(), key=lambda x: x[1].avg_mfe)
                insights.append(f"Best VIX regime: {best_vix[0]} ({best_vix[1].avg_mfe:.2f}R avg)")
            
            # Find best session
            session_performance = analysis.get('session_performance', {})
            if session_performance:
                best_session = max(session_performance.items(), key=lambda x: x[1].avg_mfe)
                insights.append(f"Best session: {best_session[0]} ({best_session[1].avg_mfe:.2f}R avg)")
            
            # Find best volume condition
            volume_performance = analysis.get('volume_performance', {})
            if volume_performance:
                best_volume = max(volume_performance.items(), key=lambda x: x[1].avg_mfe)
                insights.append(f"Best volume condition: {best_volume[0]} ({best_volume[1].avg_mfe:.2f}R avg)")
            
            # DXY correlation insight
            dxy_performance = analysis.get('dxy_correlation_performance', {})
            if dxy_performance:
                best_dxy = max(dxy_performance.items(), key=lambda x: x[1].avg_mfe)
                insights.append(f"Best DXY condition: {best_dxy[0]} ({best_dxy[1].avg_mfe:.2f}R avg)")
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            insights.append("Analysis in progress...")
        
        return insights[:5]  # Top 5 insights