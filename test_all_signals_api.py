import requests

r = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/all-signals')
print(f'Status: {r.status_code}')

if r.status_code == 200:
    data = r.json()
    print(f'Success: {data.get("success")}')
    print(f'Total: {data.get("total")}')
    print(f'Signals: {len(data.get("signals", []))}')
    
    if data.get("signals"):
        print('\nFirst signal:')
        signal = data["signals"][0]
        for key, value in signal.items():
            print(f'  {key}: {value}')
else:
    print(f'Error: {r.text}')
