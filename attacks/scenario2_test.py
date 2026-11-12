import requests

from config import ESP32_IP, SERVER_IP, VALID_TOKEN

ESP32_URL = f"http://{ESP32_IP}/temperature"
DASHBOARD_LOG_URL = f"http://{SERVER_IP}:5000/log-attack"

def log_to_dashboard(attack_type, blocked):
   
    try:
        requests.post(DASHBOARD_LOG_URL, json={"type": attack_type, "blocked": blocked}, timeout=2)
    except requests.exceptions.RequestException as e:
        print(f"(Napomena: dashboard log nije poslan - {e})")

print("=== Test 1: Zahtjev BEZ tokena (napadac/spoofing) ===")
response = requests.get(ESP32_URL, timeout=5)
print(f"Status kod: {response.status_code}")
print(f"Odgovor: {response.json()}")
blocked = response.status_code == 401
log_to_dashboard("Spoofing napad (bez tokena)", blocked=blocked)

print("\n=== Test 2: Zahtjev S ispravnim tokenom (legitiman korisnik) ===")
headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
response = requests.get(ESP32_URL, headers=headers, timeout=5)
print(f"Status kod: {response.status_code}")
print(f"Odgovor: {response.json()}")
log_to_dashboard("Legitiman pristup (s tokenom)", blocked=False)

print("\n=== Test 3: Zahtjev s POGRESNIM tokenom (spoofing pokusaj) ===")
headers = {"Authorization": "Bearer krivi-token"}
response = requests.get(ESP32_URL, headers=headers, timeout=5)
print(f"Status kod: {response.status_code}")
print(f"Odgovor: {response.json()}")
blocked = response.status_code == 401
log_to_dashboard("Spoofing napad (krivi token)", blocked=blocked)

print("\n=== Sazetak ===")
print("Test 1 (bez tokena): " + ("BLOKIRAN ispravno" if response.status_code == 401 else "PROSAO - provjeri zastitu!"))
