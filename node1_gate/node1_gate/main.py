import network
import time
import ujson
from machine import Pin, PWM, SoftI2C
from umqtt_simple import MQTTClient

# ==========================================
# 1. THƯ VIỆN NỘI BỘ: LCD I2C DRIVER
# ==========================================
class I2cLcd:
    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        time.sleep_ms(20)
        self._write_init_nibble(0x03)
        time.sleep_ms(5)
        self._write_init_nibble(0x03)
        time.sleep_ms(1)
        self._write_init_nibble(0x03)
        self._write_init_nibble(0x02)
        self.hal_write_command(0x28)
        self.hal_write_command(0x0C)
        self.hal_write_command(0x06)
        self.clear()

    def _write_init_nibble(self, nibble):
        byte = (nibble << 4) | 0x08
        self.i2c.writeto(self.i2c_addr, bytes([byte | 0x04, byte]))

    def hal_write_command(self, cmd):
        high = cmd & 0xF0
        low = (cmd << 4) & 0xF0
        self.i2c.writeto(self.i2c_addr, bytes([high | 0x0C, high | 0x08]))
        self.i2c.writeto(self.i2c_addr, bytes([low | 0x0C, low | 0x08]))

    def hal_write_data(self, data):
        high = data & 0xF0
        low = (data << 4) & 0xF0
        self.i2c.writeto(self.i2c_addr, bytes([high | 0x0D, high | 0x09]))
        self.i2c.writeto(self.i2c_addr, bytes([low | 0x0D, low | 0x09]))

    def clear(self):
        self.hal_write_command(0x01)
        time.sleep_ms(2)

    def putstr(self, string):
        for char in string:
            if char == '\n':
                self.hal_write_command(0xC0)
            else:
                self.hal_write_data(ord(char))

# ==========================================
# 2. KHỞI TẠO VÀ CẤU HÌNH PHẦN CỨNG
# ==========================================
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Wokwi-GUEST', '')
while not sta_if.isconnected():
    time.sleep(0.1)
print("Project 1: Wi-Fi OK!")

ir_sensor = Pin(13, Pin.IN, Pin.PULL_UP)

servo = PWM(Pin(15), freq=50)
def set_servo_angle(angle):
    min_duty = 26
    max_duty = 122
    duty = min_duty + int((angle / 180) * (max_duty - min_duty))
    servo.duty(duty)

set_servo_angle(0)

i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=100000)
lcd = I2cLcd(i2c, 0x27, 2, 16)
lcd.clear()
lcd.putstr("KHOI DONG...")

# CẤU HÌNH THÔNG SỐ MQTT
MQTT_SERVER = 'broker.hivemq.com'
# Dùng ID độc nhất theo thời gian thực để tránh trùng lặp làm ngắt kết nối
CLIENT_ID = 'esp32_gate_phong_node1_' + str(time.ticks_ms())
TOPIC = 'smart_parking_wokwi_final_999'

slots_free = 3

def update_lcd():
    lcd.clear()
    if slots_free > 0:
        lcd.putstr("CON TRONG: {}/3\nCHO VAO: OK".format(slots_free))
    else:
        lcd.putstr("CON TRONG: 0/3\nBAI XE: HET CHO")

def mqtt_callback(topic, msg):
    global slots_free
    try:
        data = ujson.loads(msg.decode('utf-8'))
        slots_free = data.get('f', 0)
        print("<- Project 1 nhận chỗ trống:", slots_free)
        update_lcd()
    except Exception as e:
        print("Lỗi đọc gói tin:", e)

# Hàm hỗ trợ tự kết nối lại khi rớt mạng
def connect_mqtt():
    client = MQTTClient(CLIENT_ID, MQTT_SERVER, keepalive=60)
    client.set_callback(mqtt_callback)
    client.connect()
    client.subscribe(TOPIC)
    print("Project 1: Đã kết nối MQTT Broker thành công!")
    return client

client = None
while client is None:
    try:
        client = connect_mqtt()
    except Exception as e:
        print("Lỗi kết nối MQTT, đang thử lại...", e)
        time.sleep(2)

update_lcd()
last_ir_state = 1
last_ping = time.ticks_ms()

# ==========================================
# 3. VÒNG LẶP CHÍNH VỚI KHẢ NĂNG TỰ KHÔI PHỤC
# ==========================================
while True:
    try:
        # Kiểm tra tin nhắn MQTT liên tục
        client.check_msg()
        
        # Ping broker định kỳ mỗi 15 giây để duy trì kết nối (Heartbeat)
        if time.ticks_diff(time.ticks_ms(), last_ping) > 15000:
            client.ping()
            last_ping = time.ticks_ms()
            
    except OSError as e:
        print("Phát hiện mất kết nối MQTT, đang kết nối lại...", e)
        try:
            client = connect_mqtt()
            update_lcd()
        except:
            time.sleep(2)
            continue

    current_ir_state = ir_sensor.value()
    
    # Khi xe bấm nút mở cổng
    if current_ir_state == 0 and last_ir_state == 1:
        if slots_free > 0:
            lcd.clear()
            lcd.putstr("XIN MOI VAO...\nMO BARRIER")
            set_servo_angle(90)
            
            # Chia nhỏ thời gian chờ và duy trì check_msg() để không bị rớt mạng trong lúc chờ 5s
            for _ in range(50):
                try:
                    client.check_msg()
                except:
                    pass
                time.sleep(0.1)
            
            lcd.clear()
            lcd.putstr("DANG DONG CONG...")
            set_servo_angle(0)
            time.sleep(1)
            update_lcd()
        else:
            lcd.clear()
            lcd.putstr("HET CHO!\nKHONG THE MO")
            time.sleep(2)
            update_lcd()
            
    last_ir_state = current_ir_state
    time.sleep(0.1)
