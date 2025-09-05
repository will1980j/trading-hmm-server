#!/usr/bin/env python3
"""
Comprehensive ML Analysis of ALL Trading Data
Analyzes FVG/IFVG, correlations, sessions, HTF, divergences, signal lab data, and live signals
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    from sklearn.cluster import KMeans
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

logger = logging.getLogger(__name__)

class ComprehensiveMLAnalyzer:
    """
    ML Analyzer for ALL your trading data:
    - Live signals (FVG/IFVG bias, HTF alignment, sessions)
    - Signal lab trades (1M and 15M with MFE, breakeven data)
    - Symbol correlations and divergences
    - Session performance across all timeframes
    - News proximity impact
    - Strength patterns and optimization
    """
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.models = {}
        self.scalers = {}
        
    def analyze_all_trading_data(self) -> Dict:
        """Comprehensive analysis of ALL trading data"""
        
        if not self.db:
            return {"error": "No database connection"}
        
        try:
            # Get all data sources
            live_signals = self._get_live_signals()
            signal_lab_1m = self._get_signal_lab_trades('signal_lab_trades')
            signal_lab_15m = self._get_signal_lab_trades('signal_lab_15m_trades')
            
            analysis = {
                "data_summary": {
                    "live_signals": len(live_signals),
                    "signal_lab_1m": len(signal_lab_1m),
                    "signal_lab_15m": len(signal_lab_15m)
                },
                "live_signals_analysis": self._analyze_live_signals(live_signals),
                "signal_lab_analysis": self._analyze_signal_lab_data(signal_lab_1m, signal_lab_15m),
                "cross_timeframe_analysis": self._analyze_cross_timeframe_patterns(live_signals, signal_lab_1m, signal_lab_15m),
                "correlation_analysis": self._analyze_comprehensive_correlations(live_signals),
                "session_optimization": self._analyze_session_optimization(live_signals, signal_lab_1m, signal_lab_15m),
                "strength_optimization": self._analyze_strength_patterns(live_signals),
                "news_impact_analysis": self._analyze_news_impact(signal_lab_1m, signal_lab_15m),
                "breakeven_optimization": self._analyze_breakeven_strategies(signal_lab_1m, signal_lab_15m),
                "ml_predictions": self._generate_ml_predictions(live_signals, signal_lab_1m),
                "actionable_insights": []
            }
            
            # Generate actionable insights
            analysis["actionable_insights"] = self._generate_comprehensive_insights(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {str(e)}")
            return {"error": str(e)}
    
    def _get_live_signals(self) -> List[Dict]:
        """Get live signals data"""
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT symbol, bias, strength, htf_aligned, htf_status, session, 
                   price, timestamp, signal_type, timeframe
            FROM live_signals 
            WHERE timestamp > NOW() - INTERVAL '30 days'
            ORDER BY timestamp DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    
    def _get_signal_lab_trades(self, table_name: str) -> List[Dict]:
        """Get signal lab trades data"""
        cursor = self.db.cursor()
        cursor.execute(f"""
            SELECT date, time, bias, session, signal_type, entry_price, stop_loss, take_profit,
                   mfe_none, be1_level, be1_hit, mfe1, be2_level, be2_hit, mfe2,
                   position_size, commission, news_proximity, news_event, created_at
            FROM {table_name}
            WHERE created_at > NOW() - INTERVAL '90 days'
            ORDER BY created_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    
    def _analyze_live_signals(self, signals: List[Dict]) -> Dict:
        """Analyze live signals patterns"""
        
        if not signals:
            return {"error": "No live signals data"}
        
        df = pd.DataFrame(signals)
        
        return {
            "total_signals": len(signals),
            "symbol_distribution": df['symbol'].value_counts().to_dict(),
            "bias_performance": {
                "bullish": {
                    "count": (df['bias'] == 'Bullish').sum(),
                    "avg_strength": df[df['bias'] == 'Bullish']['strength'].mean()
                },
                "bearish": {
                    "count": (df['bias'] == 'Bearish').sum(),
                    "avg_strength": df[df['bias'] == 'Bearish']['strength'].mean()
                }
            },
            "htf_impact": {
                "aligned_avg_strength": df[df['htf_aligned'] == True]['strength'].mean(),
                "not_aligned_avg_strength": df[df['htf_aligned'] == False]['strength'].mean(),
                "alignment_rate": (df['htf_aligned'] == True).mean() * 100
            },
            "session_breakdown": df.groupby('session').agg({
                'strength': ['count', 'mean'],
                'htf_aligned': lambda x: (x == True).mean() * 100
            }).round(2).to_dict(),
            "timeframe_analysis": df['timeframe'].value_counts().to_dict() if 'timeframe' in df.columns else {}
        }
    
    def _analyze_signal_lab_data(self, trades_1m: List[Dict], trades_15m: List[Dict]) -> Dict:
        """Analyze signal lab trading performance"""
        
        analysis = {}
        
        for timeframe, trades in [("1M", trades_1m), ("15M", trades_15m)]:
            if not trades:
                analysis[timeframe] = {"error": "No data"}
                continue
            
            df = pd.DataFrame(trades)
            
            # Calculate R-scores for different strategies
            r_scores = {
                "no_be": [],
                "be1": [],
                "be2": []
            }
            
            for _, trade in df.iterrows():
                mfe = float(trade.get('mfe_none', 0))
                be1_hit = trade.get('be1_hit', False)
                be2_hit = trade.get('be2_hit', False)
                mfe1 = float(trade.get('mfe1', 0))
                mfe2 = float(trade.get('mfe2', 0))
                
                # No breakeven strategy
                r_scores["no_be"].append(mfe if mfe > 0 else -1)
                
                # BE1 strategy
                if be1_hit:
                    r_scores["be1"].append(mfe1 if mfe1 > 0 else 0)
                else:
                    r_scores["be1"].append(-1 if mfe < 1 else 0)
                
                # BE2 strategy
                if be2_hit:
                    r_scores["be2"].append(mfe2 if mfe2 > 0 else 0)
                else:
                    r_scores["be2"].append(-1 if mfe < 2 else 0)
            
            # Calculate performance metrics
            strategy_performance = {}
            for strategy, scores in r_scores.items():
                if scores:
                    wins = len([s for s in scores if s > 0])
                    losses = len([s for s in scores if s < 0])
                    breakevens = len([s for s in scores if s == 0])
                    
                    strategy_performance[strategy] = {
                        "expectancy": np.mean(scores),
                        "win_rate": (wins + breakevens) / len(scores) * 100,
                        "avg_win": np.mean([s for s in scores if s > 0]) if wins > 0 else 0,
                        "avg_loss": np.mean([abs(s) for s in scores if s < 0]) if losses > 0 else 0,
                        "total_trades": len(scores)
                    }
            
            analysis[timeframe] = {
                "total_trades": len(trades),
                "session_performance": df.groupby('session')['mfe_none'].agg(['count', 'mean']).to_dict(),
                "bias_performance": df.groupby('bias')['mfe_none'].agg(['count', 'mean']).to_dict(),
                "signal_type_performance": df.groupby('signal_type')['mfe_none'].agg(['count', 'mean']).to_dict(),
                "strategy_comparison": strategy_performance,
                "best_strategy": max(strategy_performance.items(), key=lambda x: x[1]['expectancy'])[0] if strategy_performance else None
            }
        
        return analysis
    
    def _analyze_cross_timeframe_patterns(self, live_signals: List[Dict], trades_1m: List[Dict], trades_15m: List[Dict]) -> Dict:
        """Analyze patterns across different timeframes"""
        
        # Convert to DataFrames
        live_df = pd.DataFrame(live_signals) if live_signals else pd.DataFrame()
        trades_1m_df = pd.DataFrame(trades_1m) if trades_1m else pd.DataFrame()
        trades_15m_df = pd.DataFrame(trades_15m) if trades_15m else pd.DataFrame()
        
        patterns = {}
        
        # Session consistency across timeframes
        if not live_df.empty and not trades_1m_df.empty:
            live_sessions = live_df.groupby('session')['strength'].mean()
            trades_sessions = trades_1m_df.groupby('session')['mfe_none'].mean()
            
            patterns["session_consistency"] = {
                "live_signals_best_session": live_sessions.idxmax() if not live_sessions.empty else None,
                "trades_1m_best_session": trades_sessions.idxmax() if not trades_sessions.empty else None,
                "correlation": live_sessions.corr(trades_sessions) if len(live_sessions) > 1 and len(trades_sessions) > 1 else 0
            }
        
        # Bias consistency
        if not live_df.empty and not trades_1m_df.empty:
            live_bias = live_df['bias'].value_counts(normalize=True)
            trades_bias = trades_1m_df['bias'].value_counts(normalize=True)
            
            patterns["bias_consistency"] = {
                "live_signals_bias_dist": live_bias.to_dict(),
                "trades_1m_bias_dist": trades_bias.to_dict()
            }
        
        return patterns
    
    def _analyze_comprehensive_correlations(self, signals: List[Dict]) -> Dict:
        """Analyze correlations between all symbols"""
        
        if not signals:
            return {"error": "No signals data"}
        
        df = pd.DataFrame(signals)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['time_window'] = df['timestamp'].dt.floor('10min')
        
        # Symbol co-occurrence analysis
        correlations = {}
        divergences = {}
        
        for window, group in df.groupby('time_window'):
            if len(group) > 1:
                symbols = group[['symbol', 'bias']].values
                
                for i in range(len(symbols)):
                    for j in range(i + 1, len(symbols)):
                        sym1, bias1 = symbols[i]
                        sym2, bias2 = symbols[j]
                        
                        pair = f"{sym1}_{sym2}"
                        if pair not in correlations:
                            correlations[pair] = {"same": 0, "opposite": 0, "total": 0}
                        
                        correlations[pair]["total"] += 1
                        if bias1 == bias2:
                            correlations[pair]["same"] += 1
                        else:
                            correlations[pair]["opposite"] += 1
        
        # Calculate correlation percentages
        for pair, data in correlations.items():
            if data["total"] >= 5:  # Minimum sample size
                same_rate = data["same"] / data["total"] * 100
                opposite_rate = data["opposite"] / data["total"] * 100
                
                if same_rate > 70:
                    correlations[pair]["type"] = "POSITIVE_CORRELATION"
                elif opposite_rate > 70:
                    correlations[pair]["type"] = "NEGATIVE_CORRELATION"
                else:
                    correlations[pair]["type"] = "NO_CLEAR_PATTERN"
                
                correlations[pair]["same_rate"] = same_rate
                correlations[pair]["opposite_rate"] = opposite_rate
        
        return correlations
    
    def _analyze_session_optimization(self, live_signals: List[Dict], trades_1m: List[Dict], trades_15m: List[Dict]) -> Dict:
        """Optimize session trading based on all data"""
        
        session_analysis = {}
        
        # Analyze each data source
        for name, data in [("live_signals", live_signals), ("trades_1m", trades_1m), ("trades_15m", trades_15m)]:
            if not data:
                continue
            
            df = pd.DataFrame(data)
            
            if name == "live_signals":
                metric = 'strength'
            else:
                metric = 'mfe_none'
            
            if metric in df.columns and 'session' in df.columns:
                session_stats = df.groupby('session')[metric].agg(['count', 'mean', 'std']).round(2)
                session_analysis[name] = session_stats.to_dict()
        
        # Find optimal sessions
        optimal_sessions = {}
        for source, stats in session_analysis.items():
            if 'mean' in stats:
                best_session = max(stats['mean'].items(), key=lambda x: x[1])
                optimal_sessions[source] = best_session[0]
        
        return {
            "session_statistics": session_analysis,
            "optimal_sessions": optimal_sessions,
            "consensus_best_session": max(set(optimal_sessions.values()), key=list(optimal_sessions.values()).count) if optimal_sessions else None
        }
    
    def _analyze_strength_patterns(self, signals: List[Dict]) -> Dict:
        """Analyze signal strength patterns and optimization"""
        
        if not signals:
            return {"error": "No signals data"}
        
        df = pd.DataFrame(signals)
        
        # Strength distribution
        strength_bins = pd.cut(df['strength'], bins=[0, 50, 70, 85, 100], labels=['Weak', 'Medium', 'Strong', 'Very Strong'])
        strength_dist = strength_bins.value_counts().to_dict()
        
        # Strength by factors
        strength_analysis = {
            "distribution": strength_dist,
            "by_symbol": df.groupby('symbol')['strength'].mean().to_dict(),
            "by_session": df.groupby('session')['strength'].mean().to_dict(),
            "by_htf_alignment": {
                "aligned": df[df['htf_aligned'] == True]['strength'].mean(),
                "not_aligned": df[df['htf_aligned'] == False]['strength'].mean()
            },
            "by_bias": df.groupby('bias')['strength'].mean().to_dict()
        }
        
        return strength_analysis
    
    def _analyze_news_impact(self, trades_1m: List[Dict], trades_15m: List[Dict]) -> Dict:
        """Analyze news proximity impact on trading performance"""
        
        news_analysis = {}
        
        for timeframe, trades in [("1M", trades_1m), ("15M", trades_15m)]:
            if not trades:
                continue
            
            df = pd.DataFrame(trades)
            
            if 'news_proximity' in df.columns and 'mfe_none' in df.columns:
                news_impact = df.groupby('news_proximity')['mfe_none'].agg(['count', 'mean', 'std']).round(3)
                news_analysis[timeframe] = news_impact.to_dict()
        
        return news_analysis
    
    def _analyze_breakeven_strategies(self, trades_1m: List[Dict], trades_15m: List[Dict]) -> Dict:
        """Analyze breakeven strategy effectiveness"""
        
        be_analysis = {}
        
        for timeframe, trades in [("1M", trades_1m), ("15M", trades_15m)]:
            if not trades:
                continue
            
            df = pd.DataFrame(trades)
            
            # Calculate breakeven hit rates
            be1_hit_rate = df['be1_hit'].mean() * 100 if 'be1_hit' in df.columns else 0
            be2_hit_rate = df['be2_hit'].mean() * 100 if 'be2_hit' in df.columns else 0
            
            # Performance when BE is hit vs not hit
            be_performance = {}
            
            if 'be1_hit' in df.columns and 'mfe1' in df.columns:
                be1_hit_trades = df[df['be1_hit'] == True]
                be1_not_hit_trades = df[df['be1_hit'] == False]
                
                be_performance['be1'] = {
                    "hit_rate": be1_hit_rate,
                    "avg_mfe_when_hit": be1_hit_trades['mfe1'].mean() if not be1_hit_trades.empty else 0,
                    "avg_mfe_when_not_hit": be1_not_hit_trades['mfe_none'].mean() if not be1_not_hit_trades.empty else 0
                }
            
            if 'be2_hit' in df.columns and 'mfe2' in df.columns:
                be2_hit_trades = df[df['be2_hit'] == True]
                be2_not_hit_trades = df[df['be2_hit'] == False]
                
                be_performance['be2'] = {
                    "hit_rate": be2_hit_rate,
                    "avg_mfe_when_hit": be2_hit_trades['mfe2'].mean() if not be2_hit_trades.empty else 0,
                    "avg_mfe_when_not_hit": be2_not_hit_trades['mfe_none'].mean() if not be2_not_hit_trades.empty else 0
                }
            
            be_analysis[timeframe] = be_performance
        
        return be_analysis
    
    def _generate_ml_predictions(self, live_signals: List[Dict], trades_1m: List[Dict]) -> Dict:
        """Generate ML predictions for signal quality"""
        
        if not ML_AVAILABLE or not live_signals or not trades_1m:
            return {"error": "Insufficient data or ML not available"}
        
        try:
            # Prepare training data from signal lab
            df_trades = pd.DataFrame(trades_1m)
            
            # Create features from live signals
            df_signals = pd.DataFrame(live_signals)
            
            # Simple feature engineering
            features = []
            targets = []
            
            for _, trade in df_trades.iterrows():
                # Create feature vector
                feature_vector = [
                    1 if trade.get('bias') == 'Bullish' else 0,
                    1 if trade.get('session') == 'London' else 0,
                    1 if trade.get('session') == 'NY AM' else 0,
                    float(trade.get('mfe_none', 0))
                ]
                
                # Target: 1 if profitable (MFE > 1R), 0 otherwise
                target = 1 if float(trade.get('mfe_none', 0)) > 1.0 else 0
                
                features.append(feature_vector)
                targets.append(target)
            
            if len(features) < 20:
                return {"error": "Insufficient training samples"}
            
            # Train model
            X = np.array(features)
            y = np.array(targets)
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
            
            model = RandomForestClassifier(n_estimators=50, random_state=42)
            model.fit(X_train, y_train)
            
            # Test accuracy
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            return {
                "model_accuracy": accuracy * 100,
                "feature_importance": {
                    "bias_bullish": model.feature_importances_[0],
                    "session_london": model.feature_importances_[1],
                    "session_ny_am": model.feature_importances_[2],
                    "mfe_baseline": model.feature_importances_[3]
                },
                "training_samples": len(features),
                "profitable_rate": np.mean(targets) * 100
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _generate_comprehensive_insights(self, analysis: Dict) -> List[str]:
        """Generate actionable insights from comprehensive analysis"""
        
        insights = []
        
        # Live signals insights
        if "live_signals_analysis" in analysis:
            live_analysis = analysis["live_signals_analysis"]
            
            if "htf_impact" in live_analysis:
                htf = live_analysis["htf_impact"]
                strength_boost = htf.get("aligned_avg_strength", 0) - htf.get("not_aligned_avg_strength", 0)
                if strength_boost > 10:
                    insights.append(f"✅ HTF alignment boosts signal strength by {strength_boost:.1f}% - prioritize aligned signals")
        
        # Signal lab insights
        if "signal_lab_analysis" in analysis:
            for timeframe, data in analysis["signal_lab_analysis"].items():
                if "best_strategy" in data and data["best_strategy"]:
                    strategy = data["strategy_comparison"][data["best_strategy"]]
                    insights.append(f"📊 {timeframe}: Best strategy is {data['best_strategy']} with {strategy['expectancy']:.3f}R expectancy")
        
        # Session optimization
        if "session_optimization" in analysis:
            best_session = analysis["session_optimization"].get("consensus_best_session")
            if best_session:
                insights.append(f"🕐 Optimal trading session: {best_session} (consistent across all data)")
        
        # Correlation insights
        if "correlation_analysis" in analysis:
            strong_correlations = {k: v for k, v in analysis["correlation_analysis"].items() 
                                 if isinstance(v, dict) and v.get("same_rate", 0) > 75}
            for pair, data in strong_correlations.items():
                insights.append(f"🔗 Strong correlation: {pair} ({data['same_rate']:.1f}% same direction)")
        
        # News impact
        if "news_impact_analysis" in analysis:
            for timeframe, data in analysis["news_impact_analysis"].items():
                if "mean" in data:
                    best_news_timing = max(data["mean"].items(), key=lambda x: x[1])
                    insights.append(f"📰 {timeframe}: Best news timing is {best_news_timing[0]} ({best_news_timing[1]:.2f}R avg)")
        
        # ML predictions
        if "ml_predictions" in analysis and "model_accuracy" in analysis["ml_predictions"]:
            ml = analysis["ml_predictions"]
            insights.append(f"🤖 ML model accuracy: {ml['model_accuracy']:.1f}% (profitable rate: {ml.get('profitable_rate', 0):.1f}%)")
        
        return insights

def run_comprehensive_analysis(db_connection):
    """Run comprehensive ML analysis on all trading data"""
    
    analyzer = ComprehensiveMLAnalyzer(db_connection)
    
    print("🔍 COMPREHENSIVE ML ANALYSIS OF ALL TRADING DATA")
    print("=" * 60)
    
    analysis = analyzer.analyze_all_trading_data()
    
    if "error" in analysis:
        print(f"❌ Error: {analysis['error']}")
        return
    
    # Print summary
    summary = analysis["data_summary"]
    print(f"📊 DATA SUMMARY:")
    print(f"   Live signals: {summary['live_signals']}")
    print(f"   Signal lab 1M: {summary['signal_lab_1m']}")
    print(f"   Signal lab 15M: {summary['signal_lab_15m']}")
    
    # Print key insights
    print(f"\n💡 KEY INSIGHTS:")
    for insight in analysis["actionable_insights"]:
        print(f"   {insight}")
    
    return analysis

if __name__ == "__main__":
    print("Run this from your main server with database connection")