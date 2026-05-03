# 🚀 AnkiAI v3.0 Quick Start (5 phút)

## Nâng cấp: OpenAI → Multi-Provider FREE (Gemini + Groq + Ollama)

### ⏱️ Tổng thời gian setup: ~5 phút

---

## Bước 1️⃣: Get Groq API Key (1 phút)

**Groq là cách tốt nhất** - Siêu nhanh (50ms), miễn phí, unlimited

1. Mở: https://console.groq.com/keys
2. Đăng nhập (hoặc tạo tài khoản - miễn phí)
3. Click **"Create API Key"**
4. Copy API key (dạng: `gsk_xxxxxxxxxxxx`)

✅ **Xong! Lưu key này lại**

---

## Bước 2️⃣: Get Gemini API Key (1 phút)  

**Gemini**: Chất lượng cao, miễn phí, 60 req/phút

1. Mở: https://makersuite.google.com/app/apikey
2. Đăng nhập Google
3. Click **"Create API Key"** → **"Create API key in new project"**
4. Copy API key (dạng: `AIzaSy...`)

✅ **Xong! Lưu key này lại**

---

## Bước 3️⃣: Get Pexels API Key for Images (1 phút)

**Pexels**: Tìm ảnh chất lượng cao, miễn phí

1. Mở: https://www.pexels.com/api/
2. Scroll xuống → Click **"Create"**
3. Tạo application mới
4. Copy **API Key**

✅ **Xong! Lưu key này lại**

---

## Bước 4️⃣: Config AnkiAI

1. Mở **Anki**
2. Tools → Add-ons → **AnkiAI** → **Config**
3. Paste các keys: 
   - Copy Groq key → `"groq_api_key": "..."`
   - Copy Gemini key → `"gemini_api_key": "..."`
   - Copy Pexels key → `"pexels_api_key": "..."`

**Ví dụ:**
```json
{
    "groq_api_key": "gsk_abc123...",
    "gemini_api_key": "AIzaSy_xyz...",
    "pexels_api_key": "xyz123...",
    ...
}
```

4. Save (Ctrl+S hoặc Command+S)

✅ **Xong! Cấu hình hoàn tất**

---

## Bước 5️⃣: Test (1 phút)

1. Mở **Anki Settings** → Scroll lên (nếu config view còn mở, close nó)
2. Tools → Add-ons → AnkiAI
3. Lệnh: Right-click → Look for menu hoặc...
4. Actually, to test: Open browser, select some cards, then test

**Hoặc test bằng Console:**
```
Settings dialog sẽ có nút "🔌 Test AI Connections"
Click nó → Sẽ show:
✓ Groq API: OK
✓ Gemini API: OK
(nếu tất cả green = setup thành công!)
```

---

## Bước 6️⃣: Use It! 🎉

1. Mở Anki → Browser
2. Chọn các thẻ cần thêm ảnh
3. Right-click → **"AnkiAI: Tự động thêm ảnh bằng AI"**
4. Chọn fields (vocabulary, definition, image field)
5. Click "Thêm ảnh"
6. Wait... `[✓] Groq Generating keyword...` → `[✓] Pexels Searching...` 
7. ✨ Xong! Như thế với từng thẻ

---

## 🆘 Nếu bị lỗi?

### "No AI provider configured"
→ Bạn chưa paste API keys. Quay lại Bước 4

### Groq/Gemini error
→ Double-check keys không sai. Mở console.groq.com hoặc makersuite.google.com để verify

### Images không được tìm thấy
→ Check Pexels key. Hay thử Unsplash key thay

### Rất chậm
→ Ollama chạy trên máy bạn nên chậm. Disable nó (set `"use_ollama": false`)

---

## 📊 So sánh v2.0 vs v3.0

| Tiêu chí | v2.0 (OpenAI) | v3.0 (Multi) |
|----------|---|---|
| **Giá** | $0.01/từ khóa | MIỄN PHÍ ✓ |
| **Tốc độ** | 500ms | 50ms (10x nhanh) ✓ |
| **Setup** | 1 API (OpenAI) | 2 API free (Groq+Gemini/Pexels) |
| **Reliability** | Một provider | 3 providers auto-fallback ✓ |
| **Unlimited?** | Không (rate limit) | Có ✓ |

**Tiết kiệm:** 1000 ảnh/tháng = $10 → **$0** 🎊

---

## 🎯 Next Steps

Xem thêm tại:
- **SETUP_V3.md** - Chi tiết từng provider
- **MIGRATION_V3.md** - Thay đổi kỹ thuật
- **README.md** - Overview tổng quát
- **DEVELOPMENT.md** - Para developers

---

## 💡 Tips

**Best Setup:**
```json
{
    "groq_api_key": "...",           // ← Groq (siêu nhanh)
    "gemini_api_key": "...",         // ← Gemini (high quality, fallback)
    "pexels_api_key": "...",         // ← Pexels (images)
    "use_ollama": false              // ← Ollama (skip unless offline)
}
```

Với setup này:
- ✅ Groq sẽ được dùng 99% (nhanh nhất)
- ✅ Gemini sẽ backup nếu Groq down
- ✅ Ảnh từ Pexels (siêu chất lượng)
- ✅ Offline option (Ollama) skip
- ✅ Hoàn toàn FREE

---

**Ready?** 🚀 Hãy thử ngay!

Questions → Check SETUP_V3.md
