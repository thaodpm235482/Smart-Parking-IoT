# HỆ THỐNG BÃI ĐỖ XE THÔNG MINH 3 NODE (ESP32 + MQTT + THINGSPEAK)

Giảng viên hướng dẫn:** ThS. Huỳnh Lý Thanh Nhàn

 1. Kiến trúc hệ thống
Hệ thống mô phỏng bãi đỗ xe thông minh bao gồm 3 Node hoạt động độc lập, giao tiếp đồng bộ với nhau qua giao thức MQTT (`broker.hivemq.com`) và lưu trữ dữ liệu đám mây:

**Node 1 (Gate - Cổng ra vào):** Sử dụng ESP32 để điều khiển Servo đóng/mở barrier dựa trên số lượng chỗ trống hiện tại. Trạng thái bãi đỗ (SỐ CHỖ TRỐNG / BÃI ĐÃ ĐẦY) được hiển thị trực tiếp lên màn hình LCD 16x2. Node có nút nhấn để xe yêu cầu mở cổng.
**Node 2 (Sensors - Cảm biến):** Sử dụng ESP32 đọc trạng thái từ 3 cảm biến (đại diện cho 3 ô đỗ xe). Khi có sự thay đổi, Node 2 phát dữ liệu đồng bộ qua MQTT và tự động đẩy lịch sử số lượng xe lên ThingSpeak (Channel ID: `3563091`).
**Node 3 (Display - Bảng điện tử):** Sử dụng ESP32 nhận dữ liệu từ MQTT để vẽ sơ đồ bãi đỗ trực quan, cập nhật liên tục trạng thái từng ô đỗ (TRỐNG/CÓ XE) lên màn hình OLED SSD1306.

## 2. Link Mô phỏng & Video Demo
* **Mô phỏng Node 1 (Gate):** [Nhấn vào đây để xem trên Wokwi](https://wokwi.com/projects/479829069849204737)
* **Mô phỏng Node 2 (Sensors):** [Nhấn vào đây để xem trên Wokwi](https://wokwi.com/projects/479829087316388865)
* **Mô phỏng Node 3 (Display):** [Nhấn vào đây để xem trên Wokwi](https://wokwi.com/projects/479829111901312001)
* **Video Demo hoạt động:** [👉 Dán link YouTube hoặc Google Drive của nhóm vào đây]

> *Ghi chú: Thay đoạn link video ở trên bằng đường dẫn thực tế của nhóm.*

---

## 3. Hướng dẫn chạy mô phỏng trên Wokwi
Để hệ thống hoạt động đồng bộ và không bị lỗi kết nối mạng, vui lòng thực hiện theo đúng thứ tự sau:
1. Mở song song 3 đường link mô phỏng ở 3 tab trình duyệt khác nhau.
2. Nhấn nút **Play** ở **Node 2** và **Node 3** trước. Đợi khoảng 2-3 giây để màn hình Console (khung màu đen) báo `Wi-Fi OK!` và MQTT kết nối thành công.
3. Cuối cùng, nhấn nút **Play** ở **Node 1**. Node 1 sẽ tự động gửi tín hiệu để đồng bộ dữ liệu chỗ trống thực tế từ Node 2.
4. Thử thay đổi trạng thái cảm biến (gạt các nút bấm) ở Node 2 và quan sát sự thay đổi đồng thời trên màn hình OLED (Node 3) và LCD (Node 1). Nhấn nút ở Node 1 để kiểm tra tính năng tự động đóng/mở barrier.


## 4. Thành viên thực hiện
| STT | Họ và Tên | Mã số sinh viên (MSSV) |
| 1 | Lê Thị Ngọc Thảo | DPM235482 |
| 2 | Nguyễn Thị Kim Ngọc | DPM235456 |
| 3 | Nguyễn Kim Ngân | DPM235452 |
| 4 | Bùi Võ Thảo Quyên | DPM235472 |
| 5 | Đỗ Thị Mỹ An | DPM235401 |
