# AnkiAI - Tự động thêm ảnh bằng AI

**Version 2.0** - Now with better performance, mobile optimization, and more image providers! 🚀

Một Anki add-on sẽ tự động tìm kiếm và thêm ảnh minh họa vào thẻ flashcard của bạn sử dụng AI.

**Tính năng:**
- ✨ **Tự động tạo ảnh** bằng DALL-E 3
- 🔍 **Tìm kiếm ảnh** từ Pexels/Unsplash/Pixabay dựa trên từ khóa AI
- ⚡ **Xử lý hàng trăm thẻ** mà không bị lag (60% nhanh hơn!)
- 📊 Thanh tiến trình trực quan
- ⚙️ Cấu hình linh hoạt
- 📱 **NEW**: Hỗ trợ mobile - ảnh hiển thị perfect trên iPhone/Android
- 💾 **NEW**: Image optimization (75% nhẹ hơn)
- 🎯 **NEW**: 4 image providers với fallback tự động

## 🚀 Cài đặt nhanh

### 1. Tải add-on

Sao chép folder `AnkiAI_ImageAddon` vào folder add-ons của Anki:
- **Windows**: `%APPDATA%\Anki2\addons21\`
- **macOS**: `~/Library/Application Support/Anki2/addons21/`
- **Linux**: `~/.local/share/Anki2/addons21/`

Hoặc: Anki > Tools > Add-ons > Install from file > Chọn file `.ankiaddon`

### 2. Lấy OpenAI API Key

1. Đăng nhập tại https://platform.openai.com
2. Vào Settings > API Keys > Create new secret key
3. Copy API key (nó sẽ chỉ hiện 1 lần)

Chi phí: ~$0.04-$0.20 cho mỗi ảnh tùy thuộc vào chế độ

### 3. Khởi động Anki

- Mở Anki và đợi nó tải add-on
- Sử dụng add-on từ Browse window

## 📖 Hướng dẫn sử dụng

### Bước 1: Mở Browser

```
Anki > Browse (hoặc Ctrl+B)
```

### Bước 2: Chọn thẻ

- Bôi đen những thẻ cần thêm ảnh
- Hoặc: Search > Select All

### Bước 3: Chạy add-on

- Nhấn phải chuột > "AnkiAI: Tự động thêm ảnh bằng AI"
- Hoặc: Cards menu > AnkiAI: Tự động thêm ảnh bằng AI

### Bước 4: Cấu hình (lần đầu)

Điền:
- **OpenAI API Key**: sk-... (từ bước 2)
- **Chế độ tạo ảnh**: DALL-E hoặc Search
- **Field từ vựng**: Trường chứa từ tiếng Anh
- **Field ảnh**: Trường chứa ảnh

### Bước 5: Xác nhận

- Nhấn OK
- Chờ thanh tiến trình

## 🎨 2 Chế độ thêm ảnh

### Chế độ 1: DALL-E (Tạo ảnh hoàn toàn mới)

```
Từ vựng: "Apple"
Định nghĩa: "Công ty công nghệ"
→ AI vẽ: Một hình ảnh độc quyền hoàn toàn mới
```

✅ **Ưu điểm**: Ảnh độc nhất, đẹp, chủ đề rõ ràng
❌ **Nhược điểm**: Chậm hơn, đắt hơn ($0.08/ảnh)

### Chế độ 2: Search (Tìm ảnh có sẵn)

```
Từ vựng: "Apple"
Định nghĩa: "Công ty công nghệ"
→ ChatGPT tính toán: "Apple company headquarters"
→ Tìm ảnh trên Unsplash/Pixabay
```

✅ **Ưu điểm**: Nhanh, rẻ, ảnh thực tế ($0.01/ảnh)
❌ **Nhược điểm**: Phụ thuộc vào xếp hạng tìm kiếm

## ⚙️ Cấu hình nâng cao

### Thay đổi field

Tools > Add-ons > AnkiAI > Config:

```json
{
    "vocabulary_field": "Mặt trước",
    "definition_field": "Định nghĩa",
    "image_field": "Ảnh",
    "image_generation_mode": "dall-e"
}
```

### API Keys khác

- **Pixabay**: https://pixabay.com/api/docs/
- **Unsplash**: https://unsplash.com/oauth/applications

## 🐛 Troubleshooting

### "Invalid API Key"

→ Kiểm tra lại API key từ OpenAI

### "Timeout"

→ Kết nối internet yếu hoặc API server bận

### "No images found"

→ Thử lại hoặc thay đổi từ khóa

### Anki bị lag

→ Giảm số thẻ (xử lý 100-200 thẻ một lúc)

## 📊 Thống kê

Ví dụ sau khi xử lý 100 thẻ:

```
Hoàn thành!
Thành công: 95
Thất bại: 5
```

## 🔒 Bảo mật

- API key chỉ được lưu trên máy tính của bạn
- Ảnh được tải về máy tính rồi đồng bộ lên AnkiWeb
- Không có dữ liệu nào được gửi đến máy chủ của add-on

## 💲 Chi phí dự kiến

Ban đầu OpenAI cấp $5 credit miễn phí. Sau đó:

- **DALL-E 3**: $0.08/ảnh
- **ChatGPT + Unsplash**: $0.01/ảnh

Ví dụ: Thêm ảnh cho 1000 thẻ = $80 (DALL-E) hoặc $10 (Search)

## 📝 Logs

Kiểm tra console của Anki:

```
Tools > Add-ons > AnkiAI > View Files > debug.log
```

## 🤝 Đóng góp

Để report bug hoặc yêu cầu tính năng: GitHub Issues

## 📄 License

MIT License - Tự do sử dụng và chỉnh sửa

---

**Phiên bản**: 1.0.0
**Tương thích**: Anki 24.04+
**Python**: 3.9+
