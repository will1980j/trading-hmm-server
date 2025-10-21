"""
ML Cross-Validation System for Trading Dashboard
Implements time-series CV, out-of-sample testing, and overfitting detection
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit, cross_validate
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
import logging
from typing import Dict, List, Tuple
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TradingMLCrossValidator:
    """Cross-validation system for trading ML models"""
    
    def __init__(self, n_splits: int = 5, test_size: float = 0.2):
        self.n_splits = n_splits
        self.test_size = test_size
        self.results = {}
        
    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and target from trading data"""
        try:
            # Encode categorical features
            le_session = LabelEncoder()
            le_bias = LabelEncoder()
            
            df['session_encoded'] = le_session.fit_transform(df['session'])
            df['bias_encoded'] = le_bias.fit_transform(df['bias']) if 'bias' in df.columns else 0
            
            # Feature engineering
            features = ['session_encoded', 'bias_encoded']
            if 'hour' in df.columns:
                features.append('hour')
            if 'mfe_none' in df.columns:
                features.append('mfe_none')
            
            X = df[features].values
            
            # Create target: classify if trade hits 1R, 2R, or 3R
            y = np.zeros(len(df))
            if 'mfe_none' in df.columns:
                y[df['mfe_none'] >= 1] = 1  # Hit 1R
                y[df['mfe_none'] >= 2] = 2  # Hit 2R
                y[df['mfe_none'] >= 3] = 3  # Hit 3R
            
            logger.info(f"Prepared {len(X)} samples with {X.shape[1]} features")
            logger.info(f"Target distribution: {np.bincount(y.astype(int))}")
            
            return X, y
            
        except Exception as e:
            logger.error(f"Data preparation failed: {e}")
            raise
    
    def time_series_cv(self, X: np.ndarray, y: np.ndarray, model) -> Dict:
        """Walk-forward time-series cross-validation"""
        try:
            tscv = TimeSeriesSplit(n_splits=self.n_splits)
            fold_results = []
            
            for fold, (train_idx, val_idx) in enumerate(tscv.split(X), 1):
                X_train, X_val = X[train_idx], X[val_idx]
                y_train, y_val = y[train_idx], y[val_idx]
                
                model.fit(X_train, y_train)
                y_pred = model.predict(X_val)
                
                # Calculate metrics
                metrics = self._calculate_metrics(y_val, y_pred)
                metrics['fold'] = fold
                metrics['train_size'] = len(train_idx)
                metrics['val_size'] = len(val_idx)
                
                fold_results.append(metrics)
                logger.info(f"Fold {fold}: Accuracy={metrics['accuracy']:.3f}, F1={metrics['f1_macro']:.3f}")
            
            # Aggregate results
            cv_summary = self._aggregate_cv_results(fold_results)
            
            return {
                'method': 'time_series_cv',
                'n_splits': self.n_splits,
                'fold_results': fold_results,
                'summary': cv_summary
            }
            
        except Exception as e:
            logger.error(f"Time-series CV failed: {e}")
            raise
    
    def out_of_sample_test(self, X: np.ndarray, y: np.ndarray, model) -> Dict:
        """Hold-out test with last 20% of data"""
        try:
            split_idx = int(len(X) * (1 - self.test_size))
            
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            # Train on in-sample data
            model.fit(X_train, y_train)
            
            # Evaluate on both sets
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)
            
            in_sample_metrics = self._calculate_metrics(y_train, y_train_pred)
            out_sample_metrics = self._calculate_metrics(y_test, y_test_pred)
            
            # Overfitting detection
            overfitting_score = self._detect_overfitting(in_sample_metrics, out_sample_metrics)
            
            logger.info(f"In-sample accuracy: {in_sample_metrics['accuracy']:.3f}")
            logger.info(f"Out-of-sample accuracy: {out_sample_metrics['accuracy']:.3f}")
            logger.info(f"Overfitting score: {overfitting_score:.3f}")
            
            return {
                'method': 'out_of_sample',
                'test_size': self.test_size,
                'train_samples': len(X_train),
                'test_samples': len(X_test),
                'in_sample': in_sample_metrics,
                'out_sample': out_sample_metrics,
                'overfitting': overfitting_score,
                'overfitting_alert': self._get_overfitting_alert(overfitting_score)
            }
            
        except Exception as e:
            logger.error(f"Out-of-sample test failed: {e}")
            raise
    
    def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """Calculate comprehensive performance metrics"""
        try:
            metrics = {
                'accuracy': accuracy_score(y_true, y_pred),
                'precision_macro': precision_score(y_true, y_pred, average='macro', zero_division=0),
                'recall_macro': recall_score(y_true, y_pred, average='macro', zero_division=0),
                'f1_macro': f1_score(y_true, y_pred, average='macro', zero_division=0),
                'precision_weighted': precision_score(y_true, y_pred, average='weighted', zero_division=0),
                'recall_weighted': recall_score(y_true, y_pred, average='weighted', zero_division=0),
                'f1_weighted': f1_score(y_true, y_pred, average='weighted', zero_division=0)
            }
            
            # Confusion matrix
            cm = confusion_matrix(y_true, y_pred)
            metrics['confusion_matrix'] = cm.tolist()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Metrics calculation failed: {e}")
            return {}
    
    def _aggregate_cv_results(self, fold_results: List[Dict]) -> Dict:
        """Aggregate cross-validation results with confidence intervals"""
        try:
            metrics_keys = ['accuracy', 'precision_macro', 'recall_macro', 'f1_macro', 
                          'precision_weighted', 'recall_weighted', 'f1_weighted']
            
            summary = {}
            for key in metrics_keys:
                values = [fold[key] for fold in fold_results]
                summary[key] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'ci_95': (np.mean(values) - 1.96 * np.std(values), 
                             np.mean(values) + 1.96 * np.std(values))
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"CV aggregation failed: {e}")
            return {}
    
    def _detect_overfitting(self, in_sample: Dict, out_sample: Dict) -> float:
        """Calculate overfitting score (0=no overfit, 1=severe overfit)"""
        try:
            # Compare key metrics
            acc_diff = in_sample['accuracy'] - out_sample['accuracy']
            f1_diff = in_sample['f1_macro'] - out_sample['f1_macro']
            
            # Weighted overfitting score
            overfit_score = (acc_diff * 0.5 + f1_diff * 0.5)
            return max(0, min(1, overfit_score))  # Clamp to [0, 1]
            
        except Exception as e:
            logger.error(f"Overfitting detection failed: {e}")
            return 0.0
    
    def _get_overfitting_alert(self, score: float) -> Dict:
        """Generate overfitting alert with color coding"""
        if score < 0.05:
            return {'level': 'green', 'status': 'Good', 'message': 'No significant overfitting detected'}
        elif score < 0.15:
            return {'level': 'yellow', 'status': 'Warning', 'message': 'Mild overfitting detected'}
        else:
            return {'level': 'red', 'status': 'Alert', 'message': 'Severe overfitting detected'}
    
    def run_full_validation(self, df: pd.DataFrame) -> Dict:
        """Run complete validation suite"""
        try:
            logger.info("Starting full validation suite...")
            
            # Prepare data
            X, y = self.prepare_data(df)
            
            # Initialize models
            rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
            gb_model = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
            
            results = {
                'timestamp': datetime.now().isoformat(),
                'total_samples': len(X),
                'n_features': X.shape[1],
                'models': {}
            }
            
            # Test both models
            for model_name, model in [('random_forest', rf_model), ('gradient_boosting', gb_model)]:
                logger.info(f"\nValidating {model_name}...")
                
                # Time-series CV
                ts_cv_results = self.time_series_cv(X, y, model)
                
                # Out-of-sample test
                oos_results = self.out_of_sample_test(X, y, model)
                
                results['models'][model_name] = {
                    'time_series_cv': ts_cv_results,
                    'out_of_sample': oos_results,
                    'performance_indicator': self._get_performance_indicator(
                        ts_cv_results['summary'], 
                        oos_results
                    )
                }
            
            # Save results
            self._save_results(results)
            
            logger.info("Validation suite completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Full validation failed: {e}")
            raise
    
    def _get_performance_indicator(self, cv_summary: Dict, oos_results: Dict) -> Dict:
        """Generate overall performance indicator"""
        try:
            cv_accuracy = cv_summary['accuracy']['mean']
            oos_accuracy = oos_results['out_sample']['accuracy']
            overfit_score = oos_results['overfitting']
            
            # Overall score
            if cv_accuracy > 0.7 and oos_accuracy > 0.65 and overfit_score < 0.1:
                return {'color': 'green', 'status': 'Excellent', 'score': 'A'}
            elif cv_accuracy > 0.6 and oos_accuracy > 0.55 and overfit_score < 0.2:
                return {'color': 'yellow', 'status': 'Good', 'score': 'B'}
            else:
                return {'color': 'red', 'status': 'Needs Improvement', 'score': 'C'}
                
        except Exception as e:
            logger.error(f"Performance indicator failed: {e}")
            return {'color': 'gray', 'status': 'Unknown', 'score': 'N/A'}
    
    def _save_results(self, results: Dict):
        """Save validation results to JSON"""
        try:
            with open('ml_validation_results.json', 'w') as f:
                json.dump(results, f, indent=2)
            logger.info("Results saved to ml_validation_results.json")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")


