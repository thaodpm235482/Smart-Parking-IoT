import network
import time
import ujson
import urandom
from machine import Pin, SoftI2C, PWM
from i2c_lcd import I2cLcd
from umqtt_simple import MQTTClient

print("--- KHOI DONG NODE 1 ---")

# 1. Khoi tao LCD & Peripherals
i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16)
lcd.clear()
lcd.putstr("Ket noi WiFi...")

servo = PWM(Pin(15), freq=50)
btn = Pin(13, Pin.IN, Pin.PULL_UP)

def set_servo_angle(angle):
    duty = int(40 + (angle / 180.0) * 75)
    servo.duty(duty)

set_servo_angle(0) # Dong barrier ban dau

free_slots = 3 # Mac dinh ban dau trong luc cho dong bo

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

CLIENT_ID = 'node1_gate_hcmut_' + str(urandom.getrandbits(16))
TOPIC_DATA = 'smart_parking_hcmut_2026_final'
TOPIC_REQ = 'smart_parking_hcmut_2026_req'

def update_lcd_status():
    lcd.clear()
    lcd.putstr(f"CHO TRONG: {free_slots}/3\n")
    if free_slots > 0:
        lcd.putstr("XIN MOI VAO!")
    else:
        lcd.putstr("BAI DA DAY!")

def mqtt_callback(topic, msg):
    global free_slots
    try:
        data = ujson.loads(msg.decode('utf-8'))
        free_slots = data.get('f', free_slots)
        print("<- Node 1 nhan cap nhat cho trong:", free_slots)
        update_lcd_status()
    except Exception as e:
        print("Loi doc msg:", e)

def connect_mqtt():
    print("Dang ket noi MQTT Server...")
    client = MQTTClient(CLIENT_ID, MQTT_SERVER, port=1883, keepalive=60)
    client.set_callback(mqtt_callback)
    client.connect()
    client.subscribe(TOPIC_DATA)
    print("Node 1: Da ket noi MQTT thanh cong!")
    
    # GUI YEU CAU DONG BO TRANG THAI NGAY KHI KET NOI
    try:
        client.publish(TOPIC_REQ, "get_status")
        print("-> Node 1: Da gui yeu cau dong bo trang thai toi Node 2")
    except Exception as e:
        print("Loi gui yeu cau dong bo:", e)
        
    return client

client = None
while client is None:
    try:
        client = connect_mqtt()
    except Exception as e:
        print("Loi MQTT, dang thu lai...", e)
        time.sleep(1)

update_lcd_status()

last_btn_state = 1
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
            time.sleep(1)

    # 4. Kiem tra nut bam mo cong
    current_btn = btn.value()
    if current_btn == 0 and last_btn_state == 1:
        if free_slots > 0:
            print("=> [CHO PHEP] Co cho trong! Mo barrier...")
            lcd.clear()
            lcd.putstr("XE DANG VAO...\nMO BARRIER!")
            set_servo_angle(90)  # 1. MO CONG (90 do)
            time.sleep(10)       # 2. CHO XE QUA (10 GIAY)
            set_servo_angle(0)   # 3. DONG CONG (0 do)
            print("=> Barrier da dong sau 10 giay.")
            update_lcd_status()  # 4. CAP NHAT LAI MAN HINH
        else:
            print("=> [TU CHOI] Bai da DAY! Khong the mo barrier.")
            lcd.clear()
            lcd.putstr("BAI DA DAY!\nKHONG THE VAO!")
            time.sleep(2)
            update_lcd_status()
    
    last_btn_state = current_btn
    time.sleep(0.1)
