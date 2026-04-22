# 📦 Hướng dẫn cài đặt chi tiết AnkiAI

## Giai đoạn 1-5 của Add-on

### Giai đoạn 1: Xây dựng nền tảng ✅

**Mục tiêu**: Tạo nút bấm, lấy danh sách thẻ, đọc nội dung

**Đã thực hiện**:
- ✅ Browser Context Menu: Người dùng chọn thẻ → Chuột phải → "AnkiAI: Tự động thêm ảnh"
- ✅ Trích xuất dữ liệu: Lấy từ vựng + định nghĩa từ thẻ
- ✅ Kiến thức: Hook `browser_menus_did_init `

**File liên quan**: `modules/ui.py`

---

### Giai đoạn 2: Tích hợp "Bộ não" AI ✅

**Mục tiêu**: Gửi dữ liệu lên AI, nhận kết quả

**2 Tùy chọn**:

#### 🎨 Tùy chọn A: Tạo ảnh (DALL-E)

```python
# Gửi cho DALL-E:
ai_provider.get_image_url("Apple", "Công ty công nghệ")
# → Nhận URL ảnh: https://...png
```

- Độc nhất, chủ đề rõ ràng
- Chi phí: $0.08/ảnh

#### 🔍 Tùy chọn B: Tìm ảnh (ChatGPT + Unsplash)

```python
# Bước 1: ChatGPT tính từ khóa
"apple" + "Công ty công nghệ" → "Apple headquarters"

# Bước 2: Tìm trên Unsplash
Unsplash.search("Apple headquarters") → URL ảnh
```

- Nhanh, rẻ
- Chi phí: $0.01/ảnh

**File liên quan**: `modules/api_handler.py`

---

### Giai đoạn 3: Tải ảnh & Lưu vào Database ✅

**Mục tiêu**: Tải ảnh từ URL, lưu vào Anki đúng cách

**Quy trình**:

```python
# 1. Tải ảnh từ URL
image_data = requests.get(url).content

# 2. QUAN TRỌNG: Lưu bằng Anki API (không phải file bình thường)
mw.col.media.writeData("ten_anh.jpg", image_data)

# 3. Chèn vào note
note["Ảnh"] = '<img src="ten_anh.jpg">'
note.flush()
```

**File liên quan**: `modules/image_handler.py`

---

### Giai đoạn 4: Chống "Đơ" phần mềm (Background Processing) ✅

**Mục tiêu**: Xử lý 1000 thẻ không bị freeze UI

**Giải pháp**: Sử dụng `aqt.operations.QueryOp`

```python
BackgroundProcessor.process_cards_in_background(
    note_ids=[1, 2, 3, ...],
    process_func=process_note,
    on_progress=update_bar,
    on_success=show_results
)

# → Chạy ngầm, không freeze
# → Thanh tiến trình: "Đang xử lý 15/1000"
```

**File liên quan**: `modules/bg_handler.py`

---

### Giai đoạn 5: Cấu hình & Đóng gói ✅

**Mục tiêu**: Người dùng khác dùng được

**Tính năng**:
- Dialog nhập API Key (không hard-code)
- Chọn field tùy ý (không giả định tên)
- Lưu cấu hình

**File liên quan**: `modules/config.py`, `modules/ui.py`

---

## 💻 Cài đặt trên máy

### Bước 1: Tải add-on

```bash
# Option 1: Sao chép thư mục
cp -r AnkiAI_ImageAddon ~/Library/Application\ Support/Anki2/addons21/

# Option 2: Tạo symlink (để dễ debug)
ln -s $(pwd)/AnkiAI_ImageAddon ~/Library/Application\ Support/Anki2/addons21/
```

### Bước 2: Khởi động Anki

```bash
# Anki sẽ tự load add-on từ folder addons21
```

### Bước 3: Kiểm tra console

Nyc Anki Tools > Add-ons > AnkiAI > View Files > logs để xem thông báo

---

## 🔑 Lấy API Keys

### OpenAI API Key

1. Vào https://platform.openai.com
2. Sign up hoặc login
3. Settings > API Keys > Create new secret key
4. Copy key: `sk-...`
5. Paste vào cài đặt add-on

### Unsplash API Key (tuỳ chọn - dùng cho Search mode)

1. Vào https://unsplash.com/oauth/applications
2. Create New Application
3. Chấp nhận terms
4. Copy Access Key
5. Paste vào cài đặt add-on

### Pixabay API Key (tuỳ chọn)

1. Vào https://pixabay.com/api/
2. Sign up
3. Copy API Key
4. Paste vào cài đặt add-on

---

## 🎮 Sử dụng Add-on

### Lần đầu tiên

1. **Mở Anki** → Chờ load xong

2. **Mở Browser**
   ```
   Anki → Browse (Ctrl+B)
   ```

