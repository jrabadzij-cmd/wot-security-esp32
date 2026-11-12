#include <WiFi.h>
#include <WebServer.h>
#include "secrets.h"

const char *ssid = WIFI_SSID;
const char *password = WIFI_PASSWORD;
const char *VALID_TOKEN = API_TOKEN;

const int TMP36_PIN = A1;
WebServer server(80);

bool authEnabled = true;
bool nonceProtectionEnabled = true;
bool rateLimitEnabled = true;

const int MAX_NONCES = 10;
String usedNonces[MAX_NONCES];
int nonceIndex = 0;

const int MAX_REQUESTS_PER_WINDOW = 5;
const unsigned long WINDOW_MS = 1000;
unsigned long windowStart = 0;
int requestCount = 0;

bool checkRateLimit()
{
  if (!rateLimitEnabled)
    return true;
  unsigned long now = millis();
  if (now - windowStart >= WINDOW_MS)
  {
    windowStart = now;
    requestCount = 0;
  }
  requestCount++;
  return requestCount <= MAX_REQUESTS_PER_WINDOW;
}

bool isNonceUsed(String nonce)
{
  for (int i = 0; i < MAX_NONCES; i++)
  {
    if (usedNonces[i] == nonce)
      return true;
  }
  return false;
}

void storeNonce(String nonce)
{
  usedNonces[nonceIndex] = nonce;
  nonceIndex = (nonceIndex + 1) % MAX_NONCES;
}

float readTemperature()
{
  int rawValue = analogRead(TMP36_PIN);
  float voltage = rawValue * (3.3 / 4095.0);
  return (voltage - 0.5) * 100.0;
}

bool isAuthorized()
{
  if (!authEnabled)
    return true;
  if (!server.hasHeader("Authorization"))
    return false;
  String authHeader = server.header("Authorization");
  String expectedHeader = "Bearer " + String(VALID_TOKEN);
  return authHeader.equals(expectedHeader);
}

void handleTemperature()
{
  server.sendHeader("Access-Control-Allow-Origin", "*");

  if (!isAuthorized())
  {
    server.send(401, "application/json", "{\"error\": \"Unauthorized\"}");
    Serial.println("[BLOKIRANO] Bez tokena.");
    return;
  }

  if (nonceProtectionEnabled)
  {
    if (!server.hasArg("nonce"))
    {
      server.send(400, "application/json", "{\"error\": \"Missing nonce parameter\"}");
      Serial.println("[BLOKIRANO] Bez nonce.");
      return;
    }
    String nonce = server.arg("nonce");
    if (isNonceUsed(nonce))
    {
      server.send(403, "application/json", "{\"error\": \"Replay detected\"}");
      Serial.println("[BLOKIRANO] Replay!");
      return;
    }
    storeNonce(nonce);
  }

  if (!checkRateLimit())
  {
    server.send(429, "application/json", "{\"error\": \"Too Many Requests\"}");
    Serial.println("[BLOKIRANO] Rate limit.");
    return;
  }

  float temp = readTemperature();
  String json = "{\"temperature\": " + String(temp, 2) + ", \"unit\": \"celsius\"}";
  server.send(200, "application/json", json);
  Serial.println("[OK] Temperatura: " + String(temp, 2) + " C");
}

void handleToggle()
{
  server.sendHeader("Access-Control-Allow-Origin", "*");

  if (!server.hasArg("protection") || !server.hasArg("state"))
  {
    server.send(400, "application/json", "{\"error\": \"Missing parameters\"}");
    return;
  }

  String protection = server.arg("protection");
  bool state = server.arg("state") == "true";

  if (protection == "auth")
  {
    authEnabled = state;
  }
  else if (protection == "nonce")
  {
    nonceProtectionEnabled = state;
  }
  else if (protection == "ratelimit")
  {
    rateLimitEnabled = state;
  }
  else
  {
    server.send(400, "application/json", "{\"error\": \"Unknown protection type\"}");
    return;
  }

  Serial.println("[TOGGLE] " + protection + " = " + String(state ? "ON" : "OFF"));
  server.send(200, "application/json", "{\"status\": \"ok\", \"protection\": \"" + protection + "\", \"state\": " + String(state ? "true" : "false") + "}");
}

void handleStatus()
{
  server.sendHeader("Access-Control-Allow-Origin", "*");
  String json = "{\"auth\": " + String(authEnabled ? "true" : "false") +
                ", \"nonce\": " + String(nonceProtectionEnabled ? "true" : "false") +
                ", \"ratelimit\": " + String(rateLimitEnabled ? "true" : "false") + "}";
  server.send(200, "application/json", json);
}

void handleRoot()
{
  server.send(200, "text/html", "<h1>ESP32 WoT Thing</h1>");
}

void setup()
{
  Serial.begin(115200);
  delay(1000);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi spojen!");
  Serial.print("IP adresa uredaja: ");
  Serial.println(WiFi.localIP());

  server.on("/", handleRoot);
  server.on("/temperature", handleTemperature);
  server.on("/toggle", handleToggle);
  server.on("/status", handleStatus);
  server.begin();
  Serial.println("HTTP server pokrenut sa svim zastitama i toggle funkcionalnoscu.");
}

void loop()
{
  server.handleClient();
}
