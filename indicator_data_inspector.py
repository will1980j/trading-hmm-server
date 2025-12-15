"""
Indicator Data Inspector
Receives bulk signal data from indicator and creates digestible analysis
"""

from flask import request, jsonify
import json
from datetime import datetime
import os

# Storage for received signals
received_signals = []

def register_inspector_endpoint(app):
    """Register the inspection endpoint"""
    
    @app.route('/api/indicator-inspector/receive', methods=['POST'])
    def receive_indicator_data():
        """Receive bulk signal data from indicator"""
        try:
            data = request.get_json()
            
            # Store the batch
            batch_num = data.get('batch_number', 0)
            signals = data.get('signals', [])
            
            received_signals.extend(signals)
            
            # Log to file for inspection
            log_file = 'indicator_export_log.json'
            
            with open(log_file, 'a') as f:
                f.write(json.dumps({
                    'timestamp': datetime.now().isoformat(),
                    'batch': batch_num,
                    'count': len(signals),
                    'signals': signals
                }) + '\n')
            
            print(f"✅ Received batch {batch_num} with {len(signals)} signals")
            print(f"   Total received: {len(received_signals)}")
            
            return jsonify({
                'success': True,
                'batch_received': batch_num,
                'signals_in_batch': len(signals),
                'total_received': len(received_signals)
            }), 200
            
        except Exception as e:
            print(f"❌ Error receiving data: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/indicator-inspector/summary', methods=['GET'])
    def get_inspector_summary():
        """Get summary of received data"""
        if not received_signals:
            return jsonify({
                'success': True,
                'total_signals': 0,
                'message': 'No signals received yet'
            }), 200
        
        # Analyze received data
        active = [s for s in received_signals if not s.get('completed')]
        completed = [s for s in received_signals if s.get('completed')]
        
        # Date range
        dates = [s.get('date') for s in received_signals if s.get('date')]
        oldest = min(dates) if dates else None
        newest = max(dates) if dates else None
        
        # Direction breakdown
        bullish = len([s for s in received_signals if s.get('direction') == 'Bullish'])
        bearish = len([s for s in received_signals if s.get('direction') == 'Bearish'])
        
        return jsonify({
            'success': True,
            'total_signals': len(received_signals),
            'active': len(active),
            'completed': len(completed),
            'date_range': {
                'oldest': oldest,
                'newest': newest
            },
            'direction': {
                'bullish': bullish,
                'bearish': bearish
            },
            'sample_signals': received_signals[:5]  # First 5 for inspection
        }), 200
    
    @app.route('/api/indicator-inspector/clear', methods=['POST'])
    def clear_inspector():
        """Clear all received signals"""
        global received_signals
        count = len(received_signals)
        received_signals = []
        
        # Clear log file
        try:
            if os.path.exists('indicator_export_log.json'):
                os.remove('indicator_export_log.json')
        except:
            pass
        
        return jsonify({
            'success': True,
            'cleared': count,
            'message': f'Cleared {count} signals from inspector'
        }), 200
    
    @app.route('/api/indicator-inspector/all', methods=['GET'])
    def get_all_inspector_signals():
        """Get all received signals for import"""
        return jsonify({
            'success': True,
            'signals': received_signals,
            'count': len(received_signals)
        }), 200
    
    print("✅ Indicator Inspector endpoints registered")

# Register in web_server.py
if __name__ != "__main__":
    # This will be imported by web_server.py
    pass
