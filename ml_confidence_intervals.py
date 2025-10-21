"""
ML Confidence Intervals & Uncertainty Quantification for Trading Predictions
Bootstrap sampling, entropy calculation, and risk-adjusted confidence scoring
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
from scipy import stats
from scipy.stats import entropy
import logging
import json
from typing import Dict, List, Tuple
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MLConfidenceScorer:
    """Confidence interval and uncertainty quantification for ML predictions"""
    
    def __init__(self, n_bootstrap: int = 100, confidence_level: float = 0.95):
        self.n_bootstrap = n_bootstrap
        self.confidence_level = confidence_level
        self.models = []
        self.confidence_thresholds = {'high': 0.80, 'medium': 0.50, 'low': 0.0}
        
    def train_ensemble(self, X: np.ndarray, y: np.ndarray):
        """Train ensemble models"""
        try:
            rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
            gb = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
            
            rf.fit(X, y)
            gb.fit(X, y)
            
            self.models = [rf, gb]
            logger.info(f"Trained {len(self.models)} models")
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            raise
    
    def predict_with_confidence(self, X: np.ndarray) -> List[Dict]:
        """Generate predictions with confidence intervals"""
        try:
            predictions = []
            
            for i in range(len(X)):
                sample = X[i:i+1]
                
                # Get predictions from all models
                model_probs = [model.predict_proba(sample)[0] for model in self.models]
                
                # Ensemble prediction (average probabilities)
                avg_probs = np.mean(model_probs, axis=0)
                predicted_class = np.argmax(avg_probs)
                confidence_score = avg_probs[predicted_class]
                
                # Bootstrap confidence interval
                ci_lower, ci_upper = self._bootstrap_ci(sample, predicted_class)
                
                # Uncertainty quantification
                uncertainty = self._calculate_uncertainty(avg_probs)
                
                # Confidence level
                confidence_level = self._get_confidence_level(confidence_score)
                
                prediction = {
                    'prediction': int(predicted_class),
                    'prediction_label': self._get_prediction_label(predicted_class),
                    'confidence_score': float(confidence_score),
                    'confidence_interval': {
                        'lower': float(ci_lower),
                        'upper': float(ci_upper),
                        'width': float(ci_upper - ci_lower)
                    },
                    'uncertainty_level': float(uncertainty),
                    'confidence_level': confidence_level,
                    'class_probabilities': {
                        '0R': float(avg_probs[0]) if len(avg_probs) > 0 else 0.0,
                        '1R': float(avg_probs[1]) if len(avg_probs) > 1 else 0.0,
                        '2R': float(avg_probs[2]) if len(avg_probs) > 2 else 0.0,
                        '3R': float(avg_probs[3]) if len(avg_probs) > 3 else 0.0
                    },
                    'risk_adjusted_size': self._calculate_position_size(confidence_score),
                    'alert': self._generate_alert(confidence_score, uncertainty)
                }
                
                predictions.append(prediction)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise
    
    def _bootstrap_ci(self, X: np.ndarray, predicted_class: int) -> Tuple[float, float]:
        """Calculate bootstrap confidence interval"""
        try:
            bootstrap_preds = []
            
            for _ in range(self.n_bootstrap):
                # Random model selection with replacement
                model = np.random.choice(self.models)
                probs = model.predict_proba(X)[0]
                bootstrap_preds.append(probs[predicted_class])
            
            # Calculate percentile-based CI
            alpha = (1 - self.confidence_level) / 2
            ci_lower = np.percentile(bootstrap_preds, alpha * 100)
            ci_upper = np.percentile(bootstrap_preds, (1 - alpha) * 100)
            
            return ci_lower, ci_upper
            
        except Exception as e:
            logger.error(f"Bootstrap CI failed: {e}")
            return 0.0, 1.0
    
    def _calculate_uncertainty(self, probs: np.ndarray) -> float:
        """Calculate prediction uncertainty using entropy"""
        try:
            # Normalize probabilities
            probs = probs / np.sum(probs)
            
            # Shannon entropy (normalized to [0, 1])
            max_entropy = np.log(len(probs))
            uncertainty = entropy(probs) / max_entropy if max_entropy > 0 else 0.0
            
            return uncertainty
            
        except Exception as e:
            logger.error(f"Uncertainty calculation failed: {e}")
            return 1.0
    
    def _get_confidence_level(self, confidence_score: float) -> Dict:
        """Determine confidence level with color coding"""
        if confidence_score >= self.confidence_thresholds['high']:
            return {
                'level': 'high',
                'color': '#10b981',
                'label': 'High Confidence',
                'icon': '🟢'
            }
        elif confidence_score >= self.confidence_thresholds['medium']:
            return {
                'level': 'medium',
                'color': '#f59e0b',
                'label': 'Medium Confidence',
                'icon': '🟡'
            }
        else:
            return {
                'level': 'low',
                'color': '#ef4444',
                'label': 'Low Confidence',
                'icon': '🔴'
            }
    
    def _get_prediction_label(self, predicted_class: int) -> str:
        """Convert class to label"""
        labels = {0: '0R (Loss)', 1: '1R Hit', 2: '2R Hit', 3: '3R Hit'}
        return labels.get(predicted_class, 'Unknown')
    
    def _calculate_position_size(self, confidence_score: float) -> Dict:
        """Calculate risk-adjusted position size based on confidence"""
        base_size = 1.0
        
        if confidence_score >= 0.80:
            multiplier = 1.5
            recommendation = 'Full position'
        elif confidence_score >= 0.65:
            multiplier = 1.0
            recommendation = 'Standard position'
        elif confidence_score >= 0.50:
            multiplier = 0.5
            recommendation = 'Reduced position'
        else:
            multiplier = 0.25
            recommendation = 'Minimal position'
        
        return {
            'multiplier': multiplier,
            'size': base_size * multiplier,
            'recommendation': recommendation
        }
    
    def _generate_alert(self, confidence_score: float, uncertainty: float) -> Dict:
        """Generate alert for low-confidence predictions"""
        if confidence_score < 0.50 or uncertainty > 0.7:
            return {
                'active': True,
                'level': 'warning',
                'message': f'Low confidence ({confidence_score:.1%}) - Consider skipping trade',
                'color': '#ef4444'
            }
        elif confidence_score < 0.65 or uncertainty > 0.5:
            return {
                'active': True,
                'level': 'caution',
                'message': f'Moderate confidence ({confidence_score:.1%}) - Reduce position size',
                'color': '#f59e0b'
            }
        else:
            return {
                'active': False,
                'level': 'ok',
                'message': f'Good confidence ({confidence_score:.1%})',
                'color': '#10b981'
            }
    
    def analyze_confidence_performance(self, predictions: List[Dict], actuals: np.ndarray) -> Dict:
        """Analyze historical confidence vs actual performance"""
        try:
            df = pd.DataFrame(predictions)
            df['actual'] = actuals
            df['correct'] = df['prediction'] == df['actual']
            
            # Performance by confidence level
            performance_by_confidence = {}
            for level in ['high', 'medium', 'low']:
                mask = df['confidence_level'].apply(lambda x: x['level'] == level)
                if mask.sum() > 0:
                    performance_by_confidence[level] = {
                        'count': int(mask.sum()),
                        'accuracy': float(df[mask]['correct'].mean()),
                        'avg_confidence': float(df[mask]['confidence_score'].mean())
                    }
            
            # Confidence distribution
            confidence_bins = [0, 0.5, 0.65, 0.8, 1.0]
            confidence_labels = ['Low', 'Medium', 'High', 'Very High']
            df['confidence_bin'] = pd.cut(df['confidence_score'], bins=confidence_bins, labels=confidence_labels)
            
            distribution = df['confidence_bin'].value_counts().to_dict()
            
            return {
                'performance_by_confidence': performance_by_confidence,
                'confidence_distribution': {str(k): int(v) for k, v in distribution.items()},
                'overall_accuracy': float(df['correct'].mean()),
                'avg_confidence': float(df['confidence_score'].mean()),
                'avg_uncertainty': float(df['uncertainty_level'].mean())
            }
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {e}")
            return {}
    
    def save_predictions(self, predictions: List[Dict], filename: str = 'ml_confidence_predictions.json'):
        """Save predictions with confidence scores"""
        try:
            output = {
                'timestamp': datetime.now().isoformat(),
                'total_predictions': len(predictions),
                'predictions': predictions,
                'summary': {
                    'high_confidence': sum(1 for p in predictions if p['confidence_level']['level'] == 'high'),
                    'medium_confidence': sum(1 for p in predictions if p['confidence_level']['level'] == 'medium'),
                    'low_confidence': sum(1 for p in predictions if p['confidence_level']['level'] == 'low'),
                    'avg_confidence': np.mean([p['confidence_score'] for p in predictions]),
                    'avg_uncertainty': np.mean([p['uncertainty_level'] for p in predictions])
                }
            }
            
            with open(filename, 'w') as f:
                json.dump(output, f, indent=2)
            
            logger.info(f"Predictions saved to {filename}")
            
        except Exception as e:
            logger.error(f"Save failed: {e}")


def prepare_data(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    """Prepare features and target"""
    le_session = LabelEncoder()
    le_bias = LabelEncoder()
    
    df['session_encoded'] = le_session.fit_transform(df['session'])
    df['bias_encoded'] = le_bias.fit_transform(df['bias']) if 'bias' in df.columns else 0
    
    features = ['session_encoded', 'bias_encoded']
    if 'hour' in df.columns:
        features.append('hour')
    if 'mfe_none' in df.columns:
        features.append('mfe_none')
    
    X = df[features].values
    
    y = np.zeros(len(df))
    if 'mfe_none' in df.columns:
        y[df['mfe_none'] >= 1] = 1
        y[df['mfe_none'] >= 2] = 2
        y[df['mfe_none'] >= 3] = 3
    
    return X, y


def main():
    """Main execution"""
    try:
        import sqlite3
        
        # Load data
        conn = sqlite3.connect('trading_signals.db')
        df = pd.read_sql_query("SELECT * FROM signal_lab_trades WHERE mfe_none IS NOT NULL LIMIT 100", conn)
        conn.close()
        
        logger.info(f"Loaded {len(df)} signals")
        
        # Prepare data
        X, y = prepare_data(df)
        
        # Split train/test
        split = int(len(X) * 0.8)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]
        
        # Train and predict
        scorer = MLConfidenceScorer(n_bootstrap=100, confidence_level=0.95)
        scorer.train_ensemble(X_train, y_train)
        
        predictions = scorer.predict_with_confidence(X_test)
        
        # Analyze performance
        performance = scorer.analyze_confidence_performance(predictions, y_test)
        
        # Save results
        scorer.save_predictions(predictions)
        
        # Print summary
        print("\n" + "="*80)
        print("ML CONFIDENCE SCORING RESULTS")
        print("="*80)
        print(f"\nTotal Predictions: {len(predictions)}")
        print(f"Average Confidence: {performance['avg_confidence']:.1%}")
        print(f"Average Uncertainty: {performance['avg_uncertainty']:.3f}")
        print(f"\nOverall Accuracy: {performance['overall_accuracy']:.1%}")
        
        print("\nPerformance by Confidence Level:")
        for level, stats in performance['performance_by_confidence'].items():
            print(f"  {level.upper()}: {stats['count']} trades, {stats['accuracy']:.1%} accuracy")
        
        print("\nConfidence Distribution:")
        for bin_name, count in performance['confidence_distribution'].items():
            print(f"  {bin_name}: {count} trades")
        
        print("\nSample Predictions:")
        for i, pred in enumerate(predictions[:5], 1):
            print(f"\n  Prediction {i}:")
            print(f"    Class: {pred['prediction_label']}")
            print(f"    Confidence: {pred['confidence_score']:.1%} {pred['confidence_level']['icon']}")
            print(f"    CI: [{pred['confidence_interval']['lower']:.3f}, {pred['confidence_interval']['upper']:.3f}]")
            print(f"    Position Size: {pred['risk_adjusted_size']['recommendation']}")
            if pred['alert']['active']:
                print(f"    Alert: {pred['alert']['message']}")
        
        print("\n" + "="*80)
        
    except Exception as e:
        logger.error(f"Main execution failed: {e}")
        raise


if __name__ == "__main__":
    main()
