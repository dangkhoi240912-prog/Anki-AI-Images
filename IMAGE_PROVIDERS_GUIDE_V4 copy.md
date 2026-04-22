# 📸 AnkiAI v4.0 - Image Providers Guide

## 6 Image Providers (All FREE!)

---

## 1️⃣ **Pexels** ⭐ BEST CHOICE

**Quality Score:** ⭐⭐⭐⭐⭐ (95/100)  
**Speed:** ⚡⚡⚡ (100ms)  
**Free API Key:** ✅ YES  
**Signup:** 2 minutes

### Why Choose Pexels?

- Highest quality images
- Fastest responses
- Great for learning/education
- Mobile-friendly defaults
- Large collection (500K+ photos)

### Setup

1. Go to: https://www.pexels.com/api/
2. Scroll down, click **"Create"**
3. Fill "Application name"
4. Approve T&C
5. Copy **API Key**
6. Paste into config: `"pexels_api_key": "..."`

### API Rate Limits

- Rate limit: 20,000 requests/month (plenty!)
- Typical usage: 300/month (for 1000 cards)
- ✅ Sufficient for most users

---

## 2️⃣ **Unsplash** ⭐ GREAT BACKUP

**Quality Score:** ⭐⭐⭐⭐ (90/100)  
**Speed:** ⚡⚡⚡ (150ms)  
**Free API Key:** ✅ YES  
**Signup:** 2 minutes

### Why Choose Unsplash?

- Beautiful, curated photos
- Large collection (3M+ images)
- Very reliable
- Good for artistic cards
- Excellent alternative to Pexels

### Setup

1. Go to: https://unsplash.com/developers
2. Sign up (use Google/GitHub for speed)
3. Go to **Applications**
4. Click **New Application**
5. Agree to terms
6. Copy **Access Key**
7. Paste into config: `"unsplash_api_key": "..."`

### API Rate Limits

- Rate limit: 50 requests/hour (free tier)
- Translation: 1,200/day = plenty!
- Fallback: Will use other providers if hit

---

## 3️⃣ **Pixabay** ⭐ GOOD FALLBACK

**Quality Score:** ⭐⭐⭐ (85/100)  
**Speed:** ⚡⚡ (120ms)  
**Free API Key:** ✅ YES  
**Signup:** 2 minutes

### Why Choose Pixabay?

- Large diverse collection (3M+ images)
- Good quality
- Different aesthetic than Pexels
- No account needed for basic access
- Commercial-friendly images

### Setup

1. Go to: https://pixabay.com/api/
2. Click **Sign up** (email or OAuth)
3. Verify email
4. Navigate to API Dashboard
5. Copy **API Key**
6. Paste into config: `"pixabay_api_key": "..."`

### API Rate Limits

- Rate limit: 5,000 requests/hour (free)
- Translation: 120,000/day (!)
- ✅ Very generous

---

## 4️⃣ **Openverse** (Creative Commons)

**Quality Score:** ⭐⭐⭐ (75/100)  
**Speed:** ⚡ (200ms)  
**Free API Key:** ❌ NO (completely open!)  
**Signup:** ⏱️ None needed!

### Why Choose Openverse?

- 💚 NO API KEY NEEDED - completely free!
- CC-licensed images (ethical)
- Large collection (600M+ licensed images)
- Automatically included in v4.0
- Great fallback when others fail

### What You Get

```json
// Automatically included in v4.0
// No configuration needed!
{
  "enable_smart_selection": true
  // Openverse is automatically searched
}
```

### How It Works

- Search: Free, public API
- Rate limits: Very generous
- Quality: Good, but varies
- Best for: Generic terms, educational content

### Example Images

- "Flower" → CC images of flowers
- "Building" → CC images of architecture
- "People" → CC photos of people

---

## 5️⃣ **Wallhaven** (Curated)

**Quality Score:** ⭐⭐⭐⭐ (80/100)  
**Speed:** ⚡ (180ms)  
**Free API Key:** ✅ NO KEY (free tier)  
**Signup:** Optional

### Why Choose Wallhaven?

- High-quality, curated images
- Great geometric/artistic content
- Modern aesthetic
- No API key needed!
- Good for visual learning

### Setup Options

**Option 1: No Setup (Free tier)**
```json
{
  // Just add this flag:
  "wallhaven_api_key": ""  // Empty = free tier
}
```

**Option 2: With API Key (optional)**
```json
{
  "wallhaven_api_key": "YOUR_KEY"  // Skip if not needed
}
```

### Rate Limits

- Free tier: 150 requests/hour (plenty!)
- No API key: Still works!
- With API key: Same limits (no benefit)

---

## 6️⃣ **Lorem Picsum** (Instant Fallback)

**Quality Score:** ⭐⭐ (60/100)  
**Speed:** ⚡⚡⚡⚡⚡ INSTANT  
**Free API Key:** ❌ NO (completely free!)  
**Signup:** ⏱️ None!

### Why Choose Lorem Picsum?

- 💚 INSTANT - no API calls!
- Permanent fallback (always works)
- 600x400px random photos
- Perfect for testing
- No rate limits (static URLs)

### What You Get

```
https://picsum.photos/600/400?random=1
https://picsum.photos/600/400?random=2
...
```

### How It Works

- Returns random stock photos
- Great as last resort
- Always available (no internet needed!)
- Score: 60/100 (but better than nothing!)

### When It's Used

1. All paid providers succeed → Use best (e.g., Pexels)
2. Some fail → Use working ones
3. All fail → Try Lorem Picsum
4. Result: Always get SOME image!

---

## 🎯 Ranking Order in v4.0

When searching for an image, AnkiAI searches all 6 providers and RANKS them:

