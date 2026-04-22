# 🏗️ Kiến trúc AnkiAI Add-on

## Tổng quan cấu trúc

```
AnkiAI_ImageAddon/
├── __init__.py              # Main entry point - orchestrate toàn bộ
├── manifest.json            # Metadata của add-on
│
└── modules/                 # Các component tách biệt
    ├── __init__.py
    ├── config.py            # Quản lý cầu hình
    ├── ui.py                # Giao diện & Browser menu (Giai đoạn 1)
    ├── api_handler.py       # Tích hợp AI API (Giai đoạn 2)
    ├── image_handler.py     # Tải & lưu ảnh (Giai đoạn 3)
    └── bg_handler.py        # Background processing (Giai đoạn 4)
```

## Flow Diagram

```
Người dùng Anki
     ↓
[Open Browser & Select Cards]
     ↓
[Right-click → "AnkiAI: Tự động thêm ảnh"]
     ↓
ui.py: on_browser_menu_add_images()
     ├─→ Check API key
     ├─→ Show field selection dialog
     └─→ Initialize AIImageProvider & ImageHandler
           ↓
bg_handler.py: BackgroundProcessor
     └─→ For each note_id in selected:
           ├─→ Get note from database
           ├─→ Extract vocabulary & definition
           ├─→ Process via AddImageTask
           │   ├─→ Call api_handler.get_image_url()
           │   │   ├─→ Option A: OpenAI.generate_image() (DALL-E)
           │   │   └─→ Option B: ChatGPT + Unsplash.search_image()
           │   ├─→ Call image_handler.download_image()
           │   ├─→ Call image_handler.save_image_to_anki()
           │   │   └─→ mw.col.media.writeData() [CRITICAL]
           │   └─→ Call image_handler.insert_image_to_note()
           ├─→ note.flush()
           └─→ Show progress bar
     ↓
[Show Results Dialog]
```

## Mô tả từng Module

### 1️⃣ config.py - Quản lý cấu hình

**Trách nhiệm**:
- Lấy/lưu config từ Anki
- Validate API keys
- Cung cấp default values

**Key Classes**:
- `ConfigManager`: Singleton quản lý toàn bộ config

**Default Config**:
```python
{
    "openai_api_key": "",
    "unsplash_api_key": "",
    "image_generation_mode": "dall-e",  # hoặc "search"
    "vocabulary_field": "Mặt trước",
    "definition_field": "Định nghĩa",
    "image_field": "Ảnh",
    "image_download_timeout": 30,
    "max_concurrent_requests": 3,
}
```

**Public API**:
```python
config_manager.get(key, default)
config_manager.set(key, value)
config_manager.validate_api_keys()
```

---

### 2️⃣ ui.py - User Interface (Giai đoạn 1)

**Trách nhiệm**:
- Tạo Browser context menu
- Lấy danh sách thẻ được chọn
- Dialog cho người dùng chọn field
- Dialog cấu hình API

**Key Classes**:
- `BrowserMenuManager`: Hook vào Browser, show/hide menu
- `FieldSelectionDialog`: Dialog chọn vocabulary/definition/image field
- `ConfigDialog`: Dialog nhập API key

**Public API**:
```python
browser_menu_manager.setup_browser_menu(browser, callback)
browser_menu_manager.get_selected_note_ids(browser)  # → [1, 2, 3]
```

**Event Flow**:
1. User right-click in Browser
2. Menu hoàn → "AnkiAI: Tự động thêm ảnh"
3. `on_browser_menu_add_images()` được gọi
4. Lấy selected note IDs
5. Show Dialog (nếu cần)

---

### 3️⃣ api_handler.py - AI Integration (Giai đoạn 2)

**Trách nhiệm**:
- Gọi OpenAI API (ChatGPT + DALL-E)
- Gọi Unsplash/Pixabay API
- Chọn provider phù hợp

**Key Classes**:
- `OpenAIHandler`: ChatGPT & DALL-E
  - `generate_search_keyword()`: ChatGPT → từ khóa
  - `generate_image()`: DALL-E → ảnh
  
- `UnsplashHandler`: Tìm ảnh từ Unsplash
  - `search_image()`: keyword → URL
  
- `PixabayHandler`: Tìm ảnh từ Pixabay
  - `search_image()`: keyword → URL

