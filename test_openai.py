import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get('OPENAI_API_KEY')

if api_key:
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
        json={
            'model': 'gpt-4o',
            'messages': [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'OpenAI HTTP test successful'"}
            ],
            'max_tokens': 50,
            'temperature': 0.3
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("SUCCESS:", result['choices'][0]['message']['content'])
    else:
        print("ERROR:", response.status_code, response.text)
else:
    print("No API key found")