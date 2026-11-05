import network
import time
import urequests
import ujson
import urandom
from machine import Pin
from umqtt_simple import MQTTClient

# 1. Cau hinh thong so
WIFI_SSID = 'Wokwi-GUEST'
WIFI_PASS = ''
MQTT_SERVER = 'broker.emqx.io'  # Dung emqx on dinh nhat cho Wokwi
MQTT_PORT = 1883
TOPIC_DATA = b'smart_parking_hcmut_2026_final'
TOPIC_REQ = b'smart_parking_hcmut_2026_req'
CLIENT_ID = b'node2_sensor_' + str(urandom.getrandbits(16))

THINGSPEAK_API_KEY = 'JXPT76YXOKG6DRZ3'
THINGSPEAK_URL = 'http://api.thingspeak.com/update'

# 2. Khoi tao cac chan Cam bien
slot1 = Pin(12, Pin.IN, Pin.PULL_UP)
slot2 = Pin(14, Pin.IN, Pin.PULL_UP)
slot3 = Pin(27, Pin.IN, Pin.PULL_UP)

print("--- KHOI DONG NODE 2 ---")

# 3. Ket noi Wi-Fi chuan (Sua loi vong lap cho IP de khong bi -202)
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(WIFI_SSID, WIFI_PASS)

print("Dang cho IP Wi-Fi...", end="")
while not sta_if.isconnected():
    print(".", end="")
    time.sleep(0.5)
print("\nNode 2 Wi-Fi OK! IP:", sta_if.ifconfig()[0])

current_payload = ""

def send_status():
    global current_payload
    if current_payload and client:
        try:
            client.publish(TOPIC_DATA, current_payload)
            print("-> Node 2: Da gui phan hoi dong bo:", current_payload)
        except Exception as e:
            print("Loi gui phan hoi:", e)

def mqtt_callback(topic, msg):
    print("<- Node 2 nhan yeu cau dong bo tu Node 1")
    send_status()

# 4. Ket noi MQTT Broker
def connect_mqtt():
    print("Node 2: Dang ket noi MQTT Server...")
    c = MQTTClient(CLIENT_ID, MQTT_SERVER, port=MQTT_PORT, keepalive=60)
    c.set_callback(mqtt_callback)
    c.connect()
    c.subscribe(TOPIC_REQ)
    print("Node 2: Da ket noi MQTT thanh cong!")
    return c

client = None
while client is None:
    try:
        client = connect_mqtt()
    except Exception as e:
        print("Loi MQTT, dang thu lai...", e)
        time.sleep(2)

last_state = None
last_thingspeak_time = 0

while True:
    try:
        client.check_msg()
    except OSError:
        try:
            client = connect_mqtt()
        except:
            pass

    s1 = 0 if slot1.value() == 0 else 1
    s2 = 0 if slot2.value() == 0 else 1
    s3 = 0 if slot3.value() == 0 else 1
    
    current_state = (s1, s2, s3)
    free_slots = s1 + s2 + s3
    current_time = time.time()

    current_payload = ujson.dumps({
        "s1": s1,
        "s2": s2,
        "s3": s3,
        "f": free_slots
    })

    if current_state != last_state:
        print(f"=> [CAP NHAT] Slot1: {s1}, Slot2: {s2}, Slot3: {s3} | Tong trong: {free_slots}")
        send_status()

        if current_time - last_thingspeak_time >= 15:
            try:
                url = f"{THINGSPEAK_URL}?api_key={THINGSPEAK_API_KEY}&field1={free_slots}&field2={s1}&field3={s2}&field4={s3}"
                res = urequests.get(url)
                print("-> Da gui ThingSpeak, status:", res.status_code)
                res.close()
                last_thingspeak_time = current_time
            except Exception as e:
                print("Loi gui ThingSpeak:", e)

        last_state = current_state

    time.sleep(0.2)
