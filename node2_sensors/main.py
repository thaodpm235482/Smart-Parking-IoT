import network
import time
import ujson
import urequests
from machine import Pin
from umqtt_simple import MQTTClient

# ==========================================
# 1. KẾT NỐI WI-FI WOKWI
# ==========================================
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Wokwi-GUEST', '')
while not sta_if.isconnected():
    time.sleep(0.1)
print("Project 2: Wi-Fi OK!")

# ==========================================
# 2. CẤU HÌNH CẢM BIẾN Ô ĐỖ
# ==========================================
slot1 = Pin(12, Pin.IN, Pin.PULL_UP)
slot2 = Pin(14, Pin.IN, Pin.PULL_UP)
slot3 = Pin(27, Pin.IN, Pin.PULL_UP)

# ==========================================
# 3. THÔNG SỐ MQTT VÀ THINGSPEAK
# ==========================================
MQTT_SERVER = 'broker.hivemq.com'
CLIENT_ID = 'esp32_sensor_sender_2026_pro'
TOPIC = 'smart_parking_wokwi_final_999'

THINGSPEAK_API_KEY = 'JXPT76YXOKG6DRZ3'
THINGSPEAK_URL = 'http://api.thingspeak.com/update'

def connect_mqtt():
    client = MQTTClient(CLIENT_ID, MQTT_SERVER, keepalive=60)
    client.connect()
    print("Project 2: Đã kết nối MQTT Broker thành công!")
    return client

client = None
while client is None:
    try:
        client = connect_mqtt()
    except Exception as e:
        print("Lỗi kết nối MQTT, đang thử lại...", e)
        time.sleep(2)

def send_to_thingspeak(s1, s2, s3, free):
    try:
        url = f"{THINGSPEAK_URL}?api_key={THINGSPEAK_API_KEY}&field1={s1}&field2={s2}&field3={s3}&field4={free}"
        res = urequests.get(url)
        print("-> [ThingSpeak] Đã đẩy dữ liệu thành công (Status Code:", res.status_code, ")")
        res.close()
    except Exception as e:
        print("Lỗi gửi ThingSpeak:", e)

last_state = ""
last_thingspeak_time = 0

# ==========================================
# 4. VÒNG LẶP CHÍNH
# ==========================================
while True:
    # 1: Có xe (kéo xuống GND), 0: Trống
    s1_val = 1 if slot1.value() == 0 else 0
    s2_val = 1 if slot2.value() == 0 else 0
    s3_val = 1 if slot3.value() == 0 else 0
    
    # Tính số chỗ còn trống
    free_slots = 3 - (s1_val + s2_val + s3_val)

    payload = {
        "s1": s1_val,
        "s2": s2_val,
        "s3": s3_val,
        "f": free_slots
    }
    current_state = ujson.dumps(payload)

    # Đẩy MQTT tức thì cho Project 1 & 3 ngay khi thay đổi ô đỗ
    if current_state != last_state:
        try:
            client.publish(TOPIC, current_state, retain=True)
            print("=> [MQTT] Đã phát tín hiệu:", current_state)
            last_state = current_state
        except Exception as e:
            print("Lỗi mất kết nối MQTT, đang kết nối lại...")
            try:
                client = connect_mqtt()
            except:
                pass

    # Đẩy dữ liệu lên ThingSpeak định kỳ 15 giây/lần
    if time.time() - last_thingspeak_time >= 15:
        send_to_thingspeak(s1_val, s2_val, s3_val, free_slots)
        last_thingspeak_time = time.time()

    time.sleep(0.5)
