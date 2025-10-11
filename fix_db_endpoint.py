@app.route('/fix-ai-table')
def fix_ai_table():
    try:
        cursor = db.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_conversation_history (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversation_session 
            ON ai_conversation_history(session_id, timestamp)
        """)
        db.conn.commit()
        return "AI table created successfully"
    except Exception as e:
        return f"Error: {str(e)}"