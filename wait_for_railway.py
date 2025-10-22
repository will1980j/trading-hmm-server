"""
Wait for Railway to finish deploying
"""
import requests
import time

def check_railway():
    """Check if Railway is up"""
    try:
        response = requests.get(
            "https://web-production-cd33.up.railway.app/health",
            timeout=5
        )
        return response.status_code == 200
    except:
        return False

def wait_for_deployment(max_wait=300):
    """Wait for Railway deployment to complete"""
    print("⏳ Waiting for Railway deployment...")
    print("   This usually takes 2-3 minutes")
    
    start_time = time.time()
    attempt = 0
    
    while time.time() - start_time < max_wait:
        attempt += 1
        elapsed = int(time.time() - start_time)
        
        print(f"\r   Attempt {attempt} ({elapsed}s elapsed)...", end='', flush=True)
        
        if check_railway():
            print(f"\n\n✅ Railway is UP! (took {elapsed}s)")
            return True
        
        time.sleep(5)
    
    print(f"\n\n❌ Timeout after {max_wait}s")
    return False

if __name__ == '__main__':
    if wait_for_deployment():
        print("\n🎯 Railway is ready!")
        print("📝 Next steps:")
        print("   1. Run: python reset_railway_db.py")
        print("   2. Run: python test_railway_webhook.py")
    else:
        print("\n💡 Check Railway dashboard for deployment errors")
