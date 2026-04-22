# ⚡ Quick Start - AnkiAI

Thêm ảnh AI vào thẻ Anki trong 5 phút!

## Bước 1: Lấy OpenAI API Key (2 phút)

1. Vào https://platform.openai.com
2. Login/Sign up
3. Click Settings (góc phải)
4. Select "API Keys"
5. Click "Create new secret key"
6. **Copy key** (chỉ hiện 1 lần): `sk-xxxx...`

**Chi phí**: OpenAI cho $5 miễn phí. Sau đó:
- DALL-E mode: $0.08/ảnh
- Search mode: $0.01/ảnh

## Bước 2: Cài đặt add-on (1 phút)

### Cách 1: Từ file .ankiaddon (Dễ nhất)

1. Download file `AnkiAI_ImageAddon.ankiaddon` từ GitHub
2. Mở Anki
3. Go to: `Tools > Add-ons > Install from file`
4. Chọn file `.ankiaddon`
5. Restart Anki

### Cách 2: Từ folder (Cho developers)

```bash
# macOS / Linux
cp -r AnkiAI_ImageAddon ~/Library/Application\ Support/Anki2/addons21/

# Windows
copy AnkiAI_ImageAddon C:\Users\YourName\AppData\Roaming\Anki2\addons21\

# Linux
cp -r AnkiAI_ImageAddon ~/.local/share/Anki2/addons21/
```

Restart Anki.

## Bước 3: Cài đặt API Key (1 phút)

1. Mở Anki
2. Go to: `Browse` (Ctrl+B)
3. Chọn một thẻ bất kỳ
4. Chuột phải → "AnkiAI: Tự động thêm ảnh bằng AI"
5. Dialog: Paste API key từ bước 1
6. Chọn chế độ:
   - **DALL-E**: Tạo ảnh hoàn toàn mới (đẹp, chậm, đắt)
   - **Search**: Tìm ảnh có sẵn (nhanh, rẻ)
7. Click OK

## Bước 4: Thêm ảnh vào thẻ (1 phút)

1. **Mở Browser**: `Ctrl+B`
2. **Chọn thẻ**: 
   - Click thẻ đầu
   - Shift+Click thẻ cuối (hoặc Ctrl+A để chọn tất cả)
3. **Gọi add-on**:
   - Chuột phải → "AnkiAI: Tự động thêm ảnh bằng AI"
4. **Review**:
   - Số thẻ: 100
   - Chế độ: DALL-E
   - Click OK
5. **Chờ xong**: Thanh tiến trình sẽ hiện

✅ **Xong!** Các thẻ giờ có ảnh rồi

## Chế độ nào để chọn?

### 🎨 DALL-E (Tạo ảnh)

```
Từ: "Apple"
Định nghĩa: "Công ty công nghệ"
↓
AI vẽ: Một tấm ảnh hoàn toàn mới minh họa cho Apple
```

✅ Ảnh độc nhất, chủ đề rõ ràng
❌ Chậm hơn ($0.08/ảnh)

**Dùng khi**: Muốn ảnh đẹp & độc nhất

### 🔍 Search (Tìm ảnh)

```
Từ: "Apple"
Định nghĩa: "Công ty công nghệ"
↓
AI tính: "Apple company headquarters"
↓
Unsplash/Pixabay tìm: Hình đó
```

✅ Nhanh, rẻ ($0.01/ảnh)
❌ Phụ thuộc vào xếp hạng tìm kiếm

**Dùng khi**: Muốn xong nhanh & rẻ

---

## Troubleshooting

### ❌ "Invalid API Key"

→ Check lại key từ OpenAI (copy cẩn thận)

### ❌ "Timeout"

→ Internet chậm hoặc server bận. Thử lại sau 5 phút

### ❌ Anki bị lag

→ Giảm số thẻ (50 thẻ / lần thay vì 1000)

### ❌ Không thấy menu trong Browser

→ Restart Anki
→ Check: `Tools > Add-ons > AnkiAI` (có không?)

---

## Ví dụ thực tế

### 📚 Deck TOEIC (500 thẻ)

```
1. Mở Anki
2. Browse → Select deck TOEIC
3. Ctrl+A (select all)
4. Chuột phải → "AnkiAI"
5. Mode: DALL-E
6. OK
7. ☕ Uống cà phê ~30 phút
8. ✅ 500 thẻ có ảnh!
```

### 💰 Chi phí

- DALL-E: 500 × $0.08 = $40
- Search: 500 × $0.01 = $5

---

## Mẹo & Thủ thuật

### Làm nhanh hơn

```json
Mode: Search (thay vì DALL-E)
→ 10x nhanh hơn
→ 8x rẻ hơn
```

### Làm đẹp hơn

```json
Mode: DALL-E
→ Ảnh độc nhất
→ Chủ đề rõ ràng
```

### Chia batch

```
Thay vì: 1000 thẻ lúc
Làm:     100 thẻ × 10 lần

→ Tránh lag
→ Dễ quản lý
```

---

## Câu hỏi thường gặp

**Q: Ảnh sẽ sync lên AnkiWeb không?**
A: Có! Tự động. Không cần làm gì thêm.

**Q: Có thể undo không?**
A: Có. Mỗi thẻ chỉ update 1 lần. Nếu cần xóa ảnh → Edit note.

**Q: Có thể dùng mode khác mỗi lần không?**
A: Có. Mỗi lần run có thể chọn mode khác.

**Q: API key được lưu ở đâu?**
A: Chỉ trên máy bạn. Không bao giờ gửi được bên ngoài.

**Q: Nếu 100 thẻ, 95 thành công, 5 thất bại?**
A: Thử lại những thẻ thất bại. Hoặc skip.

---

## Tiếp theo

- 📖 [Setup đầy đủ](SETUP.md) - Cấu hình nâng cao
- 🏗️ [Architecture](ARCHITECTURE.md) - Cách nó hoạt động
- 👨‍💻 [Development](DEVELOPMENT.md) - Modify code
- 📚 [API Reference](API_REFERENCE.md) - Dùng trong projects khác

---

## Support

Gặp lỗi?
- Check [Full Setup Guide](SETUP.md)
- Post github issue

---

**Hôm nay là ngày tốt để thêm ảnh vào flashcard!** 🚀
