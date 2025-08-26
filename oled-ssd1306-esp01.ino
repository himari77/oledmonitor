#include <ESP8266WiFi.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

const char* ssid = "SSID WIFIMU PAK";
const char* password = "PASWORTE LEK";
const char* serverIP = "MAI AIPI ADRES";
const uint16_t serverPort = 8888; //ganti yo boleh, jarno yowes

#define CHUNK_SIZE 64
WiFiClient client;

void connectToWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  display.clearDisplay();
  display.setCursor(0,0);
  display.println("Connecting WiFi...");
  display.display();

  while (WiFi.status() != WL_CONNECTED) delay(50);

  display.clearDisplay();
  display.setCursor(0,0);
  display.println("WiFi connected");
  display.display();
}

void connectToServer() {
  while (!client.connected()) {
    if (client.connect(serverIP, serverPort)) {
      display.clearDisplay();
      display.setCursor(0,0);
      display.println("Connected to server");
      display.display();
    } else {
      delay(500); // ngulang sampe ndasmu kobong
    }
  }
}

void setup() {
  Wire.begin(0, 2); // SDA=0, SCL=2
  Wire.setClock(400000);

  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();
  display.display();

  connectToWiFi();
  connectToServer();
}

void loop() {
  if (!client.connected()) {
    display.clearDisplay();
    display.setCursor(0,0);
    display.println("Reconnecting...");
    display.display();
    connectToServer();
  }

  uint8_t buf[1024];
  size_t got = 0;

  while (got < sizeof(buf) && client.connected()) {
    if (client.available()) {
      size_t remaining = sizeof(buf) - got;
      size_t toRead = (CHUNK_SIZE < remaining) ? CHUNK_SIZE : remaining;
      int r = client.read(buf + got, (int)toRead);
      if (r > 0) got += r;
      else if (r == 0) break; // server protol xixixi
    }
  }

  if (got == sizeof(buf)) {
    memcpy(display.getBuffer(), buf, sizeof(buf));
    display.display();
    client.write(0x01); // ACK anjeng
  }
}
