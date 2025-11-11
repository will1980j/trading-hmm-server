import requests
import json

response = requests.get('https://web-production-cd33.up.railway.app/api/automated-signals/dashboard-data', timeout=10)
print(json.dumps(response.json(), indent=2))
