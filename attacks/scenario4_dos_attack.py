import requests

from config import ESP32_IP, SERVER_IP, VALID_TOKEN

ESP32_URL = f"http://{ESP32_IP}/temperature"
DASHBOARD_LOG_URL = f"http://{SERVER_IP}:5000/log-attack"
NUM_REQUESTS = 20

headers = {"Authorization": f"Bearer {VALID_TOKEN}"}

def log_to_dashboard(attack_type, blocked):
    try:
        requests.post(DASHBOARD_LOG_URL, json={"type": attack_type, "blocked": blocked}, timeout=2)
    except requests.exceptions.RequestException as e:
        print(f"(Napomena: dashboard log nije poslan - {e})")

print(f"=== Simulacija DoS napada: {NUM_REQUESTS} zahtjeva u brzom nizu ===\n")

success_count = 0
blocked_count = 0

for i in range(NUM_REQUESTS):
    try:
        import uuid
        params = {"nonce": str(uuid.uuid4())}
        response = requests.get(ESP32_URL, params=params, headers=headers, timeout=2)
        if response.status_code == 200:
            success_count += 1
            print(f"Zahtjev {i+1}: OK (200) - {response.json()}")
            log_to_dashboard("DoS napad", blocked=False)
        elif response.status_code == 429:
            blocked_count += 1
            print(f"Zahtjev {i+1}: BLOKIRAN (429 Too Many Requests)")
            log_to_dashboard("DoS napad", blocked=True)
        else:
            print(f"Zahtjev {i+1}: Neocekivan status {response.status_code} - {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Zahtjev {i+1}: Greska - {e}")

print(f"\n=== Rezultat ===")
print(f"Uspjesni zahtjevi: {success_count}")
print(f"Blokirani zahtjevi: {blocked_count}")

if blocked_count > 0:
    print("\n[OK] Rate limiting radi - dio zahtjeva je uspjesno blokiran.")
else:
    print("\n[!] Nijedan zahtjev nije blokiran - provjeri je li zastita ukljucena.")
