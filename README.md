# Detect People

Ứng dụng web dùng **Flask** để phát hiện và đếm đối tượng trong ảnh, video tải lên và luồng webcam thời gian thực. Dự án sử dụng mô hình **YOLO** để nhận diện đối tượng; phần tạo mô tả ảnh dùng **ResNet-50** trích xuất đặc trưng kết hợp **LSTM** sinh câu mô tả.

## Tính năng

- Phát hiện đối tượng trong ảnh và trả về ảnh đã được đánh dấu cùng số lượng từng loại đối tượng.
- Phát hiện đối tượng trong video tải lên và xuất video kết quả.
- Xử lý webcam trực tiếp, hiển thị khung nhận diện, đếm đối tượng và tạo mô tả cho khung hình.
- Giao diện web cho phép chọn nguồn dữ liệu và xem kết quả.

> Lưu ý: theo mã nguồn hiện tại, phần tạo mô tả được gọi cho ảnh và webcam trực tiếp; luồng xử lý video tải lên hiện thực hiện phát hiện đối tượng. Giao diện có lựa chọn “Segment”, nhưng backend hiện đang cung cấp các route phát hiện đối tượng.

## Cấu trúc dự án

```text
Detect_People/
├── app.py                    # Flask app, các route và xử lý ảnh/video/webcam
├── caption.py                # Mô hình và hàm tạo mô tả ảnh (ResNet-50 + LSTM)
├── models/
│   ├── best.pt               # Trọng số YOLO
│   └── best_model.pth        # Trọng số mô hình tạo mô tả
├── static/
│   ├── css/yolo_BHH.css      # Giao diện
│   ├── js/yolo_BHH.js        # Tương tác phía trình duyệt
│   ├── results/              # Kết quả xử lý
│   ├── uploads/              # Tệp tải lên
│   └── weight/
│       └── model_info.pkl    # Từ điển và thông tin mô hình tạo mô tả
└── templates/
    └── yolo_BHH.html         # Trang web chính
```

## Yêu cầu

- Python 3
- Webcam nếu muốn sử dụng chức năng thời gian thực
- Các thư viện Python: Flask, Ultralytics, OpenCV, NumPy, Pillow, PyTorch và TorchVision

## Cài đặt và chạy

1. Clone repository và chuyển vào thư mục dự án:

   ```bash
   git clone https://github.com/buihuutam05062002/Detect_People.git
   cd Detect_People
   ```

2. (Khuyến nghị) Tạo và kích hoạt môi trường ảo:

   ```bash
   python -m venv .venv
   ```

   Windows:

   ```bash
   .venv\Scripts\activate
   ```

   macOS/Linux:

   ```bash
   source .venv/bin/activate
   ```

3. Cài các thư viện cần thiết:

   ```bash
   pip install flask ultralytics opencv-python numpy pillow torch torchvision
   ```

   Nếu cần GPU, hãy cài phiên bản PyTorch phù hợp với CUDA theo hướng dẫn chính thức của PyTorch.

4. Chạy ứng dụng từ thư mục gốc của dự án:

   ```bash
   python app.py
   ```

5. Mở `http://localhost:5000` trong trình duyệt. Chức năng webcam cần quyền truy cập camera và camera được hệ điều hành nhận diện.

## Các route chính

| Route | Phương thức | Chức năng |
|---|---|---|
| `/` | GET | Hiển thị giao diện chính |
| `/detect_image` | POST | Nhận ảnh, phát hiện và đếm đối tượng, tạo mô tả ảnh |
| `/detect_video` | POST | Nhận video và trả đường dẫn video đã đánh dấu đối tượng |
| `/video_feed` | GET | Cung cấp luồng webcam có nhận diện |
| `/source_feed` | GET | Cung cấp luồng webcam gốc |
| `/get_object_count_realtime` | GET | Trả số lượng đối tượng trên webcam |
| `/describe_topic` | GET | Trả mô tả khung hình webcam gần nhất |
| `/stop` | POST | Dừng webcam và kết thúc ghi video |

## Ghi chú

- Chạy `app.py` từ thư mục gốc để các đường dẫn tới trọng số và tài nguyên tương đối được phân giải đúng.
- Các thư mục `static/uploads/` và `static/results/` được dùng để lưu tệp tải lên và kết quả xử lý.
- Ứng dụng khởi tạo webcam khi chạy; nếu không có camera hoặc thiết bị không khả dụng, chức năng thời gian thực có thể không hoạt động.
- Môi trường triển khai cần các tệp trọng số và `static/weight/model_info.pkl` đúng vị trí như cấu trúc trên.
