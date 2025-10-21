import pandas as pd
import numpy as np
import sqlite3
import json
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.inspection import permutation_importance
import shap
import warnings
warnings.filterwarnings('ignore')

class FeatureImportanceAnalyzer:
    def __init__(self, db_path='trading_signals.db'):
        self.db_path = db_path
        self.rf_model = None
        self.gb_model = None
        self.feature_names = None
        self.label_encoder = LabelEncoder()
        self.shap_explainer = None
        self.shap_values_cache = None
        
    def load_data(self):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM signal_lab_trades", conn)
        conn.close()
        
        # Encode categorical features
        df['session_encoded'] = self.label_encoder.fit_transform(df['session'])
        df['bias_encoded'] = LabelEncoder().fit_transform(df['bias'])
        
        # Select features
        feature_cols = ['session_encoded', 'bias_encoded', 'mfe_none', 'mfe1', 'hour']
        X = df[feature_cols]
        y = df['r_target_hit']
        
        self.feature_names = ['session', 'bias', 'mfe_none', 'mfe1', 'hour']
        
        return train_test_split(X, y, test_size=0.2, random_state=42)
    
    def train_models(self):
        X_train, X_test, y_train, y_test = self.load_data()
        
        self.rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        self.rf_model.fit(X_train, y_train)
        
        self.gb_model = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
        self.gb_model.fit(X_train, y_train)
        
        return X_train, X_test, y_train, y_test
    
    def calculate_feature_importance(self):
        X_train, X_test, y_train, y_test = self.train_models()
        
        # Random Forest feature importance
        rf_importance = self.rf_model.feature_importances_
        
        # Gradient Boosting feature importance
        gb_importance = self.gb_model.feature_importances_
        
        # Average ensemble importance
        ensemble_importance = (rf_importance + gb_importance) / 2
        
        # Permutation importance
        perm_importance = permutation_importance(self.rf_model, X_test, y_test, n_repeats=10, random_state=42)
        
        # Normalize to percentages
        rf_pct = (rf_importance / rf_importance.sum()) * 100
        gb_pct = (gb_importance / gb_importance.sum()) * 100
        ensemble_pct = (ensemble_importance / ensemble_importance.sum()) * 100
        perm_pct = (perm_importance.importances_mean / perm_importance.importances_mean.sum()) * 100
        
        results = []
        for i, feature in enumerate(self.feature_names):
            results.append({
                'feature': feature,
                'rf_importance': float(rf_pct[i]),
                'gb_importance': float(gb_pct[i]),
                'ensemble_importance': float(ensemble_pct[i]),
                'permutation_importance': float(perm_pct[i]),
                'perm_std': float(perm_importance.importances_std[i])
            })
        
        # Sort by ensemble importance
        results.sort(key=lambda x: x['ensemble_importance'], reverse=True)
        
        return results, X_train, X_test
    
    def calculate_shap_values(self, X_train, X_test):
        # Use TreeExplainer for tree-based models
        self.shap_explainer = shap.TreeExplainer(self.rf_model)
        
        # Calculate SHAP values for test set (sample for performance)
        sample_size = min(100, len(X_test))
        X_sample = X_test.sample(n=sample_size, random_state=42) if len(X_test) > sample_size else X_test
        
        shap_values = self.shap_explainer.shap_values(X_sample)
        
        # For multi-class, average absolute SHAP values across classes
        if isinstance(shap_values, list):
            shap_importance = np.mean([np.abs(sv).mean(axis=0) for sv in shap_values], axis=0)
        else:
            shap_importance = np.abs(shap_values).mean(axis=0)
        
        # Normalize to percentages
        shap_pct = (shap_importance / shap_importance.sum()) * 100
        
        results = []
        for i, feature in enumerate(self.feature_names):
            results.append({
                'feature': feature,
                'shap_importance': float(shap_pct[i])
            })
        
        results.sort(key=lambda x: x['shap_importance'], reverse=True)
        
        # Cache for waterfall charts
        self.shap_values_cache = {
            'values': shap_values,
            'base_value': self.shap_explainer.expected_value,
            'data': X_sample.values.tolist()
        }
        
        return results
    
    def calculate_feature_correlation(self):
        X_train, X_test, y_train, y_test = self.load_data()
        
        # Calculate correlation matrix
        corr_matrix = X_train.corr()
        
        correlations = []
        for i, feat1 in enumerate(self.feature_names):
            for j, feat2 in enumerate(self.feature_names):
                if i < j:  # Only upper triangle
                    correlations.append({
                        'feature1': feat1,
                        'feature2': feat2,
                        'correlation': float(corr_matrix.iloc[i, j])
                    })
        
        return correlations
    
    def analyze_feature_stability(self):
        # Simulate time-based analysis by splitting data into time windows
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM signal_lab_trades ORDER BY date, time", conn)
        conn.close()
        
        df['session_encoded'] = self.label_encoder.fit_transform(df['session'])
        df['bias_encoded'] = LabelEncoder().fit_transform(df['bias'])
        
        feature_cols = ['session_encoded', 'bias_encoded', 'mfe_none', 'mfe1', 'hour']
        
        # Split into 5 time windows
        window_size = len(df) // 5
        stability_results = []
        
        for window_idx in range(5):
            start_idx = window_idx * window_size
            end_idx = start_idx + window_size if window_idx < 4 else len(df)
            
            window_df = df.iloc[start_idx:end_idx]
            X_window = window_df[feature_cols]
            y_window = window_df['r_target_hit']
            
            if len(X_window) < 50:
                continue
            
            model = RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42)
            model.fit(X_window, y_window)
            
            importance = model.feature_importances_
            importance_pct = (importance / importance.sum()) * 100
            
            window_result = {'window': window_idx + 1}
            for i, feature in enumerate(self.feature_names):
                window_result[feature] = float(importance_pct[i])
            
            stability_results.append(window_result)
        
        return stability_results
    
    def generate_recommendations(self, importance_results):
        recommendations = []
        
        # Top features
        top_features = [r['feature'] for r in importance_results[:3]]
        recommendations.append({
            'type': 'top_features',
            'priority': 'high',
            'message': f"Focus on top 3 features: {', '.join(top_features)}",
            'features': top_features
        })
        
        # Low importance features
        low_features = [r for r in importance_results if r['ensemble_importance'] < 5]
        if low_features:
            recommendations.append({
                'type': 'remove_features',
                'priority': 'medium',
                'message': f"Consider removing {len(low_features)} low-importance features",
                'features': [f['feature'] for f in low_features]
            })
        
        # High variance in permutation importance
        high_variance = [r for r in importance_results if r.get('perm_std', 0) > 2]
        if high_variance:
            recommendations.append({
                'type': 'unstable_features',
                'priority': 'medium',
                'message': f"{len(high_variance)} features show high variance",
                'features': [f['feature'] for f in high_variance]
            })
        
        return recommendations
    
    def run_full_analysis(self):
        print("Starting feature importance analysis...")
        
        # Calculate all importance metrics
        importance_results, X_train, X_test = self.calculate_feature_importance()
        print(f"✓ Calculated feature importance for {len(importance_results)} features")
        
        # Calculate SHAP values
        shap_results = self.calculate_shap_values(X_train, X_test)
        print("✓ Calculated SHAP values")
        
        # Merge SHAP into importance results
        shap_dict = {r['feature']: r['shap_importance'] for r in shap_results}
        for result in importance_results:
            result['shap_importance'] = shap_dict.get(result['feature'], 0)
        
        # Calculate correlations
        correlations = self.calculate_feature_correlation()
        print(f"✓ Calculated {len(correlations)} feature correlations")
        
        # Analyze stability
        stability = self.analyze_feature_stability()
        print(f"✓ Analyzed feature stability across {len(stability)} time windows")
        
        # Generate recommendations
        recommendations = self.generate_recommendations(importance_results)
        print(f"✓ Generated {len(recommendations)} recommendations")
        
        # Compile results
        output = {
            'timestamp': datetime.now().isoformat(),
            'feature_importance': importance_results,
            'correlations': correlations,
            'stability_over_time': stability,
            'recommendations': recommendations,
            'summary': {
                'total_features': len(importance_results),
                'top_feature': importance_results[0]['feature'],
                'top_importance': importance_results[0]['ensemble_importance'],
                'avg_correlation': float(np.mean([abs(c['correlation']) for c in correlations]))
            }
        }
        
        # Save to JSON
        with open('ml_feature_importance.json', 'w') as f:
            json.dump(output, f, indent=2)
        
        print("\n✓ Analysis complete! Results saved to ml_feature_importance.json")
        return output

if __name__ == '__main__':
    analyzer = FeatureImportanceAnalyzer()
    results = analyzer.run_full_analysis()
    
    print("\n=== TOP 5 FEATURES ===")
    for i, feat in enumerate(results['feature_importance'][:5], 1):
        print(f"{i}. {feat['feature']}: {feat['ensemble_importance']:.2f}%")
