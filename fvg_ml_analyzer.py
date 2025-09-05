#!/usr/bin/env python3
"""
ML Analysis of FVG/IFVG Bias and Correlated Symbols
Uses your actual trading data to find real patterns
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
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

logger = logging.getLogger(__name__)

class FVGMLAnalyzer:
    """
    ML Analyzer for FVG/IFVG patterns and correlated symbol relationships
    Uses your actual signal data to find profitable patterns
    """
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        
    def analyze_fvg_patterns(self) -> Dict:
        """Analyze FVG/IFVG patterns from your live signals data"""
        
        if not self.db:
            return {"error": "No database connection"}
        
        try:
            # Get your actual FVG/IFVG signals
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT symbol, bias, strength, htf_aligned, htf_status, session, 
                       price, timestamp, signal_type
                FROM live_signals 
                WHERE timestamp > NOW() - INTERVAL '7 days'
                ORDER BY timestamp DESC
            """)
            
            signals = [dict(row) for row in cursor.fetchall()]
            
            if len(signals) < 20:
                return {"error": "Need more signal data for analysis"}
            
            # Analyze patterns
            patterns = self._find_fvg_patterns(signals)
            correlations = self._analyze_symbol_correlations(signals)
            session_analysis = self._analyze_session_performance(signals)
            htf_analysis = self._analyze_htf_effectiveness(signals)
            
            return {
                "total_signals": len(signals),
                "fvg_patterns": patterns,
                "symbol_correlations": correlations,
                "session_performance": session_analysis,
                "htf_effectiveness": htf_analysis,
                "recommendations": self._generate_recommendations(patterns, correlations, session_analysis, htf_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing FVG patterns: {str(e)}")
            return {"error": str(e)}
    
    def _find_fvg_patterns(self, signals: List[Dict]) -> Dict:
        """Find patterns in FVG/IFVG signal performance"""
        
        df = pd.DataFrame(signals)
        
        patterns = {
            "bias_distribution": df['bias'].value_counts().to_dict(),
            "strength_by_bias": df.groupby('bias')['strength'].mean().to_dict(),
            "htf_alignment_impact": {},
            "session_bias_patterns": {}
        }
        
        # HTF alignment impact on strength
        if 'htf_aligned' in df.columns:
            patterns["htf_alignment_impact"] = {
                "aligned_avg_strength": df[df['htf_aligned'] == True]['strength'].mean(),
                "not_aligned_avg_strength": df[df['htf_aligned'] == False]['strength'].mean(),
                "alignment_rate": (df['htf_aligned'] == True).mean() * 100
            }
        
        # Session-specific bias patterns
        session_bias = df.groupby(['session', 'bias']).size().unstack(fill_value=0)
        patterns["session_bias_patterns"] = session_bias.to_dict()
        
        return patterns
    
    def _analyze_symbol_correlations(self, signals: List[Dict]) -> Dict:
        """Analyze correlations between symbols in your signals"""
        
        df = pd.DataFrame(signals)
        
        # Group signals by time windows to find correlations
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['time_window'] = df['timestamp'].dt.floor('5min')  # 5-minute windows
        
        correlations = {}
        
        # Find symbols that signal together
        symbol_pairs = {}
        for window, group in df.groupby('time_window'):
            if len(group) > 1:
                symbols = group['symbol'].tolist()
                biases = group['bias'].tolist()
                
                for i, sym1 in enumerate(symbols):
                    for j, sym2 in enumerate(symbols):
                        if i < j:  # Avoid duplicates
                            pair = f"{sym1}_{sym2}"
                            if pair not in symbol_pairs:
                                symbol_pairs[pair] = {"same_bias": 0, "opposite_bias": 0, "total": 0}
                            
                            symbol_pairs[pair]["total"] += 1
                            if biases[i] == biases[j]:
                                symbol_pairs[pair]["same_bias"] += 1
                            else:
                                symbol_pairs[pair]["opposite_bias"] += 1
        
        # Calculate correlation percentages
        for pair, data in symbol_pairs.items():
            if data["total"] >= 3:  # Minimum occurrences
                correlations[pair] = {
                    "correlation_rate": data["same_bias"] / data["total"] * 100,
                    "divergence_rate": data["opposite_bias"] / data["total"] * 100,
                    "sample_size": data["total"]
                }
        
        return correlations
    
    def _analyze_session_performance(self, signals: List[Dict]) -> Dict:
        """Analyze which sessions produce the best signals"""
        
        df = pd.DataFrame(signals)
        
        session_stats = {}
        for session in df['session'].unique():
            session_data = df[df['session'] == session]
            
            session_stats[session] = {
                "signal_count": len(session_data),
                "avg_strength": session_data['strength'].mean(),
                "bias_distribution": session_data['bias'].value_counts().to_dict(),
                "htf_alignment_rate": (session_data['htf_aligned'] == True).mean() * 100 if 'htf_aligned' in session_data.columns else 0
            }
        
        return session_stats
    
    def _analyze_htf_effectiveness(self, signals: List[Dict]) -> Dict:
        """Analyze HTF alignment effectiveness"""
        
        df = pd.DataFrame(signals)
        
        if 'htf_aligned' not in df.columns:
            return {"error": "No HTF alignment data"}
        
        htf_analysis = {
            "aligned_signals": {
                "count": (df['htf_aligned'] == True).sum(),
                "avg_strength": df[df['htf_aligned'] == True]['strength'].mean(),
                "bias_distribution": df[df['htf_aligned'] == True]['bias'].value_counts().to_dict()
            },
            "not_aligned_signals": {
                "count": (df['htf_aligned'] == False).sum(),
                "avg_strength": df[df['htf_aligned'] == False]['strength'].mean(),
                "bias_distribution": df[df['htf_aligned'] == False]['bias'].value_counts().to_dict()
            }
        }
        
        # Calculate effectiveness
        aligned_strength = htf_analysis["aligned_signals"]["avg_strength"]
        not_aligned_strength = htf_analysis["not_aligned_signals"]["avg_strength"]
        
        htf_analysis["effectiveness"] = {
            "strength_boost": aligned_strength - not_aligned_strength,
            "alignment_rate": (df['htf_aligned'] == True).mean() * 100
        }
        
        return htf_analysis
    
    def _generate_recommendations(self, patterns: Dict, correlations: Dict, sessions: Dict, htf: Dict) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        
        recommendations = []
        
        # HTF recommendations
        if htf.get("effectiveness", {}).get("strength_boost", 0) > 10:
            recommendations.append(f"✅ HTF alignment adds {htf['effectiveness']['strength_boost']:.1f}% strength - prioritize aligned signals")
        
        # Session recommendations
        best_session = max(sessions.items(), key=lambda x: x[1]['avg_strength'])
        recommendations.append(f"🕐 Best session: {best_session[0]} (avg strength: {best_session[1]['avg_strength']:.1f}%)")
        
        # Correlation recommendations
        strong_correlations = {k: v for k, v in correlations.items() if v['correlation_rate'] > 70 and v['sample_size'] >= 5}
        if strong_correlations:
            for pair, data in strong_correlations.items():
                recommendations.append(f"🔗 Strong correlation: {pair} ({data['correlation_rate']:.1f}% same bias)")
        
        # Divergence opportunities
        strong_divergences = {k: v for k, v in correlations.items() if v['divergence_rate'] > 70 and v['sample_size'] >= 5}
        if strong_divergences:
            for pair, data in strong_divergences.items():
                recommendations.append(f"⚡ Divergence opportunity: {pair} ({data['divergence_rate']:.1f}% opposite bias)")
        
        return recommendations
    
    def predict_signal_quality(self, signal_data: Dict) -> Dict:
        """Predict signal quality based on historical patterns"""
        
        if not ML_AVAILABLE:
            return {"error": "ML libraries not available"}
        
        try:
            # Get historical data for training
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT bias, strength, htf_aligned, session, symbol,
                       CASE WHEN strength > 80 THEN 1 ELSE 0 END as high_quality
                FROM live_signals 
                WHERE timestamp > NOW() - INTERVAL '30 days'
                AND strength IS NOT NULL
            """)
            
            training_data = [dict(row) for row in cursor.fetchall()]
            
            if len(training_data) < 50:
                return {"error": "Insufficient training data"}
            
            # Prepare features
            df = pd.DataFrame(training_data)
            features = self._prepare_ml_features(df)
            target = df['high_quality'].values
            
            # Train model
            X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
            
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Test accuracy
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Predict current signal
            current_features = self._prepare_signal_features(signal_data)
            quality_prob = model.predict_proba([current_features])[0][1]  # Probability of high quality
            
            # Feature importance
            feature_names = ['bias_bullish', 'htf_aligned', 'session_encoded', 'symbol_encoded']
            importance = dict(zip(feature_names, model.feature_importances_))
            
            return {
                "quality_probability": quality_prob * 100,
                "model_accuracy": accuracy * 100,
                "feature_importance": importance,
                "recommendation": "HIGH QUALITY" if quality_prob > 0.7 else "MEDIUM QUALITY" if quality_prob > 0.4 else "LOW QUALITY"
            }
            
        except Exception as e:
            logger.error(f"Error in ML prediction: {str(e)}")
            return {"error": str(e)}
    
    def _prepare_ml_features(self, df: pd.DataFrame) -> np.ndarray:
        """Prepare features for ML model"""
        
        features = []
        
        # Bias encoding
        features.append((df['bias'] == 'Bullish').astype(int))
        
        # HTF alignment
        features.append(df['htf_aligned'].astype(int))
        
        # Session encoding (simplified)
        session_map = {'London': 1, 'NY AM': 2, 'NY PM': 3, 'Asia': 4}
        features.append(df['session'].map(session_map).fillna(0))
        
        # Symbol encoding
        symbol_map = {'NQ1!': 1, 'ES1!': 2, 'YM1!': 3, 'DXY': 4}
        features.append(df['symbol'].map(symbol_map).fillna(0))
        
        return np.column_stack(features)
    
    def _prepare_signal_features(self, signal_data: Dict) -> List[float]:
        """Prepare features for a single signal"""
        
        features = []
        
        # Bias encoding
        features.append(1.0 if signal_data.get('bias') == 'Bullish' else 0.0)
        
        # HTF alignment
        features.append(1.0 if signal_data.get('htf_aligned') else 0.0)
        
        # Session encoding
        session_map = {'London': 1, 'NY AM': 2, 'NY PM': 3, 'Asia': 4}
        features.append(float(session_map.get(signal_data.get('session'), 0)))
        
        # Symbol encoding
        symbol_map = {'NQ1!': 1, 'ES1!': 2, 'YM1!': 3, 'DXY': 4}
        features.append(float(symbol_map.get(signal_data.get('symbol'), 0)))
        
        return features

def analyze_current_fvg_data(db_connection):
    """Analyze current FVG/IFVG data with ML"""
    
    analyzer = FVGMLAnalyzer(db_connection)
    
    print("🔍 ANALYZING YOUR FVG/IFVG DATA WITH ML")
    print("=" * 50)
    
    # Analyze patterns
    analysis = analyzer.analyze_fvg_patterns()
    
    if "error" in analysis:
        print(f"❌ Error: {analysis['error']}")
        return
    
    print(f"📊 Analyzed {analysis['total_signals']} signals")
    
    # FVG Patterns
    print(f"\n🎯 FVG PATTERNS:")
    patterns = analysis['fvg_patterns']
    print(f"   Bias distribution: {patterns['bias_distribution']}")
    print(f"   Strength by bias: {patterns['strength_by_bias']}")
    
    # HTF Impact
    if patterns['htf_alignment_impact']:
        htf = patterns['htf_alignment_impact']
        print(f"   HTF aligned strength: {htf.get('aligned_avg_strength', 0):.1f}%")
        print(f"   HTF not aligned strength: {htf.get('not_aligned_avg_strength', 0):.1f}%")
    
    # Correlations
    print(f"\n🔗 SYMBOL CORRELATIONS:")
    for pair, data in analysis['symbol_correlations'].items():
        print(f"   {pair}: {data['correlation_rate']:.1f}% same bias ({data['sample_size']} samples)")
    
    # Sessions
    print(f"\n🕐 SESSION PERFORMANCE:")
    for session, data in analysis['session_performance'].items():
        print(f"   {session}: {data['signal_count']} signals, {data['avg_strength']:.1f}% avg strength")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    for rec in analysis['recommendations']:
        print(f"   {rec}")

if __name__ == "__main__":
    # Would need database connection
    print("Run this from your main server with database connection")