- `AIImageProvider`: Wrapper chọn mode
  - `get_image_url()`: Gọi provider thích hợp

**Example Usage**:
```python
# Mode A: DALL-E
provider = AIImageProvider(openai_key="sk-...", mode="dall-e")
url = provider.get_image_url("Apple", "A company")

# Mode B: Search
provider = AIImageProvider(
    openai_key="sk-...",
    mode="search",
    unsplash_key="..."
)
url = provider.get_image_url("Apple", "A company")
```

**Error Handling**:
- Timeout: Retry 3 lần
- Invalid response: Throw APIError
- Rate limiting: Wait & retry

---

### 4️⃣ image_handler.py - Image Processing (Giai đoạn 3)

**Trách nhiệm**:
- Tải ảnh từ URL
- Lưu vào thư mục média của Anki
- Chèn HTML vào note
- Detect image format

**Key Classes**:
- `ImageHandler`:
  - `download_image()`: URL → bytes
  - `get_image_filename()`: Tạo tên file duy nhất
  - `_detect_image_format()`: Magic bytes → extension
  - `save_image_to_anki()`: bytes → mw.col.media.writeData()
  - `insert_image_to_note()`: HTML → note field
  - `process_image()`: Full pipeline

**CRITICAL**: `mw.col.media.writeData()`

Anki sẽ:
- Lưu file vào thư mục media
- Tự động đồng bộ lên AnkiWeb
- Track dependencies

**Example Usage**:
```python
image_handler = ImageHandler(mw)

# 1. Tải ảnh
image_data = image_handler.download_image("https://...")

# 2. Lưu vào Anki
filename = image_handler.save_image_to_anki(image_data, "apple.jpg")

# 3. Chèn vào note
image_handler.insert_image_to_note(note, filename, "Ảnh")
note.flush()
```

**Supported Formats**: .jpg, .png, .gif, .webp

---

### 5️⃣ bg_handler.py - Background Processing (Giai đoạn 4)

**Trách nhiệm**:
- Xử lý hàng ngàn thẻ mà không freeze UI
- Hiển thị thanh tiến trình
- Handle cancellation

**Key Classes**:
- `BackgroundProcessor`:
  - `process_cards_in_background()`: Chạy ngầm
  - `cancel()`: Dừng xử lý
  
- `ProcessingTask`: Base class cho công việc
  - `process_note()`: Xử lý 1 note (override)
  - `get_summary()`: Tóm tắt kết quả

- `ProgressDialog`: Hiển thị tiến trình (Qt)

**Sử dụng Anki's QueryOp**:
```python
op = QueryOp(mw, background_work, on_done)
op.with_progress("Title").run_in_background()
```

Ưu điểm:
- Non-blocking UI
- Built-in progress bar
- Proper exception handling

**Example Usage**:
```python
processor = BackgroundProcessor()

def process_note(note):
    # Do something with note
    return success, message

processor.process_cards_in_background(
    note_ids=[1, 2, 3],
    process_func=process_note,
    on_progress=lambda cur, tot, msg: print(f"{cur}/{tot}"),
    on_success=lambda res: print("Done!"),
    on_error=lambda err: print(f"Error: {err}")
)
```

---

### 🎯 __init__.py - Main Orchestrator

**Trách nhiệm**:
- Setup add-on khi Anki khởi động
- Khởi tạo tất cả components
- Định nghĩa AddImageTask
- Hook vào browser menus

**Key Classes**:
- `AddImageTask(ProcessingTask)`: Công việc chính
  - Lấy vocabulary/definition
  - Gọi AI
  - Tải ảnh
  - Chèn vào note

**Hooks**:
- `profile_did_open`: Hook Anki startup
- `browser_menus_did_init`: Hook Browser menu

**Global Instances**:
```python
config_manager = get_config_manager()
browser_menu_manager = BrowserMenuManager()
image_handler = ImageHandler(mw)
bg_processor = BackgroundProcessor()
```

---

## Design Patterns

### 1. Singleton Pattern
```python
# config.py
config_manager = None

def get_config_manager():
    global config_manager
    if config_manager is None:
        config_manager = ConfigManager()
    return config_manager
```

### 2. Strategy Pattern (cho AI provider)
```python
# api_handler.py
AIImageProvider.mode = "dall-e" or "search"
# Tự động chọn strategy phù hợp
```

