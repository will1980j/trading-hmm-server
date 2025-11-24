"""
STRICT LOG EXTRACTION - Railway Error Analysis
Extracts errors for /api/system-status and /api/signals/stats/today
"""
import requests
import re

RAILWAY_URL = "https://web-production-cd33.up.railway.app"

def test_endpoints():
    """Test the endpoints and capture any errors"""
    
    endpoints = [
        "/api/system-status",
        "/api/signals/stats/today"
    ]
    
    print("=" * 80)
    print("RAILWAY ENDPOINT ERROR EXTRACTION")
    print("=" * 80)
    
    for endpoint in endpoints:
        url = f"{RAILWAY_URL}{endpoint}"
        print(f"\n{'=' * 80}")
        print(f"ENDPOINT: {endpoint}")
        print(f"URL: {url}")
        print(f"{'=' * 80}\n")
        
        try:
            response = requests.get(url, timeout=10)
            
            print(f"STATUS CODE: {response.status_code}")
            print(f"HEADERS: {dict(response.headers)}")
            print(f"\nRESPONSE BODY:")
            print("-" * 80)
            
            if response.status_code >= 400:
                # Try to parse as JSON first
                try:
                    error_data = response.json()
                    print(f"JSON ERROR RESPONSE:")
                    import json
                    print(json.dumps(error_data, indent=2))
                except:
                    # Raw text response
                    print(f"RAW ERROR RESPONSE:")
                    print(response.text)
                    
                    # Try to extract Python traceback
                    text = response.text
                    if "Traceback" in text:
                        print("\n" + "=" * 80)
                        print("EXTRACTED TRACEBACK:")
                        print("=" * 80)
                        
                        # Extract traceback section
                        traceback_match = re.search(
                            r'(Traceback \(most recent call last\):.*?)(?=\n\n|\Z)',
                            text,
                            re.DOTALL
                        )
                        if traceback_match:
                            print(traceback_match.group(1))
                        
                        # Extract exception type and message
                        exception_match = re.search(
                            r'(\w+Error|Exception): (.+?)(?=\n|$)',
                            text
                        )
                        if exception_match:
                            print("\n" + "=" * 80)
                            print("EXCEPTION DETAILS:")
                            print("=" * 80)
                            print(f"TYPE: {exception_match.group(1)}")
                            print(f"MESSAGE: {exception_match.group(2)}")
                        
                        # Extract file and line number
                        file_matches = re.findall(
                            r'File "([^"]+)", line (\d+)',
                            text
                        )
                        if file_matches:
                            print("\n" + "=" * 80)
                            print("FILE LOCATIONS:")
                            print("=" * 80)
                            for file_path, line_num in file_matches:
                                print(f"  {file_path}:{line_num}")
            else:
                print(f"SUCCESS - Status {response.status_code}")
                try:
                    print(response.json())
                except:
                    print(response.text[:500])
                    
        except requests.exceptions.RequestException as e:
            print(f"REQUEST FAILED: {type(e).__name__}: {e}")
        
        print("\n")

if __name__ == "__main__":
    test_endpoints()
