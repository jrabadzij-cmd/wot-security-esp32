# Sigurnosni rizici Weba stvari (WoT): demonstracijski sustav

Praktični dio završnog rada o sigurnosnim rizicima Weba stvari (Web of Things).
Sustav je izgrađen na **Arduino Nano ESP32** mikrokontroleru sa senzorom
temperature (TMP36), a sigurnosni mehanizmi testirani su kroz četiri
kontrolirana scenarija napada, sa i bez aktivne zaštite.

Rad: [\Poveznica na sam rad\]](https://urn.nsk.hr/urn:nbn:hr:211:753952)

## O radu

Web stvari (WoT) nadograđuje Internet stvari (IoT) postojećim web tehnologijama
radi lakše integracije i interoperabilnosti uređaja različitih proizvođača.
Teorijski dio obrađuje arhitekturu IoT sustava, komunikacijske protokole na
svim slojevima, W3C WoT arhitekturu (Thing Description) te sigurnosne rizike
i ključne napade (prisluškivanje, MITM, replay, brute force, DoS/DDoS).

Praktični dio čini demonstracijski sustav s dokumentom opisa stvari (TD) i web
dashboardom za praćenje i upravljanje sigurnosnim mehanizmima.

## Testirani napadi i protumjere

| Scenarij napada        | Protumjera                        |
|------------------------|-----------------------------------|
| Prisluškivanje prometa | TLS/HTTPS enkripcija (proxy)      |
| Lažiranje identiteta   | Bearer token autentifikacija      |
| Ponavljanje zahtjeva   | Jednokratni identifikator (nonce) |
| Uskraćivanje usluge    | Ograničavanje broja zahtjeva      |

Zaključak rada: sigurnost sustava proizlazi iz slojevite primjene više
komplementarnih mehanizama, dok pojedinačni mehanizmi ostaju nedostatni protiv
specifičnih vrsta napada.

## Struktura repozitorija

- `firmware/`: Arduino kod za Nano ESP32
- `server/`: Python (Flask) server, web dashboard (HTML, CSS, JS) i Thing Description
- `proxy/`: HTTPS proxy ispred ESP32 uređaja
- `attacks/`: Python skripte za scenarije napada (samo za edukaciju)

## Pokretanje

Potrebno: Arduino IDE (s podrškom za Nano ESP32), Python 3.10+ i
`pip install flask requests cryptography`.

1. **ESP32:** u `firmware/esp32_nano_tmp36_server/` kopiraj `secrets.example.h`
   u `secrets.h` i upiši WiFi podatke i vlastiti token. Uploadaj sketch na
   uređaj i u Serial Monitoru pročitaj IP adresu uređaja.
2. **Server i dashboard:** u `server/dashboard.html` i `server/thing-description.json`
   zamijeni `ESP32_IP_ADRESA` IP adresom uređaja. Zatim pokreni
   `python td_server.py` i otvori `http://localhost:5000/dashboard`.
3. **Proxy:** u `proxy/` kopiraj `config.example.py` u `config.py`, upiši IP
   uređaja i pokreni `python https_proxy.py`.
4. **Napadi:** u `attacks/` kopiraj `config.example.py` u `config.py`, upiši IP
   uređaja, IP računala sa serverom i isti token kao u `secrets.h`. Pokreni
   npr. `python scenario3_replay_attack.py`.

## Upozorenje

Skripte za napade napisane su isključivo u edukativne svrhe i testirane na
vlastitom sustavu u kontroliranim uvjetima. Ne koristiti protiv tuđih uređaja
ili mreža.