3. **Chọn thẻ**
   ```
   Click chọn thẻ đầu
   Shift+Click chọn thẻ cuối (hoặc Ctrl+A để chọn tất cả)
   ```

4. **Gọi add-on**
   - Chuột phải → "AnkiAI: Tự động thêm ảnh bằng AI"
   - Hoặc: Cards menu → "AnkiAI: Tự động thêm ảnh bằng AI"

5. **Cấu hình (lần đầu)**
   - Dialog xuất hiện
   - Nhập OpenAI API Key
   - Chọn chế độ (DALL-E hoặc Search)
   - OK

6. **Chọn Field (nếu cần)**
   - Nếu tên field khác, dialog sẽ hỏi
   - Chọn đúng field từ vựng, ảnh, etc.

7. **Xác nhận**
   - Review: số thẻ, chế độ, field
   - OK để bắt đầu

8. **Chờ hoàn thành**
   - Thanh tiến trình: "Đang xử lý 15/100"
   - Sau khi xong: Kết quả (thành công/thất bại)

### Lần sau

- Chỉ cần: Chọn thẻ → Chuột phải → "AnkiAI" → OK
- Cấu hình được nhớ tự động

---

## ⚙️ Cấu hình nâng cao

### Sửa config file

```
Anki → Tools → Add-ons → AnkiAI → Config
```

**Ví dụ config**:

```json
{
    "openai_api_key": "sk-...",
    "unsplash_api_key": "",
    "image_generation_mode": "dall-e",
    "vocabulary_field": "Mặt trước",
    "definition_field": "Định nghĩa",
    "image_field": "Ảnh",
    "image_download_timeout": 30,
    "max_concurrent_requests": 3,
    "auto_add_on_sync": false
}
```

**Giải thích**:
- `openai_api_key`: API key từ OpenAI
- `image_generation_mode`: "dall-e" (tạo) hoặc "search" (tìm)
- `vocabulary_field`: Tên field chứa từ vựng
- `definition_field`: Tên field chứa định nghĩa
- `image_field`: Tên field chứa ảnh
- `image_download_timeout`: Timeout tải ảnh (giây)

---

## 📊 Ví dụ thực tế

### Deck: Từ vựng tiếng Anh TOEIC

**Template**:

```
Mặt trước (Front): Apple
Mặt sau (Back): 1. A company
                2. A red fruit
Ảnh: (trống)
```

**Chạy add-on**:

```
1. Chọn 500 thẻ trong deck TOEIC
2. Browse → Chuột phải → "AnkiAI"
3. Mode: DALL-E
4. Field chọn: Mặt trước, Ảnh
5. OK
6. Chờ ~30 phút
7. Kết quả: 480/500 thẻ có ảnh mới
```

---

## 🐛 Lỗi thường gặp

### 1. "Error: INVALID_API_KEY"

**Nguyên nhân**: API key sai hoặc hết hạn

**Giải pháp**:
- Kiểm tra lại key từ OpenAI
- Tạo key mới
- Paste vào config

### 2. "Image not found"

**Nguyên nhân**: Unsplash/Pixabay không có ảnh cho từ khóa

**Giải pháp**:
- Không thể sửa (từ khóa do AI tính)
- Thử chế độ DALL-E (tạo ảnh)

### 3. "Connection timeout"

**Nguyên nhân**: Internet yếu hoặc server bận

**Giải pháp**:
- Check internet
- Thử lại sau 5 phút
- Giảm số thẻ xử lý (100 → 50)

### 4. "Anki bị lag"

**Nguyên nhân**: Xử lý quá nhiều thẻ cùng lúc

**Giải pháp**:
- Chia batch: 50 thẻ / lần
- Chờ xong lần này rồi làm lần khác

### 5. "Field not found"

**Nguyên nhân**: Tên field sai

**Giải pháp**:
- Check lại tên field trong template
- Cấu hình lại trong Config

---

## 🚀 Tối ưu hoá

### Để tốc độ nhanh nhất

```json
{
    "image_generation_mode": "search",  // Thay vì "dall-e"
    "max_concurrent_requests": 5,
    "image_download_timeout": 20
}
```

Chi phí: ~$10 cho 1000 thẻ (thay vì $80)
Thời gian: 10 phút (thay vì 60 phút)

### Để chất lượng ảnh cao nhất

```json
{
    "image_generation_mode": "dall-e"
}
```

Chi phí: ~$80 cho 1000 thẻ
Thời gian: 60 phút
Chất lượng: Cao, độc nhất

---

## 📞 Support

Nếu gặp lỗi không trong danh sách:

1. Kiểm tra logs: Tools > Add-ons > AnkiAI > View Files > debug
2. Screenshot lỗi
3. Post trong Add-on forum hoặc GitHub

---

**Last updated**: 2024
