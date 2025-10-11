-- Create missing AI conversation history table on Railway
CREATE TABLE IF NOT EXISTS ai_conversation_history (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_conversation_session 
ON ai_conversation_history(session_id, timestamp);