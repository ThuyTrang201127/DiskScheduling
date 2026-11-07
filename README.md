# Disk Scheduling Simulator

Project mô phỏng thuật toán lập lịch đĩa **LOOK** và **C-LOOK** bằng Python 3.
Giao diện Tkinter cho phép nhập dữ liệu trực tiếp, xem nhật ký từng bước và quan
sát biểu đồ Matplotlib để so sánh tổng quãng đường của hai thuật toán.

Project không có cơ sở dữ liệu và không có nút chạy kiểm thử tự động. Các bộ dữ
liệu mẫu nằm trong README này.
## Chức năng

- Chọn riêng LOOK, C-LOOK hoặc so sánh cả hai trên cùng một đầu vào.
- Nhập cylinder lớn nhất của đĩa, chọn hướng ban đầu Trái/Phải; kiểm tra cylinder
  và đầu đọc trong phạm vi từ 0 đến giới hạn đã nhập.
- Mô phỏng đường đi; hiển thị vị trí trước/sau, khoảng cách, tổng tích lũy, hướng,
  sự kiện đổi hướng/quay vòng và các yêu cầu còn lại.
- In cùng nhật ký mô phỏng ra Terminal.
- Hoạt ảnh đầu đọc tiến từ trên xuống trên biểu đồ Matplotlib; biểu đồ cột so
  sánh tổng quãng đường LOOK và C-LOOK theo chính dữ liệu vừa nhập.
- Báo lỗi dữ liệu không hợp lệ mà không làm sập giao diện.
- Dữ liệu hàng đợi rỗng được chấp nhận như một trường hợp biên; kết quả có tổng
  quãng đường bằng 0.

## Cấu trúc project

```text
DiskScheduling/
├── main.py
├── requirements.txt
├── README.md
├── algorithms/
│   ├── __init__.py
│   ├── common.py
│   ├── look.py
│   └── clook.py
├── gui/
│   ├── __init__.py
│   └── main_window.py
├── visualization/
│   ├── __init__.py
│   └── chart.py
```

`algorithms/` chỉ chứa kiểm tra dữ liệu và phép tính. `gui/` chịu trách nhiệm
nhận dữ liệu và trình bày. `visualization/` vẽ biểu đồ bằng Matplotlib. Tách riêng
các phần này giúp dễ đọc, giải thích và thay đổi mà không trộn thuật toán với giao diện.

## Nguyên lý

### LOOK

1. Sắp xếp các yêu cầu cylinder nhỏ hơn và lớn hơn đầu đọc.
2. Phục vụ các yêu cầu theo hướng ban đầu.
3. Khi đã đến yêu cầu xa nhất ở phía đó, đổi hướng tại chính cylinder này và
   phục vụ các yêu cầu còn lại.
4. Không chạy đến biên đĩa nếu không có yêu cầu ở đó.

### C-LOOK

1. Phục vụ các yêu cầu theo một hướng.
2. Khi hết yêu cầu ở phía đang đi, quay vòng tới yêu cầu ở đầu kia.
3. Tiếp tục phục vụ theo cùng hướng ban đầu, không quét ngược lại như LOOK.
4. Tổng quãng đường bao gồm cả khoảng cách của chặng quay vòng.

Mỗi bước tính khoảng cách là `abs(vị_trí_mới - vị_trí_cũ)`. Vì vậy chặng quay
vòng C-LOOK cũng được tính vào tổng di chuyển.

## Cài đặt và chạy trên VS Code (Windows)

1. Cài Python 3 và VS Code. Trong VS Code, chọn **File → Open Folder…** và mở
   thư mục `DiskScheduling`.
2. Mở Terminal (**Terminal → New Terminal**). Tạo môi trường ảo:

   ```powershell
   py -3 -m venv .venv
   ```

   Nếu PowerShell báo không nhận ra `py` và `python`, gọi trực tiếp CPython đã cài.
   Ví dụ với Python 3.14 cài theo mặc định cho user hiện tại:

   ```powershell
   & "$env:LocalAppData\Programs\Python\Python314\python.exe" -m venv .venv
   ```

   Nếu cài phiên bản hoặc vị trí khác, thay đường dẫn bằng đường dẫn
   `python.exe` của CPython trên máy.
3. Cài Matplotlib:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

4. Trong VS Code, nhấn **Ctrl+Shift+P**, chọn **Python: Select Interpreter**, rồi
   chọn Python trong `.venv`.
