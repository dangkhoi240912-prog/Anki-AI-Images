# 👨‍💻 Hướng dẫn phát triển AnkiAI

## Cài đặt môi trường phát triển

### 1. Clone/Download add-on

```bash
cd ~/Desktop
git clone https://github.com/yourusername/AnkiAI-ImageAddon.git
cd AnkiAI-ImageAddon
```

### 2. Setup Python environment

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install add-on locally for testing

```bash
python build.py install
```

## Cấu trúc thư mục

```
AnkiAI-ImageAddon/
├── AnkiAI_ImageAddon/           # Main add-on package
│   ├── __init__.py              # Entry point
│   ├── manifest.json            # Metadata
│   └── modules/
│       ├── config.py            # Configuration management
│       ├── ui.py                # User interface
│       ├── api_handler.py       # API integration
│       ├── image_handler.py     # Image processing
│       └── bg_handler.py        # Background operations
│
├── tests/                       # Unit tests
│   ├── test_config.py
│   ├── test_api_handler.py
│   ├── test_image_handler.py
│   └── test_ui.py
│
├── docs/                        # Documentation
│   ├── README.md
│   ├── SETUP.md
│   ├── ARCHITECTURE.md
│   └── DEVELOPMENT.md
│
├── build.py                     # Build script
├── requirements.txt             # Dependencies
└── .gitignore
```

## Làm việc với add-on

### Testing locally

1. **Build add-on**:
   ```bash
   python build.py install
   ```

2. **Khởi động Anki**:
   - Anki sẽ tự load add-on từ folder addons21

3. **Test các tính năng**:
   - Browse → Chọn thẻ → Chuột phải → "AnkiAI"

4. **Xem logs** (nếu cần debug):
   ```
   Tools > Add-ons > AnkiAI > View Files > debug.log
   ```

### Making changes

```python
# Ví dụ: Thêm new feature vào api_handler.py

from .modules.api_handler import OpenAIHandler

class OpenAIHandler:
    def generate_music(self, vocabulary):
        """NEW: Tạo nhạc thay vì ảnh"""
        # Implementation here
        pass
```

### Debugging

**Print statements**:
```python
# Dùng print() để debug (sẽ hiện ở console)
print(f"[DEBUG] Vocabulary: {vocabulary}")
```

**Anki console** (nếu available):
```
Tools > Add-ons > AnkiAI > View Files > debug.log
```

## Mở rộng add-on

### Thêm new API provider

```python
# Thêm vào modules/api_handler.py

class StabilityAIHandler:
    """Nếu muốn dùng Stable Diffusion thay vì DALL-E"""
    
    def __init__(self, api_key):
        self.api_key = api_key
    
    def generate_image(self, vocabulary, definition):
        # Gọi Stability AI API
        pass


# Sau đó update AIImageProvider:
class AIImageProvider:
    def __init__(self, ..., stability_key=None):
        self.stability = StabilityAIHandler(stability_key)
```

### Thêm new processing option

```python
# Ví dụ: Tự động thêm pronunciation

class AddImageWithPronunciationTask(ProcessingTask):
    def process_note(self, note):
        # 1. Tìm ảnh (như cũ)
        # 2. THÊM: Tạo audio pronunciation
        pronunciation_url = self.text_to_speech(vocabulary)
        # 3. Lưu audio file
        # 4. Chèn vào note
```

### Thêm new config option

```python
# modules/config.py

DEFAULT_CONFIG = {
    # ... existing config ...
    "enable_pronunciation": False,  # NEW
    "google_cloud_key": "",         # NEW
}

# modules/ui.py

class ConfigDialog:
    def init_ui(self):
        # ... existing UI ...
        # THÊM pronunciation checkbox
        self.pronunciation_check = QCheckBox("Enable pronunciation")
```

## Testing

### Unit tests

```bash
# Chạy tất cả tests
pytest

# Chạy specific test file
pytest tests/test_api_handler.py

# Chạy specific test
pytest tests/test_api_handler.py::test_openai_search_keyword

# Verbose output
pytest -v

# Coverage report
pytest --cov=AnkiAI_ImageAddon
```

