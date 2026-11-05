import network
import time
import ujson
import urandom
from machine import Pin, SoftI2C
import ssd1306
from umqtt_simple import MQTTClient

print("--- KHOI DONG NODE 3 ---")

i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

oled.fill(0)
oled.text("PARKING SYSTEM", 8, 10)
oled.text("Ket noi WiFi...", 5, 35)
oled.show()

# 2. Ket noi Wi-Fi chuan
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Wokwi-GUEST', '')
print("Dang cho IP...", end="")
while not sta_if.isconnected():
    print(".", end="")
    time.sleep(0.5)
print("\nWi-Fi OK! IP:", sta_if.ifconfig()[0])

# 3. Ket noi MQTT
MQTT_SERVER = 'broker.emqx.io' # Quay lai dung EMQX

CLIENT_ID = 'node3_oled_hcmut_' + str(urandom.getrandbits(16))
TOPIC = 'smart_parking_hcmut_2026_final'

def mqtt_callback(topic, msg):
    try:
        data = ujson.loads(msg.decode('utf-8'))
        s1 = data.get('s1', 1)
        s2 = data.get('s2', 1)
        s3 = data.get('s3', 1)
        
        print(f"<- Node 3 nhan cap nhat: O1={s1}, O2={s2}, O3={s3}")
        
        oled.fill(0)
        oled.text("--- MOI DO XE ---", 0, 0)
        oled.text(f"O 1: {'TRONG' if s1==1 else 'CO XE'}", 0, 16)
        oled.text(f"O 2: {'TRONG' if s2==1 else 'CO XE'}", 0, 32)
        oled.text(f"O 3: {'TRONG' if s3==1 else 'CO XE'}", 0, 48)
        oled.show()
    except Exception as e:
        print("Loi doc msg:", e)

def connect_mqtt():
    print("Dang ket noi MQTT Server...")
    client = MQTTClient(CLIENT_ID, MQTT_SERVER, port=1883, keepalive=60)
    client.set_callback(mqtt_callback)
    client.connect()
    client.subscribe(TOPIC)
    print("Node 3: Da ket noi MQTT thanh cong!")
    return client

client = None
while client is None:
    try:
        client = connect_mqtt()
    except Exception as e:
        print("Loi MQTT, dang thu lai...", e)
        time.sleep(2)

oled.fill(0)
oled.text("--- MOI DO XE ---", 0, 0)
oled.text("O 1: TRONG", 0, 16)
oled.text("O 2: TRONG", 0, 32)
oled.text("O 3: TRONG", 0, 48)
oled.show()

last_ping = time.ticks_ms()

while True:
    try:
        client.check_msg()
        if time.ticks_diff(time.ticks_ms(), last_ping) > 15000:
            client.ping()
            last_ping = time.ticks_ms()
    except OSError:
        try:
            client = connect_mqtt()
        except:
            time.sleep(2)
            
    time.sleep(0.1)