5. Chạy ứng dụng:

   ```powershell
   .\.venv\Scripts\python.exe .\main.py
   ```

Nếu đã xóa `.venv`, hãy tạo lại môi trường bằng bước 2 rồi cài lại thư viện bằng
bước 3. Thư mục `__pycache__` được Python tự tạo lại khi chạy và không cần khôi phục.

Tkinter thường được đóng gói cùng Python trên Windows. Nếu khi mở ứng dụng báo
thiếu Tkinter, hãy cài lại Python từ python.org và bật thành phần Tcl/Tk.
Nên dùng CPython x64 từ python.org cho môi trường ảo của project. Một số bản
Python thuộc MSYS2/UCRT có thể không có wheel Matplotlib tương thích; khi pip cố
biên dịch Matplotlib từ mã nguồn, hãy chọn interpreter CPython x64 trong VS Code,
xóa môi trường ảo chưa cài được thư viện rồi tạo lại theo các bước trên.

## Cách nhập và trình bày

1. Nhập các cylinder cách nhau bằng dấu cách hoặc dấu phẩy, ví dụ:
   `98 183 37 122 14 124 65 67`. Cách nhập cũ dùng dấu phẩy
   `98, 183, 37, 122, 14, 124, 65, 67` vẫn được hỗ trợ.
2. Nhập vị trí đầu đọc và cylinder lớn nhất (mặc định `199`), chọn hướng Trái/Phải
   và thuật toán.
3. Nhấn **Chạy mô phỏng**. Nhật ký hiện ở tab **Nhật ký từng bước** và trong
   Terminal; biểu đồ hiện ở tab **Biểu đồ & so sánh**.
4. Chọn **So sánh cả hai** để xem hai đường đi và biểu đồ cột so sánh cùng lúc.
   Nút **Tạm dừng/Tiếp tục** điều khiển hoạt ảnh. **Xóa dữ liệu** đặt lại biểu mẫu.

Mỗi dòng nhật ký có thuật toán, số bước, vị trí đầu đọc trước/sau, khoảng cách,
tổng tích lũy, hướng, sự kiện và hàng đợi còn lại. LOOK đánh dấu bước **Đổi
hướng**; C-LOOK đánh dấu **Quay vòng** và tô chặng đó màu cam trên biểu đồ.

## Bộ dữ liệu tự kiểm tra

### TC01 – Thông thường

- Cylinder: `98, 183, 37, 122, 14, 124, 65, 67`
- Đầu đọc: `53`; cylinder lớn nhất: `199`; hướng: **Phải**
- LOOK phải có thứ tự `65, 67, 98, 122, 124, 183, 37, 14`, tổng `299`.
- C-LOOK phải có thứ tự `65, 67, 98, 122, 124, 183, 14, 37`, tổng `322`.

### TC02 – Cylinder ở biên

- Cylinder: `0, 199`; đầu đọc: `0`; cylinder lớn nhất: `199`; hướng: **Phải**
- Hai thuật toán đều phục vụ `0, 199`, tổng di chuyển `199`.

### TC03 – Cylinder âm

- Cylinder: `-5, 20`; đầu đọc: `53`.
- Ứng dụng phải báo cylinder `-5` nằm ngoài phạm vi `0..199` và không crash.

### Các trường hợp bổ sung

- Xóa trống hàng đợi: kết quả hợp lệ, không có yêu cầu, tổng bằng `0`.
- Chữ thay số: `abc, 20`; cylinder vượt giới hạn: `20, 200`.
- Đầu đọc không phải số hoặc ngoài giới hạn: `abc` hoặc `200`.
- Cylinder lớn nhất không phải số hoặc âm; đầu đọc/yêu cầu lớn hơn giới hạn.
- Cylinder trùng: `50, 50, 10, 190`; hai yêu cầu cylinder 50 vẫn được tính riêng.
- Chạy TC01 với hướng **Trái** để quan sát thứ tự phục vụ thay đổi.

Giá trị tính tay để đối chiếu có trong `reports/test_results.txt`.

## Kiểm thử tự động

Project theo yêu cầu tối giản này **không tạo thư mục tests và không có nút chạy
kiểm thử**. Hãy tự nhập các bộ dữ liệu ở trên vào giao diện khi kiểm tra hoặc
trình bày. Nhật ký sẽ cho thấy rõ từng bước để đối chiếu kết quả.
