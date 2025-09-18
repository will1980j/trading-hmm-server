from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.data.decode('utf-8')
    print("📥 Received alert:", payload)
    with open("latest_alert.json", "w") as f:
        f.write(payload)
    return '', 200

if __name__ == '__main__':
    app.run(port=5000)