def main():
    """Main execution function"""
    try:
        # Load trading data
        import sqlite3
        conn = sqlite3.connect('trading_signals.db')
        df = pd.read_sql_query("SELECT * FROM signal_lab_trades WHERE mfe_none IS NOT NULL", conn)
        conn.close()
        
        logger.info(f"Loaded {len(df)} trading signals")
        
        # Run validation
        validator = TradingMLCrossValidator(n_splits=5, test_size=0.2)
        results = validator.run_full_validation(df)
        
        # Print summary
        print("\n" + "="*80)
        print("ML CROSS-VALIDATION RESULTS")
        print("="*80)
        
        for model_name, model_results in results['models'].items():
            print(f"\n{model_name.upper()}:")
            print(f"  Performance: {model_results['performance_indicator']['status']} ({model_results['performance_indicator']['score']})")
            
            cv_acc = model_results['time_series_cv']['summary']['accuracy']
            print(f"  CV Accuracy: {cv_acc['mean']:.3f} ± {cv_acc['std']:.3f}")
            
            oos = model_results['out_of_sample']
            print(f"  Out-of-Sample Accuracy: {oos['out_sample']['accuracy']:.3f}")
            print(f"  Overfitting: {oos['overfitting_alert']['status']} ({oos['overfitting']:.3f})")
        
        print("\n" + "="*80)
        
    except Exception as e:
        logger.error(f"Main execution failed: {e}")
        raise


if __name__ == "__main__":
    main()
