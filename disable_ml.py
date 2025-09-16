import re

# Read the ML engine file
with open('advanced_ml_engine.py', 'r') as f:
    content = f.read()

# Replace the predict_signal_quality method to return early
pattern = r'(def predict_signal_quality\(self, market_context: Dict, signal_data: Dict\) -> Dict\[str, Any\]:\s*""".*?"""\s*try:\s*)'
replacement = r'\1# Temporarily disabled due to feature mismatch - needs retraining\n            return {\n                "predicted_mfe": 0.0,\n                "confidence": 0.0,\n                "prediction_interval": [0.0, 0.0],\n                "feature_contributions": {},\n                "model_consensus": {},\n                "recommendation": "ML temporarily disabled - feature mismatch"\n            }\n            '

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write back
with open('advanced_ml_engine.py', 'w') as f:
    f.write(new_content)

print("ML predictions temporarily disabled")