### Integration testing

```python
# tests/test_integration.py

def test_full_workflow():
    """Test toàn bộ workflow từ đầu đến cuối"""
    
    # Setup
    config = get_config_manager()
    config.set("openai_api_key", FAKE_KEY)
    
    # Test
    ai_provider = AIImageProvider(FAKE_KEY)
    url = ai_provider.get_image_url("test", "test")
    
    assert url is not None
    assert "http" in url
```

## Code Style

### Follow PEP 8

```bash
# Check style
pylint AnkiAI_ImageAddon

# Auto-format
black AnkiAI_ImageAddon
```

### Docstrings

```python
def get_image_url(self, vocabulary: str, definition: str) -> str:
    """
    Lấy URL ảnh từ AI
    
    Args:
        vocabulary: Từ vựng tiếng Anh
        definition: Định nghĩa hoặc context
    
    Returns:
        URL của ảnh
    
    Raises:
        APIError: Nếu API call fail
    
    Example:
        >>> provider = AIImageProvider("sk-...")
        >>> url = provider.get_image_url("Apple", "A company")
        >>> print(url)
        "https://..."
    """
    # Implementation
    pass
```

### Type hints

```python
from typing import List, Optional, Dict, Tuple

def process_notes(
    note_ids: List[int],
    callback: Optional[Callable] = None
) -> Dict[str, int]:
    """Process multiple notes"""
    pass
```

## Common tasks

### Add new dependency

```bash
# Add to requirements.txt
echo "new-package==1.0.0" >> requirements.txt

# Install
pip install -r requirements.txt
```

### Update add-on version

```json
// manifest.json
{
    "version": "1.1.0"
}
```

### Build release

```bash
# Clean old builds
python build.py clean

# Build new version
python build.py build

# This creates AnkiAI_ImageAddon-1.1.0.ankiaddon
```

### Submit to AnkiWeb

1. Build add-on:
   ```bash
   python build.py build
   ```

2. Go to https://ankiweb.net/

3. Sign in > Add-ons > Share

4. Upload the .ankiaddon file

5. Fill in description (Vietnamese)

## Performance tips

### Optimize API calls

```python
# BAD: Tạo new instance mỗi lần
for note_id in note_ids:
    ai = AIImageProvider(key)  # ❌ Slow
    url = ai.get_image_url(...)

# GOOD: Reuse instance
ai = AIImageProvider(key)  # ✅ Fast
for note_id in note_ids:
    url = ai.get_image_url(...)
```

### Reduce network roundtrips

```python
# BAD: Call API 3 times
keyword = ai.generate_search_keyword(vocab, def)
image_url = unsplash.search(keyword)
image_data = requests.get(image_url)

# GOOD: Batch if possible
# (Depending on API)
```

### Cache results

```python
# Nếu tìm cùng keyword 2 lần, reuse result
cache = {}

def get_cached_image(keyword):
    if keyword in cache:
        return cache[keyword]  # ✅ Instant
    
    url = unsplash.search(keyword)
    cache[keyword] = url
    return url
```

## Troubleshooting

### "ImportError: No module named requests"

```bash
# Make sure you're in the virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Then reinstall
pip install -r requirements.txt
```

### "Cannot find Anki installation"

Make sure Anki is installed and the add-on is in correct folder:
- macOS: `~/Library/Application Support/Anki2/addons21/`
- Windows: `%APPDATA%\Anki2\addons21\`
- Linux: `~/.local/share/Anki2/addons21/`

### Anki not loading add-on

Check for syntax errors:
```bash
# Try importing module directly
python3 -c "from AnkiAI_ImageAddon import *"
```

If import fails, you'll see the error.

## Resources

- [Anki Add-on Development](https://addon-docs.ankiweb.net/)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Unsplash API](https://unsplash.com/oauth/applications)

## Support

- Report issues: GitHub Issues
- Ask questions: Anki Forums
- Discord community: [Link]

---

**Happy coding!** 🚀
