from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

from config import ESP32_URL

@app.route('/temperature', methods=['GET'])
def proxy_temperature():
    try:
        params = request.args.to_dict()
        headers = {"Authorization": request.headers.get("Authorization", "")}
        
        response = requests.get(f"{ESP32_URL}/temperature", params=params, headers=headers, timeout=5)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Ne mogu dohvatiti podatke s ESP32: {str(e)}"}), 502

@app.route('/', methods=['GET'])
def index():
    return "<h1>HTTPS Proxy za ESP32 WoT uredaj</h1><p>Endpoint: <a href='/temperature'>/temperature</a></p>"

if __name__ == '__main__':
    print("HTTPS Proxy pokrenut na https://0.0.0.0:5443")
    print(f"Prosljeduje zahtjeve prema: {ESP32_URL}")
    
    app.run(host='0.0.0.0', port=5443, ssl_context='adhoc', debug=False)