### 3. Task Pattern (cho background)
```python
# bg_handler.py
class ProcessingTask:
    def process_note(self, note):
        # Override trong subclass
        pass
```

### 4. Callback Pattern
```python
# __init__.py
processor.process_cards_in_background(
    ...,
    on_progress=callback,
    on_success=callback,
    on_error=callback
)
```

---

## Sequence Diagram

```
Browser User
    │
    ├─→ [1. Select cards]
    │
    ├─→ [2. Right-click]
    │       │
    │       └─→ ui.show_menu()
    │
    ├─→ [3. Click "AnkiAI"]
    │       │
    │       └─→ on_browser_menu_add_images()
    │           ├─→ Get selected note IDs
    │           ├─→ Check & validate API key
    │           ├─→ Show FieldSelectionDialog
    │           ├─→ Show confirm dialog
    │           └─→ Start background process
    │
    └─→ [4. Wait for progress]
            (other Anki operations can continue)
            │
            └─→ bg_handler.QueryOp
                ├─→ For each note:
                │   ├─→ AddImageTask.process_note()
                │   │   ├─→ Get vocabulary/definition
                │   │   ├─→ api_handler.get_image_url()
                │   │   ├─→ image_handler.download_image()
                │   │   ├─→ image_handler.save_image_to_anki()
                │   │   └─→ image_handler.insert_image_to_note()
                │   ├─→ note.flush()
                │   └─→ Call on_progress callback
                │
                └─→ Call on_success/on_error callback
                    └─→ Show results dialog
```

---

## Error Handling Strategy

### Levels:

1. **API Layer** (api_handler.py)
   - Try 3 times nếu timeout
   - Throw APIError nếu fail

2. **Image Layer** (image_handler.py)
   - Try 3 times tải ảnh
   - Detect format dynamically
   - Throw ImageError nếu fail

3. **Task Layer** (__init__.py)
   - Catch APIError & ImageError
   - Return (success, message)
   - Log mỗi error

4. **Background Layer** (bg_handler.py)
   - Catch Task exceptions
   - Add to errors list
   - Continue processing

5. **UI Layer** (ui.py)
   - Show summary: X failed, Y succeeded
   - Show detailed errors

---

## Performance Considerations

### Optimization:

1. **Batch Processing**
   - Xử lý 100-200 thẻ / lần
   - Không hơn → RAM overflow

2. **Timeout Settings**
   - Download: 30s
   - API calls: 10s
   - Retry: 3x

3. **Concurrent Requests**
   - Default: 3 parallel
   - Tăng → rate limit risk
   - Giảm → chậm hơn

4. **Cache**
   - Có thể cache từ khóa
   - Nếu vocabulary = "Apple" từng tìm → reuse

---

## Testing Strategy

### Unit tests:
```python
# test_config.py
def test_get_config()
def test_set_config()
def test_validate_api_keys()

# test_api_handler.py
def test_openai_search_keyword()
def test_openai_generate_image()
def test_unsplash_search()

# test_image_handler.py
def test_download_image()
def test_detect_format()
def test_save_to_anki()

# test_ui.py
def test_get_selected_notes()
def test_field_selection_dialog()
```

### Integration tests:
```python
# test_integration.py
def test_full_workflow():
    # Select cards → API → Download → Save
    pass
```

---

## Security Considerations

1. **API Keys**
   - Stored locally, never transmitted to 3rd party
   - Hidden in config dialog (placeholder)
   - Never logged

2. **Images**
   - Downloaded to local machine
   - Synced through Anki's official mechanism
   - No metadata leakage

3. **Data Privacy**
   - Vocabulary sent to OpenAI (unavoidable)
   - Anki data not shared elsewhere
   - GDPR compliant

---

## Future Improvements

1. **Cache search keywords** để tránh re-call AI
2. **Support video ảnh** (animated)
3. **Batch API calls** thay vì individual
4. **Custom prompts** cho DALL-E
5. **Image templates** (add borders, text, etc.)
6. **Auto-retry** logic tuyên chỉnh
7. **Statistics dashboard** (cost, success rate)
8. **Undo last batch** functionality

---

**Architecture Version**: 1.0
**Last Updated**: 2024
