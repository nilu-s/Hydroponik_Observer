#include <Arduino.h>
#include <ArduinoJson.h>
#include <DallasTemperature.h>
#include <OneWire.h>
#include <stdio.h>

static const uint32_t SERIAL_BAUDRATE = 115200;
static const int PH_PIN = 28;   // ADC2 (GPIO28)
static const int EC_PIN = 26;   // ADC0 (GPIO26)
static const int TEMP_PIN = 17; // GPIO17 (OneWire)

static const uint32_t SAMPLE_INTERVAL_MS = 250;
static const uint32_t SMOOTHING_WINDOW_MS = 10000;
static const size_t MAX_SAMPLES = 64;
static const uint32_t HELLO_RETRY_INTERVAL_MS = 1200;
static const uint32_t HELLO_ACK_TIMEOUT_MS = 4000;
static const char *FW_VERSION = "pico-0.1.0";

struct CalibrationPoint {
  float raw;
  float val;
};

struct CalibrationData {
  bool hasPh;
  bool hasEc;
  CalibrationPoint phPoints[3];
  CalibrationPoint ecPoints[2];
  String calibHash;
};

struct Sample {
  uint32_t ts;
  float ph;
  float ec;
  float temp;
};

enum NodeMode { MODE_REAL, MODE_DEBUG };

static NodeMode nodeMode = MODE_REAL;
static CalibrationData calibration;
static Sample samples[MAX_SAMPLES];
static size_t sampleCount = 0;
static size_t sampleIndex = 0;
static uint32_t lastSampleAt = 0;

static float debugPh = 6.2f;
static float debugEc = 1.6f;
static float debugTemp = 21.5f;
static uint32_t lastDebugUpdate = 0;

static OneWire oneWire(TEMP_PIN);
static DallasTemperature tempSensor(&oneWire);

static String inputBuffer;
static uint32_t lastAnnounceAt = 0;
static uint32_t lastHelloAckAt = 0;
static bool nodeConnected = false;

static float clampf(float value, float minVal, float maxVal) {
  if (value < minVal) {
    return minVal;
  }
  if (value > maxVal) {
    return maxVal;
  }
  return value;
}

static float advanceTenths(float value, float minVal, float maxVal) {
  const int minTenths = static_cast<int>(minVal * 10.0f + 0.5f);
  const int maxTenths = static_cast<int>(maxVal * 10.0f + 0.5f);
  int currentTenths = static_cast<int>(value * 10.0f + 0.5f);
  if (currentTenths < minTenths || currentTenths > maxTenths) {
    currentTenths = minTenths;
  }
  int nextTenths = currentTenths + 1;
  if (nextTenths > maxTenths) {
    nextTenths = minTenths;
  }
  return static_cast<float>(nextTenths) / 10.0f;
}

static uint32_t fnv1a(const char *data, size_t len) {
  uint32_t hash = 2166136261u;
  for (size_t i = 0; i < len; i++) {
    hash ^= static_cast<uint8_t>(data[i]);
    hash *= 16777619u;
  }
  return hash;
}

static void setDefaultCalibration() {
  calibration.hasPh = true;
  calibration.hasEc = true;
  calibration.phPoints[0] = {0.0f, 0.0f};
  calibration.phPoints[1] = {1.65f, 7.0f};
  calibration.phPoints[2] = {3.3f, 14.0f};
  calibration.ecPoints[0] = {0.0f, 0.0f};
  calibration.ecPoints[1] = {3.3f, 5.0f};
  calibration.calibHash = "default";
}

static void markConnected() {
  nodeConnected = true;
  lastHelloAckAt = millis();
}

static float applyLinear(const CalibrationPoint &a, const CalibrationPoint &b, float raw) {
  if (fabsf(b.raw - a.raw) < 0.0001f) {
    return a.val;
  }
  const float slope = (b.val - a.val) / (b.raw - a.raw);
  return a.val + slope * (raw - a.raw);
}

static float applyPhCalibration(float raw) {
  const CalibrationPoint &p1 = calibration.phPoints[0];
  const CalibrationPoint &p2 = calibration.phPoints[1];
  const CalibrationPoint &p3 = calibration.phPoints[2];

  if (raw <= p1.raw) {
    return applyLinear(p1, p2, raw);
  }
  if (raw <= p2.raw) {
    return applyLinear(p1, p2, raw);
  }
  if (raw <= p3.raw) {
    return applyLinear(p2, p3, raw);
  }
  return applyLinear(p2, p3, raw);
}

static float applyEcCalibration(float raw) {
  const CalibrationPoint &p1 = calibration.ecPoints[0];
  const CalibrationPoint &p2 = calibration.ecPoints[1];
  return applyLinear(p1, p2, raw);
}

static float readPhRaw() {
  const int raw = analogRead(PH_PIN);
  return (static_cast<float>(raw) / 4095.0f) * 3.3f;
}

