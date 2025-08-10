# Trade Manager Security & Performance Fixes

# 1. Add missing authorization to web_server.py
@app.route('/api/trades')
@login_required  # ADD THIS
def get_trades():
    # existing code...

@app.route('/api/prop-firms')
@login_required  # ADD THIS  
def get_prop_firms():
    # existing code...

# 2. Fix error handling in serve_files function
@app.route('/<path:filename>')
def serve_files(filename):
    try:
        if filename.endswith(('.jpg', '.png', '.gif', '.ico', '.pdf')):
            return send_from_directory('.', filename)
        return "File not found", 404
    except (IOError, OSError) as e:
        logger.error(f"File access error: {str(e)}")
        return "File access error", 500

# 3. Improve input validation in authenticate function
def authenticate(username, password):
    if not username or not password:
        return False
    if not isinstance(username, str) or not isinstance(password, str):
        return False
    # existing validation logic...

# 4. Fix broad exception handling
try:
    # specific operations
    pass
except OpenAIError as e:
    logger.error(f"OpenAI API error: {e}")
    return jsonify({"error": "AI service unavailable"}), 503
except ConnectionError as e:
    logger.error(f"Connection error: {e}")
    return jsonify({"error": "Connection failed"}), 502
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return jsonify({"error": "Internal server error"}), 500