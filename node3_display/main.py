import network
import time
import ujson
from machine import I2C, Pin
import ssd1306
from umqtt_simple import MQTTClient

# Cấu hình Wi-Fi
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Wokwi-GUEST', '')
while not sta_if.isconnected():
    time.sleep(0.1)
print("Project 3: Wi-Fi OK!")

# Khởi tạo OLED
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Thông số MQTT khớp với Project 2
MQTT_SERVER = 'broker.hivemq.com'
CLIENT_ID = 'esp32_oled_receiver_2026_pro'
TOPIC = 'smart_parking_wokwi_final_999'

def mqtt_callback(topic, msg):
    print("<- Nhận:", msg)
    try:
        data = ujson.loads(msg.decode('utf-8'))
        
        # Dịch số thành chữ không dấu để OLED hiển thị mượt mà nhất
        txt_1 = "CO XE" if data.get('s1') == 1 else "TRONG"
        txt_2 = "CO XE" if data.get('s2') == 1 else "TRONG"
        txt_3 = "CO XE" if data.get('s3') == 1 else "TRONG"
        trong = data.get('f', 0)
        
        # In ra màn hình dễ đọc
        oled.fill(0)
        oled.text("-- BAI DO XE --", 8, 0)
        oled.text(f"Vi tri 1: {txt_1}", 0, 16)
        oled.text(f"Vi tri 2: {txt_2}", 0, 28)
        oled.text(f"Vi tri 3: {txt_3}", 0, 40)
        oled.text(f"Cho trong: {trong}/3", 0, 56)
        oled.show()
    except Exception as e:
        print("Lỗi giải mã:", e)

# Kết nối MQTT với vòng lặp thử lại
client = MQTTClient(CLIENT_ID, MQTT_SERVER)
client.set_callback(mqtt_callback)

connected = False
while not connected:
    try:
        client.connect()
        connected = True
        print("Project 3: Đã kết nối MQTT!")
    except:
        print("Đang thử kết nối lại MQTT...")
        time.sleep(2)

client.subscribe(TOPIC)

oled.fill(0)
oled.text("DANG KET NOI...", 8, 25)
oled.show()

while True:
    try:
        client.check_msg()
    except:
        pass
    time.sleep(0.1)
