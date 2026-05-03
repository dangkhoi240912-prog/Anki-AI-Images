# 🚀 AnkiAI v3.0 - Multi-AI Provider Setup Guide

## Nâng cấp từ OpenAI sang Multi-Provider (Gemini + Groq + Ollama)

Chúng tôi đã chuyển từ **OpenAI ChatGPT** sang hệ thống **Multi-AI Provider auto-fallback** hoàn toàn miễn phí! 🎉

---

## ⚡ Lợi ích v3.0

| Feature | OpenAI | v3.0 (Groq+Gemini+Ollama) |
|---------|--------|--------------------------|
| **Giá** | $0.01/keyword | **MIỄN PHÍ** ✓ |
| **Tốc độ** | ~500ms | **~50ms (Groq)** ✓✓✓ |
| **Chất lượng từ khóa** | Tốt | **Tốt** ✓ |
| **Giới hạn** | 3 req/phút | Groq: Unlimited, Gemini: 60/phút |
| **Auto-fallback** | Không | **Có** ✓ |
| **Local option** | Không | **Ollama (offline)** ✓ |

---

## 📋 Cấu hình từng AI Provider

### 1️⃣ **Groq** (⭐⭐⭐ Nên dùng - Siêu nhanh, miễn phí)

**Đặc điểm:**
- ⚡ Siêu nhanh (~50ms)
- 💚 Hoàn toàn miễn phí (không cần thẻ tín dụng)
- ♾️ Không giới hạn requests
- 🎯 Model: Mixtral 8x7B (chất lượng cao)

**Hướng dẫn cài đặt:**

1. Truy cập: https://console.groq.com/keys
2. Đăng nhập hoặc tạo tài khoản (miễn phí)
3. Click **"Create API Key"**
4. Copy API key
5. Paste vào: **Settings → Groq API Key**

```
API Key Format: gsk_xxxxxxxxxxxxxxxxxxxx
```

---

### 2️⃣ **Google Gemini** (⭐⭐ Nên dùng - Chất lượng cao, miễn phí)

**Đặc điểm:**
- 🎯 Chất lượng từ khóa rất cao
- 💚 Hoàn toàn miễn phí (không cần thẻ tín dụng)
- ⏱️ Giới hạn: 60 requests/phút
- 🚀 Model: Gemini 1.5 Flash (nhanh & intelligent)

**Hướng dẫn cài đặt:**

1. Truy cập: https://makersuite.google.com/app/apikey
2. Đăng nhập với Google Account
3. Click **"Create API Key"**
4. Chọn **"Create API key in new project"** hoặc project hiện tại
5. Copy API key
6. Paste vào: **Settings → Gemini API Key**

```
API Key Format: AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

### 3️⃣ **Ollama** (⭐ Local backup - Hoàn toàn miễn phí, offline)

**Đặc điểm:**
- 💻 Chạy trên máy của bạn (không cần internet)
- 💚 Hoàn toàn miễn phí
- ♾️ Không giới hạn requests
- ⚠️ Chậm hơn (tùy vào GPU)
- 📱 Yêu cầu: ~4GB RAM, cần tải model

**Hướng dẫn cài đặt:**

#### Bước 1: Cài đặt Ollama

- **macOS/Windows/Linux**: Tải từ https://ollama.com
- Click **Download** → Follow instructions

#### Bước 2: Tải model (chỉ làm lần đầu)

```bash
ollama pull mistral
# hoặc một model khác:
# ollama pull neural-chat       (nhẹ, nhanh)
# ollama pull openhermes       (chất lượng cao)
```

Lần đầu sẽ tải (~5GB, yêu cầu internet). Lần sau không cần.

#### Bước 3: Khởi động Ollama

```bash
ollama serve
# hoặc dùng GUI: Ollama → Start
```

Ollama sẽ chạy tại: `http://localhost:11434`

#### Bước 4: Cấu hình trong AnkiAI

