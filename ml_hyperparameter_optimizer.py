"""
ML Hyperparameter Optimization for Trading Signals
Optimizes Random Forest + Gradient Boosting ensemble
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import make_scorer, precision_score, recall_score, f1_score
import joblib
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Standalone function for parallel processing (must be picklable)
def profit_score(y_true, y_pred):
    """Custom scoring: profit-based metric for trading"""
    return np.sum(np.where(y_true == y_pred, 2, -1))

class MLHyperparameterOptimizer:
    def __init__(self, db):
        self.db = db
        self.best_rf_model = None
        self.best_gb_model = None
        self.optimization_results = {}
        
    def optimize_random_forest(self, X_train, y_train):
        """Optimize Random Forest hyperparameters"""
        param_grid = {
            'n_estimators': [100, 150, 200],
            'max_depth': [5, 7, 10],
            'min_samples_split': [2, 5],
            'min_samples_leaf': [1, 2],
            'max_features': ['sqrt', 'log2']
        }
        
        rf = RandomForestClassifier(random_state=42)
        tscv = TimeSeriesSplit(n_splits=5)
        
        scoring = {
            'accuracy': 'accuracy',
            'precision': make_scorer(precision_score, zero_division=0),
            'recall': make_scorer(recall_score, zero_division=0),
            'f1': make_scorer(f1_score, zero_division=0),
            'profit': make_scorer(profit_score)
        }
        
        grid_search = GridSearchCV(
            rf, param_grid, 
            cv=tscv,
            scoring=scoring,
            refit='profit',
            n_jobs=-1,
            verbose=1
        )
        
        logger.info("🔍 Optimizing Random Forest...")
        grid_search.fit(X_train, y_train)
        
        self.best_rf_model = grid_search.best_estimator_
        
        return {
            'best_params': grid_search.best_params_,
            'best_score': grid_search.best_score_,
            'cv_results': pd.DataFrame(grid_search.cv_results_)
        }
    
    def optimize_gradient_boosting(self, X_train, y_train):
        """Optimize Gradient Boosting with early stopping"""
        param_grid = {
            'n_estimators': [100, 150, 200],
            'max_depth': [3, 5, 7],
            'learning_rate': [0.01, 0.05, 0.1],
            'subsample': [0.8, 1.0],
            'min_samples_split': [2, 5]
        }
        
        gb = GradientBoostingClassifier(random_state=42, validation_fraction=0.1, n_iter_no_change=10)
        tscv = TimeSeriesSplit(n_splits=5)
        
        scoring = {
            'accuracy': 'accuracy',
            'precision': make_scorer(precision_score, zero_division=0),
            'recall': make_scorer(recall_score, zero_division=0),
            'f1': make_scorer(f1_score, zero_division=0),
            'profit': make_scorer(profit_score)
        }
        
        grid_search = GridSearchCV(
            gb, param_grid,
            cv=tscv,
            scoring=scoring,
            refit='profit',
            n_jobs=-1,
            verbose=1
        )
        
        logger.info("🔍 Optimizing Gradient Boosting...")
        grid_search.fit(X_train, y_train)
        
        self.best_gb_model = grid_search.best_estimator_
        
        return {
            'best_params': grid_search.best_params_,
            'best_score': grid_search.best_score_,
            'cv_results': pd.DataFrame(grid_search.cv_results_)
        }
    
    def compare_with_baseline(self, X_test, y_test):
        """Compare optimized models with baseline"""
        baseline_rf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        baseline_gb = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
        
        baseline_rf.fit(X_test, y_test)
        baseline_gb.fit(X_test, y_test)
        
        baseline_rf_pred = baseline_rf.predict(X_test)
        baseline_gb_pred = baseline_gb.predict(X_test)
        optimized_rf_pred = self.best_rf_model.predict(X_test)
        optimized_gb_pred = self.best_gb_model.predict(X_test)
        
        from sklearn.metrics import accuracy_score
        
        results = {
            'baseline_rf': {
                'accuracy': accuracy_score(y_test, baseline_rf_pred),
                'precision': precision_score(y_test, baseline_rf_pred, zero_division=0),
                'recall': recall_score(y_test, baseline_rf_pred, zero_division=0),
                'f1': f1_score(y_test, baseline_rf_pred, zero_division=0),
                'profit': profit_score(y_test, baseline_rf_pred)
            },
            'optimized_rf': {
                'accuracy': accuracy_score(y_test, optimized_rf_pred),
                'precision': precision_score(y_test, optimized_rf_pred, zero_division=0),
                'recall': recall_score(y_test, optimized_rf_pred, zero_division=0),
                'f1': f1_score(y_test, optimized_rf_pred, zero_division=0),
                'profit': profit_score(y_test, optimized_rf_pred)
            },
            'baseline_gb': {
                'accuracy': accuracy_score(y_test, baseline_gb_pred),
                'precision': precision_score(y_test, baseline_gb_pred, zero_division=0),
                'recall': recall_score(y_test, baseline_gb_pred, zero_division=0),
                'f1': f1_score(y_test, baseline_gb_pred, zero_division=0),
                'profit': profit_score(y_test, baseline_gb_pred)
            },
            'optimized_gb': {
                'accuracy': accuracy_score(y_test, optimized_gb_pred),
                'precision': precision_score(y_test, optimized_gb_pred, zero_division=0),
                'recall': recall_score(y_test, optimized_gb_pred, zero_division=0),
                'f1': f1_score(y_test, optimized_gb_pred, zero_division=0),
                'profit': profit_score(y_test, optimized_gb_pred)
            }
        }
        
        results['rf_improvement'] = {
            'accuracy': (results['optimized_rf']['accuracy'] - results['baseline_rf']['accuracy']) * 100,
            'profit': results['optimized_rf']['profit'] - results['baseline_rf']['profit']
        }
        results['gb_improvement'] = {
            'accuracy': (results['optimized_gb']['accuracy'] - results['baseline_gb']['accuracy']) * 100,
            'profit': results['optimized_gb']['profit'] - results['baseline_gb']['profit']
        }
        
        return results
    
    def save_models(self, filepath_prefix='models/optimized'):
        """Save optimized models"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        rf_path = f"{filepath_prefix}_rf_{timestamp}.joblib"
        gb_path = f"{filepath_prefix}_gb_{timestamp}.joblib"
        
        joblib.dump(self.best_rf_model, rf_path)
        joblib.dump(self.best_gb_model, gb_path)
        
        logger.info(f"✅ Saved optimized models: {rf_path}, {gb_path}")
        
        return {'rf_path': rf_path, 'gb_path': gb_path}
    
    def run_full_optimization(self, X_train, y_train, X_test, y_test):
        """Run complete optimization pipeline"""
        logger.info("🚀 Starting hyperparameter optimization...")
        
        rf_results = self.optimize_random_forest(X_train, y_train)
        gb_results = self.optimize_gradient_boosting(X_train, y_train)
        
        comparison = self.compare_with_baseline(X_test, y_test)
        
        model_paths = self.save_models()
        
        results = {
            'rf_optimization': rf_results,
            'gb_optimization': gb_results,
            'comparison': comparison,
            'model_paths': model_paths,
            'timestamp': datetime.now().isoformat()
        }
        
        self.optimization_results = results
        
        logger.info("✅ Optimization complete!")
        logger.info(f"RF Improvement: {comparison['rf_improvement']['accuracy']:.2f}% accuracy")
        logger.info(f"GB Improvement: {comparison['gb_improvement']['accuracy']:.2f}% accuracy")
        
        return results

def optimize_trading_models(db):
    """Main function to optimize trading ML models"""
    from unified_ml_intelligence import get_unified_ml
    
    try:
        ml_engine = get_unified_ml(db)
        trades = ml_engine._get_all_trades()
        
        if len(trades) < 100:
            return {'error': 'Insufficient training data', 'samples': len(trades)}
        
        MAX_SAMPLES = 3000
        if len(trades) > MAX_SAMPLES:
            logger.info(f"📊 Sampling {MAX_SAMPLES} from {len(trades)} trades for optimization")
            trades = trades[-MAX_SAMPLES:]
        
        prep_result = ml_engine._prepare_training_data(trades)
        if len(prep_result) == 2:
            X, y = prep_result
        elif len(prep_result) == 3:
            X, y, _ = prep_result
        else:
            X, y = prep_result[0], prep_result[1]
        
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        optimizer = MLHyperparameterOptimizer(db)
        results = optimizer.run_full_optimization(X_train, y_train, X_test, y_test)
        
        return results
    except Exception as e:
        logger.error(f"Optimization failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {'error': str(e), 'traceback': traceback.format_exc()}
