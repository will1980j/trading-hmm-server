#!/usr/bin/env python3

import requests
import json

def deploy_fixed_v2_stats():
    """Deploy fixed V2 stats endpoint to Railway"""
    
    print("🔧 DEPLOYING FIXED V2 STATS ENDPOINT")
    print("=" * 50)
    
    # Fixed V2 stats endpoint code
    fixed_endpoint_code = '''
@app.route('/api/v2/stats', methods=['GET'])
def get_v2_stats():
    """Get comprehensive V2 automation statistics - Public endpoint for dashboard"""
    try:
        # Check database availability first
        if not db_enabled or not db:
            return jsonify({
                "total_signals": 0,
                "pending_trades": 0,
                "active_trades": 0,
                "today_signals": 0,
                "public_access": True,
                "error": "Database not available"
            })

        # Always try to get basic stats (public access)
        try:
            cursor = db.conn.cursor()
            
            # Simple query first to test connection
            cursor.execute("SELECT COUNT(*) FROM signal_lab_v2_trades;")
            total_count = cursor.fetchone()[0] or 0
            
            # Get detailed stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_signals,
                    COUNT(CASE WHEN trade_status = 'pending_confirmation' THEN 1 END) as pending_trades,
                    COUNT(CASE WHEN active_trade = true THEN 1 END) as active_trades,
                    COUNT(CASE WHEN DATE(created_at) = CURRENT_DATE THEN 1 END) as today_signals
                FROM signal_lab_v2_trades;
            """)
            
            result = cursor.fetchone()
            if result:
                return jsonify({
                    "total_signals": result[0] or 0,
                    "pending_trades": result[1] or 0,
                    "active_trades": result[2] or 0,
                    "today_signals": result[3] or 0,
                    "public_access": True,
                    "status": "success"
                })
            else:
                return jsonify({
                    "total_signals": 0,
                    "pending_trades": 0,
                    "active_trades": 0,
                    "today_signals": 0,
                    "public_access": True,
                    "status": "no_data"
                })
                
        except Exception as db_error:
            logger.error(f"V2 stats database error: {str(db_error)}")
            return jsonify({
                "total_signals": 0,
                "pending_trades": 0,
                "active_trades": 0,
                "today_signals": 0,
                "public_access": True,
                "error": f"Database query failed: {str(db_error)}",
                "status": "error"
            })
        
    except Exception as e:
        logger.error(f"V2 stats general error: {str(e)}")
        return jsonify({
            "total_signals": 0,
            "pending_trades": 0,
            "active_trades": 0,
            "today_signals": 0,
            "public_access": True,
            "error": f"Endpoint error: {str(e)}",
            "status": "error"
        }), 500
'''
    
    # Deploy to Railway
    try:
        response = requests.post(
            "https://web-production-cd33.up.railway.app/api/deploy-code",
            json={
                "code": fixed_endpoint_code,
                "description": "Fixed V2 stats endpoint with better error handling"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Fixed V2 stats endpoint deployed successfully!")
            return True
        else:
            print(f"❌ Deployment failed: {response.status_code}")
            print(response.text[:500])
            return False
            
    except Exception as e:
        print(f"❌ Deployment error: {e}")
        return False

def test_fixed_endpoint():
    """Test the fixed endpoint"""
    print("\n🧪 TESTING FIXED ENDPOINT")
    print("=" * 30)
    
    try:
        response = requests.get(
            "https://web-production-cd33.up.railway.app/api/v2/stats",
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS!")
            print(json.dumps(data, indent=2))
        else:
            print("❌ Still failing:")
            print(response.text[:300])
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    if deploy_fixed_v2_stats():
        # Wait a moment for deployment
        import time
        time.sleep(3)
        test_fixed_endpoint()