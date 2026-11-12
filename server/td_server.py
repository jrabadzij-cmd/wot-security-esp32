from flask import Flask, jsonify, send_file, request
import json
from datetime import datetime

app = Flask(__name__)

TD_FILE = "thing-description.json"

attack_log = []

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/td', methods=['GET'])
def get_thing_description():
    with open(TD_FILE, 'r', encoding='utf-8') as f:
        td = json.load(f)
    return jsonify(td)

@app.route('/dashboard', methods=['GET'])
def dashboard():
    return send_file('dashboard.html')

@app.route('/log-attack', methods=['POST', 'OPTIONS'])
def log_attack():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.get_json()
    entry = {
        'time': datetime.now().strftime('%H:%M:%S'),
        'type': data.get('type', 'Nepoznat napad'),
        'blocked': data.get('blocked', False)
    }
    attack_log.insert(0, entry)  
    
  
    if len(attack_log) > 50:
        attack_log.pop()
    
    print(f"[LOG] {entry['type']} - {'BLOKIRAN' if entry['blocked'] else 'USPIO'}")
    return jsonify({"status": "logged"}), 200

@app.route('/attack-log', methods=['GET'])
def get_attack_log():
    return jsonify(attack_log)

@app.route('/', methods=['GET'])
def index():
    return """
    <h1>WoT Server - Thing Description</h1>
    <p>Thing Description dostupan na: <a href="/td">/td</a></p>
    <p>Dashboard dostupan na: <a href="/dashboard">/dashboard</a></p>
    """

if __name__ == '__main__':
    print("WoT TD server pokrenut na http://localhost:5000")
    print("Thing Description dostupan na http://localhost:5000/td")
    print("Dashboard dostupan na http://localhost:5000/dashboard")
    app.run(host='0.0.0.0', port=5000, debug=False)