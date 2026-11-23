# TVS - ExamGuard AI — Demo 1.1

**Trình diễn video mô phỏng đã xử lý YOLO ONNX và phát lại cảnh báo H.15 tại 4,067 giây. Không phải phát hiện rời ghế thời gian thực.**

## 1. Bổ sung video bắt buộc trước khi chạy

Từ máy Windows đang chạy Demo 1.1, sao chép **`V15_8s_alert_v2_web.mp4`** vào **cùng thư mục với `app.py`**. Nếu bản tiếng Việt v2 chưa có, có thể dùng `V15_8s_alert_web.mp4` (bản cảnh báo tiếng Anh đã kiểm thử). Video này không có trong ZIP vì chưa được cung cấp dưới dạng tệp cho lần đóng gói này. Không tự thay thế bằng một video khác không có cảnh báo.

Nếu có, chép thư mục ảnh H.15 `evidence/` (các JPG gốc) vào cùng thư mục. Không chỉnh sửa dữ liệu/ảnh nghiên cứu.

## 2. Chạy trên Windows

```bat
cd /d D:\KHKT\ExamGuard_AI_2_0A
.venv_demo\Scripts\activate
python -m pip install -r TVS_ExamGuard_Web_Deploy\requirements.txt
python -m streamlit run TVS_ExamGuard_Web_Deploy\app.py
```

Mở http://localhost:8501. Trước 4,067 giây: `16 | 00 | —`; sau mốc: `16 | 01 | G06`, cảnh báo đỏ đồng bộ trong video và bên cạnh. Khi kéo về đầu, chỉ số trở về `00 | —`.

## 3. GitHub + Streamlit Community Cloud

1. Tạo repository GitHub riêng hoặc công khai theo quy định dự án. Tải lên **toàn bộ nội dung** thư mục này (không tải cả môi trường `.venv`).
2. **Nhớ tải thêm video H.264** vào gốc repo cùng `app.py`. Kiểm tra dung lượng và quyền sử dụng video. Không tải video người thật khi chưa có quyền đồng ý.
3. Vào https://share.streamlit.io, kết nối GitHub và chọn repository / nhánh, đặt **Main file path: `app.py`**, triển khai.
4. Mở URL ứng dụng được cấp, thử nút Play, cảnh báo G06, chuyển tab nghiên cứu, tải CSV gốc. Nếu trang báo thiếu video, kiểm tra tên tệp và chữ hoa/thường.

**Lưu ý:** GitHub lưu mã nguồn; Streamlit Community Cloud chạy app. Ứng dụng cần truy cập Internet khi triển khai công khai. Với video nhúng dạng base64, chỉ nên dùng clip ngắn dung lượng vừa phải; nếu lớn hơn, cần phương án lưu trữ tệp khác.

## 4. Dữ liệu và tính trung thực

- `H15_event_audit.csv` là **dữ liệu H.15 gốc, đầy đủ 9 phép đo ROI** cho 3 tín hiệu G06, G10, G15, không phải bảng rút gọn.
- Bảng tổng hợp 3 sự kiện được tính trong ứng dụng, **không ghi đè CSV gốc**.
- Chế độ trình diễn chọn **1 tình huống G06**; G10 và G15 vẫn còn nguyên trong tab nghiên cứu, không bị xóa.
- Không khẳng định hệ thống tự động xác nhận 3 học sinh rời ghế, giám sát trực tiếp hay phát hiện gian lận.
- **Chưa có mã nguồn đầy đủ của tất cả thử nghiệm H1–H16 trong gói này.** Để nộp hồ sơ khoa học đầy đủ, lưu riêng các mã nguồn gốc từ máy nghiên cứu và minh chứng theo mẫu Sở.

## 5. Cấu trúc

```
app.py
requirements.txt
.streamlit/config.toml
H15_event_audit.csv
V15_8s_alert_v2_web.mp4  <-- sao chép thêm từ máy thầy
evidence/                 <-- sao chép thêm ảnh H.15 gốc nếu có
README.md
.gitignore
```

## 6. Mã nguồn nghiên cứu kèm theo

`research_source/examguard_alert_2_0H15.py` là **bản mã nguồn H.15 đã cung cấp trước đây**, lưu riêng để đối chiếu. Đây chỉ là một phần của chuỗi nghiên cứu, không phải toàn bộ mã nguồn H1–H16. Việc triển khai ứng dụng không tự chạy H.15; chỉ đọc kết quả CSV đã tính trước.