- Settings → Tick **"Sử dụng Ollama local"**
- Đảm bảo URL là: `http://localhost:11434`

---

## 🔄 Cơ chế Auto-Fallback

Khi bạn yêu cầu generate từ khóa, AnkiAI sẽ tự động:

```
Yêu cầu generate từ khóa
    ↓
Thử Groq (nhanh nhất) → Thành công? ✓ Hoàn tất
    ↓ (Groq failed)
Thử Gemini (chất lượng cao) → Thành công? ✓ Hoàn tất
    ↓ (Gemini failed)
Thử Ollama (local) → Thành công? ✓ Hoàn tất
    ↓ (Tất cả failed)
❌ Lỗi: Không có AI provider nào khả dụng
```

**Lợi ích:**
- ✅ Không bao giờ bị block (2 provider là đủ)
- ✅ Nếu Groq hit rate limit, tự động chuyển sang Gemini
- ✅ Nếu internet down, Ollama local vẫn chạy được
- ✅ Tự động retry khi một provider bị lỗi

---

## 📷 Image Search Providers

Các AI provider trên chỉ dùng cho **keyword generation**. 

Để tìm ảnh, bạn vẫn cần **Image Search Providers** (miễn phí):

### Pexels (⭐ Nên dùng - Nhanh, chất lượng cao)

1. Truy cập: https://www.pexels.com/api/
2. Click **Create** → Tạo API key mới
3. Copy key
4. Paste vào: **Settings → Pexels API Key**

### Unsplash (Tuỳ chọn)

1. Truy cập: https://unsplash.com/developers
2. Click **Applications** → **New Application**
3. Copy **Access Key**
4. Paste vào: **Settings → Unsplash API Key**

### Pixabay (Tuỳ chọn)

1. Truy cập: https://pixabay.com/api/
2. Tạo tài khoản
3. Đăng nhập → Copy **API KEY**
4. Paste vào: **Settings → Pixabay API Key**

---

## ✅ Check Setup

Sau khi cấu hình, click **"🔌 Test AI Connections"** trong Settings để verify:

```
✓ Groq API: OK
✓ Gemini API: OK  
✓ Ollama: OK
```

Nếu ít nhất một provider show ✓, bạn đã sẵn sàng!

---

## 🆘 Troubleshooting

### "No AI provider configured"
→ Cấu hình ít nhất một AI key (Groq HOẶC Gemini HOẶC Ollama)

### Groq API Key invalid
→ Double-check key từ https://console.groq.com/keys

### Gemini API Key invalid  
→ Double-check key từ https://makersuite.google.com/app/apikey

### Ollama: Not running
→ Mở terminal, chạy: `ollama serve`

### Rất chậm (hoặc timeout)
→ Ollama có thể đang process. Đợi hoặc disable Ollama & dùng Groq/Gemini

---

## 💰 Chi phí

| Provider | Giá | Giới hạn |
|----------|-----|---------|
| Groq | **FREE** | Unlimited |
| Gemini | **FREE** | 60 reqs/phút |
| Ollama | **FREE** | Unlimited |
| **Tổng cộng** | **$0/tháng** ✓ | |

Nếu so sánh với OpenAI ($0.01/request):
- 1000 keywords/tháng = $10 → **SAVE $10/tháng** 🎉

---

## 🚀 Getting Started

1. **Bước 1**: Get API keys (Groq + Gemini + Pexels)
2. **Bước 2**: Paste vào Settings
3. **Bước 3**: Click "Test" để verify
4. **Bước 4**: Select cards → Right-click → "Add Images"
5. **Enjoy!** 🎊

---

## 📚 Reference

- Groq Console: https://console.groq.com
- Gemini API Keys: https://makersuite.google.com/app/apikey
- Ollama: https://ollama.com
- Pexels API: https://www.pexels.com/api
- Unsplash API: https://unsplash.com/developers
- Pixabay API: https://pixabay.com/api

---

**Questions?** Check QUICKSTART.md or DEVELOPMENT.md
