import requests
import uuid

from config import ESP32_IP, SERVER_IP, VALID_TOKEN

ESP32_URL = f"http://{ESP32_IP}/temperature"
DASHBOARD_LOG_URL = f"http://{SERVER_IP}:5000/log-attack"

headers = {"Authorization": f"Bearer {VALID_TOKEN}"}

def log_to_dashboard(attack_type, blocked):
    try:
        requests.post(DASHBOARD_LOG_URL, json={"type": attack_type, "blocked": blocked}, timeout=2)
    except requests.exceptions.RequestException as e:
        print(f"(Napomena: dashboard log nije poslan - {e})")


legitimate_nonce = str(uuid.uuid4())

print("=== Korak 1: Legitiman zahtjev (originalni korisnik) ===")
print(f"Nonce: {legitimate_nonce}")
response = requests.get(ESP32_URL, params={"nonce": legitimate_nonce}, headers=headers, timeout=5)
print(f"Status kod: {response.status_code}")
print(f"Odgovor: {response.json()}")
log_to_dashboard("Legitiman zahtjev (nonce)", blocked=False)

print("\n=== Korak 2: Napadac presrece i PONOVNO salje ISTI zahtjev (replay) ===")
print(f"Ponovno koristen nonce: {legitimate_nonce}")
response = requests.get(ESP32_URL, params={"nonce": legitimate_nonce}, headers=headers, timeout=5)
print(f"Status kod: {response.status_code}")
print(f"Odgovor: {response.json()}")

blocked = response.status_code == 403
log_to_dashboard("Replay napad", blocked=blocked)

if response.status_code == 403:
    print("\n[OK] Replay napad uspjesno blokiran!")
else:
    print("\n[!] Replay napad USPIO - zastita nije aktivna ili ne radi.")