static float readEcRaw() {
  const int raw = analogRead(EC_PIN);
  return (static_cast<float>(raw) / 4095.0f) * 3.3f;
}

static float readTempC() {
  tempSensor.requestTemperatures();
  const float tempC = tempSensor.getTempCByIndex(0);
  if (tempC <= -100.0f || tempC >= 150.0f) {
    return 22.0f;
  }
  return tempC;
}

static void addSample(const Sample &sample) {
  samples[sampleIndex] = sample;
  sampleIndex = (sampleIndex + 1) % MAX_SAMPLES;
  if (sampleCount < MAX_SAMPLES) {
    sampleCount++;
  }
}

static Sample computeSmoothed(uint32_t now) {
  float sumPh = 0.0f;
  float sumEc = 0.0f;
  float sumTemp = 0.0f;
  size_t count = 0;
  for (size_t i = 0; i < sampleCount; i++) {
    const Sample &s = samples[i];
    if (now - s.ts <= SMOOTHING_WINDOW_MS) {
      sumPh += s.ph;
      sumEc += s.ec;
      sumTemp += s.temp;
      count++;
    }
  }
  if (count == 0) {
    return {now, 0.0f, 0.0f, 0.0f};
  }
  return {
      now,
      sumPh / static_cast<float>(count),
      sumEc / static_cast<float>(count),
      sumTemp / static_cast<float>(count),
  };
}

static void updateSamples(uint32_t now) {
  if (now - lastSampleAt < SAMPLE_INTERVAL_MS) {
    return;
  }
  lastSampleAt = now;
  const float phRaw = readPhRaw();
  const float ecRaw = readEcRaw();
  const float temp = readTempC();
  const float ph = applyPhCalibration(phRaw);
  const float ec = applyEcCalibration(ecRaw);
  addSample({now, ph, ec, temp});
}

static void resetDebugValues() {
  debugPh = 6.0f + static_cast<float>(random(0, 10)) / 10.0f;
  debugEc = 1.0f + static_cast<float>(random(0, 10)) / 10.0f;
  debugTemp = 20.0f + static_cast<float>(random(0, 10)) / 10.0f;
  lastDebugUpdate = millis();
}

static void updateDebugValues(uint32_t now) {
  if (now - lastDebugUpdate < 5000) {
    return;
  }
  lastDebugUpdate = now;
  debugPh = advanceTenths(debugPh, 6.0f, 6.9f);
  debugEc = advanceTenths(debugEc, 1.0f, 1.9f);
  debugTemp = advanceTenths(debugTemp, 20.0f, 20.9f);
}

static void sendJson(const JsonDocument &doc) {
  serializeJson(doc, Serial);
  Serial.print('\n');
}

static void sendHello(const String &rawLine) {
  StaticJsonDocument<384> response;
  response["t"] = "hello";
  response["raw"] = rawLine;
  response["fw"] = FW_VERSION;
  JsonObject cap = response.createNestedObject("cap");
  cap["ph"] = true;
  cap["ec"] = true;
  cap["temp"] = true;
  cap["debug"] = true;
  cap["calib"] = true;
  JsonObject pins = cap.createNestedObject("pins");
  pins["ph"] = "adc2";
  pins["ec"] = "adc0";
  pins["temp"] = "gpio17";
  response["calibHash"] = calibration.calibHash;
  sendJson(response);
}

static void handleHello(const String &rawLine) {
  StaticJsonDocument<384> response;
  response["t"] = "hello_ack";
  response["raw"] = rawLine;
  response["fw"] = FW_VERSION;
  JsonObject cap = response.createNestedObject("cap");
  cap["ph"] = true;
  cap["ec"] = true;
  cap["temp"] = true;
  cap["debug"] = true;
  cap["calib"] = true;
  JsonObject pins = cap.createNestedObject("pins");
  pins["ph"] = "adc2";
  pins["ec"] = "adc0";
  pins["temp"] = "gpio17";
  response["calibHash"] = calibration.calibHash;
  sendJson(response);
}

static void handleHelloAck() {
  markConnected();
}

static void handleGetAll(const String &rawLine) {
  StaticJsonDocument<384> response;
  response["t"] = "all";
  response["raw"] = rawLine;
  const uint32_t now = millis();
  response["ts"] = now;
  response["mode"] = (nodeMode == MODE_DEBUG) ? "debug" : "real";
  JsonArray status = response.createNestedArray("status");
  status.add("ok");

  if (nodeMode == MODE_DEBUG) {
    updateDebugValues(now);
    response["ph"] = debugPh;
    response["ec"] = debugEc;
    response["temp"] = debugTemp;
    sendJson(response);
    return;
  }

  updateSamples(now);
  const Sample smoothed = computeSmoothed(now);
  response["ph"] = smoothed.ph;
  response["ec"] = smoothed.ec;
  response["temp"] = smoothed.temp;
  sendJson(response);
}

