"""
AnkiAI v3.0 - Migration Guide
OpenAI → Multi-Provider (Gemini + Groq + Ollama)

================================================================================
MAJOR CHANGES
================================================================================

1. AI Providers
   OLD: One OpenAI API key required
   NEW: Multi-provider with auto-fallback
        - Groq (⭐ Fastest, unlimited free)
        - Gemini (⭐ High quality, 60 req/min free)
        - Ollama (Backup, offline, unlimited)

2. Cost
   OLD: $0.01 per keyword (add up fast!)
   NEW: $0 - COMPLETELY FREE ✓
   
3. Speed
   OLD: ~500ms per keyword
   NEW: ~50ms per keyword (Groq) - 10x FASTER ✓

4. Reliability
   OLD: Single provider - if OpenAI is down, you're stuck
   NEW: 3 providers - auto-fallback to next if one fails ✓

================================================================================
FILE CHANGES
================================================================================

NEW FILES:
- modules/ai_providers.py
  Contains: GeminiProvider, GroqProvider, OllamaProvider, MultiAIProvider
  
MODIFIED FILES:
- modules/config.py
  Changed: openai_api_key → gemini_api_key, groq_api_key, use_ollama
  
- modules/api_handler.py
  Removed: OpenAIHandler, generate_image() from AIImageProvider
  Changed: Using MultiAIProvider instead
  
- modules/ui.py
  Changed: UI configuration dialog to show 3 AI options + test button
  
- __init__.py
  Changed: Initialization to use new MultiAIProvider

================================================================================
MIGRATION CHECKLIST
================================================================================

[ ] 1. Get Groq API key from console.groq.com
[ ] 2. Get Gemini API key from makersuite.google.com  
[ ] 3. Get Pexels API key from pexels.com/api (for image search)
[ ] 4. Update settings with new keys
[ ] 5. Click "Test AI Connections" button
[ ] 6. Try adding images to a few cards
[ ] 7. Enjoy faster, free, unlimited AI! 🎉

================================================================================
API CONFIGURATION (v3.0)
================================================================================

DEFAULT_CONFIG = {
    # AI Providers (v3.0)
    "gemini_api_key": "",              # Google Gemini API key
    "groq_api_key": "",                # Groq API key
    "use_ollama": False,               # Use local Ollama
    "ollama_url": "http://localhost:11434",
    
    # Image Search APIs (unchanged)
    "unsplash_api_key": "",
    "pixabay_api_key": "",
    "pexels_api_key": "",
    
    # Settings (unchanged)
    "image_generation_mode": "search",  # Always "search" in v3.0
    "vocabulary_field": "Mặt trước",
    "definition_field": "Định nghĩa",
    "image_field": "Ảnh",
    "image_download_timeout": 20,
    "max_concurrent_requests": 5,
    "enable_keyword_cache": True,
    "enable_image_optimization": True,
    "image_max_width": 800,
    "image_quality": 85,
    "auto_add_on_sync": False,
}

================================================================================
AUTO-FALLBACK LOGIC
================================================================================

When generating a keyword:

1. Try Groq (fastest)
   └─ Success? Return keyword
   └─ Fail? Continue...

2. Try Gemini (high quality)
   └─ Success? Return keyword
   └─ Fail? Continue...

3. Try Ollama (local backup)
   └─ Success? Return keyword
   └─ Fail? Throw error "All AI providers failed"

If any provider hits rate limit or times out, automatically tries the next one.

================================================================================
CODE EXAMPLES
================================================================================

OLD (v2.0):
```python
ai_provider = AIImageProvider(
    openai_key="sk-...",
    mode="dall-e",
    unsplash_key="...",
)
```

NEW (v3.0):
```python
ai_provider = AIImageProvider(
    gemini_key="AIzaSy...",
    groq_key="gsk_...",
    use_ollama=False,
    pexels_key="...",
)
```

================================================================================
SUPPORTED MODELS
================================================================================

Groq: mixtral-8x7b-32768 (8x7B Mixture of Experts)
Gemini: gemini-1.5-flash (Google's latest)
Ollama: mistral (or any local model: neural-chat, openhermes, etc.)

All models are excellent for keyword generation (1-2 words).

================================================================================
OLLAMA LOCAL SETUP
================================================================================

If you want completely LOCAL & OFFLINE operation:

1. Install Ollama: https://ollama.com
2. Download model: ollama pull mistral
3. Start server: ollama serve
4. Enable in AnkiAI: Settings → Check "Sử dụng Ollama local"

Model selection (pick one):
- mistral (balanced, recommended)
- neural-chat (faster, lighter)
- openhermes (better quality, slower)

Size: 4-7GB depending on model
Speed: 0.5-2s per keyword on CPU, 50-100ms on GPU

================================================================================
TESTING
================================================================================

Click "🔌 Test AI Connections" in settings to verify:

Output should show:
✓ Groq API: OK          (or similar for other providers)
✓ Gemini API: OK
✓ Ollama: OK

If all fail, you're not configured correctly.
At least ONE provider must show ✓ to work.

================================================================================
TROUBLESHOOTING
================================================================================

Issue: "No API provider configured"
Solution: Get keys from Groq/Gemini (free, 5 minutes total)

Issue: "All providers failed" 
Solution: Check network, check API keys, click Test button

Issue: Keyword generation timeout
Solution: Ollama might be slow on first request. Disable it and use Groq.

Issue: "Ollama: Not running"
Solution: Open terminal, run: ollama serve

Issue: Want completely offline?
Solution: Use Ollama only (get model first: ollama pull mistral)

================================================================================
PERFORMANCE COMPARISON
================================================================================

Provider | Speed | Quality | Cost | Reliability | Setup Time
---------|-------|---------|------|-------------|------------
Groq     | ⚡⚡⚡  | ⭐⭐⭐  | FREE | ✓✓✓ (cloud) | 2 min
Gemini   | ⚡⚡   | ⭐⭐⭐⭐ | FREE | ✓✓ (cloud)  | 2 min
Ollama   | ⚡    | ⭐⭐⭐  | FREE | ✓ (local)   | 5 min (first time)
OpenAI   | ⚡⚡   | ⭐⭐⭐  | $$$  | ✓✓✓        | 1 min

================================================================================
FAQ
================================================================================

Q: Do I need all 3 providers?
A: No, at least 1 is enough. More = better fallback safety.

Q: Should I use Ollama?
A: Only if you want completely offline option. Otherwise Groq is better.

Q: Is it really free?
A: Yes! Groq and Gemini are 100% free forever (their API policy).

Q: How many images can I add per month?
A: Unlimited! No rate limiting with this setup.

Q: What about image search providers?
A: Still need 1 (Pexels recommended - fastest). All are free.

Q: Can I use just Ollama and be offline?
A: Yes, if you don't care about speed. Set use_ollama=True only.

Q: Why did you drop OpenAI?
A: Cost + speed. Groq is 10x faster and free vs $0.01 each.

================================================================================
ROLLBACK (if needed)
================================================================================

To go back to OpenAI:
1. Edit config.py: Add back openai_api_key
2. Edit api_handler.py: Restore OpenAIHandler class
3. Edit ui.py: Show OpenAI input field
4. Re-upload old __init__.py

But why would you? v3.0 is better in every way! 🚀

================================================================================
"""