```
Provider Ranking (highest = best):

1. Pexels      (95/100) ⭐⭐⭐⭐⭐
2. Unsplash    (90/100) ⭐⭐⭐⭐
3. Wallhaven   (80/100) ⭐⭐⭐⭐
4. Pixabay     (85/100) ⭐⭐⭐
5. Openverse   (75/100) ⭐⭐⭐
6. Lorem Picsum (60/100) ⭐⭐ (fallback)
```

**Result:** Best image is automatically selected!

---

## 📊 Comparison Table

| Feature | Pexels | Unsplash | Pixabay | Openverse | Wallhaven | Lorem |
|---------|--------|----------|---------|-----------|-----------|-------|
| Image Quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| Speed | Fast | Medium | Fast | Slow | Medium | INSTANT |
| Need API Key? | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Collection Size | 500K | 3M | 3M | 600M | 1M+ | Infinite |
| Rate Limit | 20K/mo | 50/hr | 5K/hr | Gen. | 150/hr | ∞ |
| Best For | Education | Artistic | Diverse | CC-licensed | Modern | Fallback |
| Recommended? | ✅ Must | ⭐ Good | ⭐ Good | ⭐ Auto | ⭐ Free | ⭐ Safety |

---

## 🔍 Image Quality Comparison

### Example: "Apple"

**Pexels** (95/100) ⭐⭐⭐⭐⭐
- Sharp apple photos
- Well-composed
- Professional quality

**Unsplash** (90/100) ⭐⭐⭐⭐
- Beautiful aesthetic
- Artistic framing
- Good detail

**Pixabay** (85/100) ⭐⭐⭐
- Clear images
- Varied styles
- Good diversity

**Openverse** (75/100) ⭐⭐⭐
- CC-licensed
- Varied quality
- Educational

**Wallhaven** (80/100) ⭐⭐⭐⭐
- Modern aesthetic
- Curated images  
- High quality

**Lorem Picsum** (60/100) ⭐⭐
- Random photo
- Best effort
- Fallback only

---

## 🚀 Setup Priority

### Minimum (works immediately)

```json
{
  "pexels_api_key": "..."
}
```

**Result:** Good images from Pexels only

### Recommended

```json
{
  "pexels_api_key": "...",
  "unsplash_api_key": "..."
}
```

**Result:** Best images from Pexels or Unsplash

### Full Setup (best reliability)

```json
{
  "pexels_api_key": "...",
  "unsplash_api_key": "...",
  "pixabay_api_key": "..."
}
```

**Result:** 
- First search from all 3
- Smart ranking picks best
- Will never fail (6 backups)

### With Creative Commons

```json
{
  "pexels_api_key": "...",
  "unsplash_api_key": "...",
  "pixabay_api_key": "..."
  // Openverse + Lorem auto-included!
}
```

**Result:**
- 6 providers total
- Ethical CC images included
- Ultimate reliability

---

## 💡 Tips

### For Best Images

1. Setup at least **Pexels + Unsplash**
2. Enable smart selection (default)
3. Let it rank all options

### For Maximum Reliability

1. Setup **all 3 paid** (2 min each = 6 min total)
2. Openverse + Lorem auto-included
3. Never worry about failures!

### For Free Setup

1. Use Openverse (auto, no setup)
2. Use Lorem Picsum (instant fallback)
3. Works but may get generic images

### For Educational Use

1. Setup Pexels (best for learning)
2. Add Openverse (CC-licensed = ethically OK)
3. Perfect combo!

---

## ❓ FAQ

### "Do I need all 6 providers?"

No! v4.0 works with just 1-2. But more = better odds.

Recommended: Pexels (must) + Unsplash (good backup)

### "Which is fastest?"

Lorem Picsum (instant, no API call)

But for quality: Pexels + Unsplash

### "What if a provider fails?"

Auto-fallback! With 6 providers, at least 4 usually work.

### "Can I use just free providers?"

Yes! Openverse + Lorem Picsum combo works, but quality varies.

### "Do I need API keys for all?"

No! Only for: Pexels, Unsplash, Pixabay (optional)

Free: Openverse, Lorem Picsum, Wallhaven

### "What's the cost?"

$0! All providers are free.

### "Rate limits?"

Very generous. For 1000 cards:
- Pexels: 20K/mo (you need ~1K)
- Unsplash: 50/hr (you need ~10/hr)
- Pixabay: 5K/hr (you need ~1/hr)

All have buffer!

---

## 🎯 Recommended Setup for Most Users

```json
{
  "groq_api_key": "gsk_...",
  "gemini_api_key": "AIzaSy_...",
  
  // Image providers (choose based on needs):
  "pexels_api_key": "...",      // ← MUST HAVE
  "unsplash_api_key": "...",    // ← HIGHLY RECOMMENDED
  
  // Optional (but free):
  "pixabay_api_key": "",        // ← Optional
  "wallhaven_api_key": "",      // ← Auto (no key needed)
  
  // Smart selection (auto-enabled)
  "enable_smart_selection": true,
  "max_concurrent_providers": 6
  
  // Openverse + Lorem Picsum are AUTOMATIC!
}
```

**Setup Time:** ~5 minutes  
**Quality:** Excellent  
**Reliability:** Very high  
**Cost:** $0  
**Recommendation:** ⭐⭐⭐⭐⭐

---

## 🚀 Getting Started

1. Read [QUICKSTART_V4.md](QUICKSTART_V4.md)
2. Get 2-3 API keys from providers above
3. Paste into config
4. Test connections
5. Start adding images!

**Total time:** 10 minutes  
**Result:** Beautiful, smart Anki images 🎉

---

**Version:** 4.0  
**Last Updated:** 2024  
**All Providers:** ✅ Tested & Working