static void handleSetMode(JsonObject payload) {
  const char *mode = payload["mode"];
  if (mode && String(mode) == "debug") {
    nodeMode = MODE_DEBUG;
    resetDebugValues();
    return;
  }
  nodeMode = MODE_REAL;
}

static void handleSetSim(JsonObject payload) {
  if (payload.containsKey("ph")) {
    debugPh = payload["ph"].as<float>();
  }
  if (payload.containsKey("ec")) {
    debugEc = payload["ec"].as<float>();
  }
  if (payload.containsKey("temp")) {
    debugTemp = payload["temp"].as<float>();
  }
}

static void handleSetCalib(JsonObject payload) {
  JsonObject ph = payload["ph"];
  JsonArray phPoints = ph["points"];
  if (!phPoints.isNull() && phPoints.size() >= 3) {
    for (size_t i = 0; i < 3; i++) {
      JsonObject point = phPoints[i];
      calibration.phPoints[i] = {
          point["raw"].as<float>(),
          point["val"].as<float>(),
      };
    }
    calibration.hasPh = true;
  }

  JsonObject ec = payload["ec"];
  JsonArray ecPoints = ec["points"];
  if (!ecPoints.isNull() && ecPoints.size() >= 2) {
    for (size_t i = 0; i < 2; i++) {
      JsonObject point = ecPoints[i];
      calibration.ecPoints[i] = {
          point["raw"].as<float>(),
          point["val"].as<float>(),
      };
    }
    calibration.hasEc = true;
  }

  if (payload.containsKey("calibHash")) {
    calibration.calibHash = payload["calibHash"].as<String>();
  } else {
    String rawPayload;
    serializeJson(payload, rawPayload);
    uint32_t hash = fnv1a(rawPayload.c_str(), rawPayload.length());
    calibration.calibHash = String(hash, HEX);
  }
}

static void handleMessage(const String &line) {
  StaticJsonDocument<512> doc;
  DeserializationError err = deserializeJson(doc, line);
  if (err) {
    StaticJsonDocument<256> response;
    response["t"] = "error";
    response["msg"] = "invalid_json";
    response["raw"] = line;
    sendJson(response);
    return;
  }
  const char *type = doc["t"];
  if (!type) {
    StaticJsonDocument<256> response;
    response["t"] = "unknown";
    response["msg"] = "missing_type";
    response["raw"] = line;
    sendJson(response);
    return;
  }
  markConnected();
  if (String(type) == "hello") {
    handleHello(line);
    return;
  }
  if (String(type) == "hello_ack") {
    handleHelloAck();
    return;
  }
  if (String(type) == "get_all") {
    handleGetAll(line);
    return;
  }
  if (String(type) == "set_mode") {
    handleSetMode(doc.as<JsonObject>());
    return;
  }
  if (String(type) == "set_sim") {
    handleSetSim(doc.as<JsonObject>());
    return;
  }
  if (String(type) == "set_calib") {
    JsonObject payload = doc["payload"].as<JsonObject>();
    if (!payload.isNull()) {
      handleSetCalib(payload);
    }
    StaticJsonDocument<256> response;
    response["t"] = "set_calib_ack";
    response["raw"] = line;
    sendJson(response);
    return;
  }
  StaticJsonDocument<256> response;
  response["t"] = "unknown";
  response["msg"] = "unsupported_type";
  response["raw"] = line;
  sendJson(response);
}

void setup() {
  Serial.begin(SERIAL_BAUDRATE);
  analogReadResolution(12);
  pinMode(PH_PIN, INPUT);
  pinMode(EC_PIN, INPUT);
  tempSensor.begin();
  const uint32_t seed =
      (static_cast<uint32_t>(analogRead(PH_PIN)) << 16) ^
      static_cast<uint32_t>(analogRead(EC_PIN)) ^
      static_cast<uint32_t>(micros());
  randomSeed(seed);
  setDefaultCalibration();
  resetDebugValues();
}

void loop() {
  while (Serial.available() > 0) {
    const char ch = static_cast<char>(Serial.read());
    if (ch == '\n') {
      String line = inputBuffer;
      inputBuffer = "";
      line.trim();
      if (line.length() > 0) {
        handleMessage(line);
      }
    } else if (ch != '\r') {
      inputBuffer += ch;
      if (inputBuffer.length() > 512) {
        inputBuffer = "";
      }
    }
  }

  const uint32_t now = millis();
  if (nodeConnected && now - lastHelloAckAt > HELLO_ACK_TIMEOUT_MS) {
    nodeConnected = false;
  }
  if (!nodeConnected && now - lastAnnounceAt >= HELLO_RETRY_INTERVAL_MS) {
    lastAnnounceAt = now;
    sendHello("probe");
  }

  if (nodeMode == MODE_REAL) {
    updateSamples(now);
  } else {
    updateDebugValues(now);
  }
}