from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from os import environ

app = Flask(__name__)
app.secret_key = environ.get('SECRET_KEY', 'dev-key-change-in-production')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

@app.route('/')
def home():
    return "Server is running!"

if __name__ == '__main__':
    port = int(environ.get('PORT', 8080))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)