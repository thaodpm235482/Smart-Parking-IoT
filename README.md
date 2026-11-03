# HỆ THỐNG BÃI ĐỖ XE THÔNG MINH 3 NODE (ESP32 + MQTT + THINGSPEAK)

**Giảng viên hướng dẫn:** ThS. Huỳnh Lý Thanh Nhàn

## 1. Kiến trúc hệ thống
* **Node 1 (Gate):** ESP32 điều khiển Servo mở cổng và xuất thông báo lên LCD 16x2.
* **Node 2 (Sensors):** ESP32 đọc trạng thái 3 ô đỗ, phát dữ liệu qua MQTT (`broker.hivemq.com`) với `retain=True` và đẩy lịch sử lên ThingSpeak (Channel ID: `3563091`).
* **Node 3 (Display):** ESP32 nhận dữ liệu từ MQTT, vẽ sơ đồ bãi đỗ trực quan lên màn hình OLED SSD1306.

## 2. Link Mô phỏng & Video Demo
* **Mô phỏng Node 1:** (https://wokwi.com/projects/479598781372565505)
* **Mô phỏng Node 2:** (https://wokwi.com/projects/479597080971888641)
* **Mô phỏng Node 3:** https://wokwi.com/projects/479597120923694081
* **Video Demo dự án:** [Dán link YouTube vào đây]

## 3. Thành viên thực hiện
1. Lê Thị Ngọc Thảo (MSSV: DPM235482)
2. Nguyễn Thị Kim Ngọc (MSSV: DPM235456)
3. Nguyễn Kim Ngân (MSSV: DPM235452)
4. Bùi Võ Thảo Quyên (MSSV: DPM235472)
5. Đỗ Thị Mỹ An (MSSV: 2)
