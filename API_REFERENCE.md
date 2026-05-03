# 📚 API Reference - AnkiAI

Hướng dẫn sử dụng các module của AnkiAI trong projects khác.

## Mục lục

1. [config.py](#configpy) - Configuration Management
2. [api_handler.py](#api_handlerpy) - AI Integration
3. [image_handler.py](#image_handlerpy) - Image Processing
4. [ui.py](#uipy) - UI Components
5. [bg_handler.py](#bg_handlerpy) - Background Processing

---

## config.py

Quản lý cấu hình của add-on.

### ConfigManager

```python
from AnkiAI_ImageAddon.modules.config import ConfigManager, get_config_manager

# Lấy singleton instance
config = get_config_manager()

# Get config value
api_key = config.get("openai_api_key")
mode = config.get("image_generation_mode", "dall-e")  # với default

# Set config value
config.set("vocabulary_field", "Front")

# Validate API keys
valid = config.validate_api_keys()
# Returns: {"openai": True, "unsplash": False}

# Reset to default
config.reset_to_default()

# Get all config as dict
all_config = config.get_all()
```

### Default Config

```python
{
    "openai_api_key": "",
    "unsplash_api_key": "",
    "image_generation_mode": "dall-e",  # "dall-e" hoặc "search"
    "vocabulary_field": "Mặt trước",
    "definition_field": "Định nghĩa",
    "image_field": "Ảnh",
    "image_download_timeout": 30,
    "max_concurrent_requests": 3,
    "auto_add_on_sync": False,
}
```

---

## api_handler.py

Tích hợp với AI services.

### OpenAIHandler

```python
from AnkiAI_ImageAddon.modules.api_handler import OpenAIHandler

openai = OpenAIHandler(api_key="sk-...")

# Option 1: Tạo ảnh bằng DALL-E
image_url = openai.generate_image(
    vocabulary="Apple",
    definition="A company",
    style="illustration"  # Optional
)
# Returns: "https://..."

# Option 2: Tạo từ khóa cho tìm kiếm
keyword = openai.generate_search_keyword(
    vocabulary="Apple",
    definition="A company"
)
# Returns: "Apple Inc headquarters"
```

### UnsplashHandler

```python
from AnkiAI_ImageAddon.modules.api_handler import UnsplashHandler

unsplash = UnsplashHandler(api_key="your-unsplash-key")

# Tìm ảnh
image_url = unsplash.search_image("Apple headquarters")
# Returns: "https://images.unsplash.com/..."
```

### PixabayHandler

```python
from AnkiAI_ImageAddon.modules.api_handler import PixabayHandler

pixabay = PixabayHandler(api_key="your-pixabay-key")

# Tìm ảnh (miễn phí)
image_url = pixabay.search_image("Apple")
# Returns: "https://pixabay.com/..."
```

### AIImageProvider (Wrapper)

```python
from AnkiAI_ImageAddon.modules.api_handler import AIImageProvider

# Mode 1: DALL-E (tạo ảnh)
provider = AIImageProvider(
    openai_key="sk-...",
    mode="dall-e"
)
url = provider.get_image_url("Apple", "A company")

# Mode 2: Search (tìm ảnh)
provider = AIImageProvider(
    openai_key="sk-...",
    mode="search",
    unsplash_key="...",
    pixabay_key="..."
)
url = provider.get_image_url("Apple", "A company")
```

### Error Handling

```python
from AnkiAI_ImageAddon.modules.api_handler import APIError

try:
    url = provider.get_image_url("Apple", "")
except APIError as e:
    print(f"API Error: {e}")
    # Handle error
```

---

## image_handler.py

Xử lý tải và lưu ảnh.

### ImageHandler

```python
from AnkiAI_ImageAddon.modules.image_handler import ImageHandler
from aqt import mw

image_handler = ImageHandler(mw)

# 1. Tải ảnh từ URL
image_data = image_handler.download_image(
    "https://example.com/image.jpg",
    timeout=30
)
# Returns: bytes

# 2. Lấy extension ảnh
extension = image_handler._detect_image_format(image_data)
# Returns: ".jpg"

# 3. Tạo tên file
filename = image_handler.get_image_filename(
    vocabulary="Apple",
    image_data=image_data
)
# Returns: "Apple_20240101_120000.jpg"

# 4. Lưu vào Anki (CRITICAL)
saved_filename = image_handler.save_image_to_anki(
    image_data=image_data,
    filename=filename
)
# Returns: "Apple_20240101_120000.jpg" (saved)

# 5. Chèn vào note
note = mw.col.get_note(note_id)
success = image_handler.insert_image_to_note(
    note=note,
    image_filename=saved_filename,
    image_field_name="Ảnh"
)
note.flush()  # IMPORTANT: Save changes

# OR: Full pipeline in one call
success, message = image_handler.process_image(
    url="https://example.com/image.jpg",
    note=note,
    vocabulary="Apple",
    image_field_name="Ảnh"
)
```

### Error Handling

```python
from AnkiAI_ImageAddon.modules.image_handler import ImageError

try:
    image_handler.download_image("bad-url")
except ImageError as e:
    print(f"Image Error: {e}")
```

### Supported Formats

- .jpg / .jpeg
- .png
- .gif
- .webp

---

## ui.py

UI components & helpers.

### BrowserMenuManager

```python
from AnkiAI_ImageAddon.modules.ui import BrowserMenuManager

browser_menu = BrowserMenuManager()

# Setup menu dalam Browser
def on_menu_click(browser):
    print("Menu clicked!")

browser_menu.setup_browser_menu(browser, on_menu_click)

# Lấy selected note IDs từ Browser
note_ids = browser_menu.get_selected_note_ids(browser)
# Returns: [123, 456, 789]

# Show dialogs
browser_menu.show_error("Title", "Error message")
browser_menu.show_warning("Title", "Warning message")
browser_menu.show_info("Title", "Info message")
replied = browser_menu.show_question("Title", "Question?")
# Returns: True if user clicked Yes
```

### FieldSelectionDialog

```python
from AnkiAI_ImageAddon.modules.ui import FieldSelectionDialog

available_fields = ["Front", "Back", "Image", "Definition"]

dialog = FieldSelectionDialog(
    model_name="Vocabulary",
    available_fields=available_fields,
    parent=browser
)

if dialog.exec() == FieldSelectionDialog.Accepted:
    vocab_field = dialog.selected_vocab_field
    definition_field = dialog.selected_definition_field
    image_field = dialog.selected_image_field
    print(f"Selected: {vocab_field}, {definition_field}, {image_field}")
```

### ConfigDialog

```python
from AnkiAI_ImageAddon.modules.ui import ConfigDialog

config_dialog = ConfigDialog(parent=browser)

if config_dialog.exec() == ConfigDialog.Accepted:
    config = config_dialog.get_config()
    # Returns: {
    #     "openai_api_key": "sk-...",
    #     "mode": "dall-e",
    #     "unsplash_api_key": ""
    # }
```

### Utility function

```python
from AnkiAI_ImageAddon.modules.ui import get_note_data

note = mw.col.get_note(note_id)
vocabulary, definition = get_note_data(note)
# Returns: ("Apple", "A company")
# Automatically removes HTML tags and strips whitespace
```

---

## bg_handler.py

Background processing.

### BackgroundProcessor

```python
from AnkiAI_ImageAddon.modules.bg_handler import BackgroundProcessor

processor = BackgroundProcessor()

# Define process function
def process_note(note):
    # Do something with note
    # Return (success: bool, message: str)
    return True, "Success"

# Run in background
processor.process_cards_in_background(
    note_ids=[1, 2, 3, 4, 5],
    process_func=process_note,
    on_progress=lambda cur, tot, msg: print(f"{msg} ({cur}/{tot})"),
    on_success=lambda res: print(f"Done: {res}"),
    on_error=lambda err: print(f"Error: {err}"),
    title="Processing 5 cards"
)

# Other optional callbacks
processor.is_processing()  # Returns: True/False
processor.cancel()  # Cancel current processing
```

### ProcessingTask

```python
from AnkiAI_ImageAddon.modules.bg_handler import ProcessingTask

class MyCustomTask(ProcessingTask):
    def __init__(self):
        super().__init__("My Task Name")
    
    def process_note(self, note):
        """Override this method"""
        try:
            # Do something
            vocabulary = note["Mặt trước"]
            # Process...
            return True, f"Processed {vocabulary}"
        except Exception as e:
            return False, str(e)

# Use custom task
task = MyCustomTask()

def process_func(note):
    return task.process_note(note)

processor.process_cards_in_background(
    note_ids=[...],
    process_func=process_func,
    on_success=lambda res: print(task.get_summary())
)

# Get summary
summary = task.get_summary()
# Returns: {
#     "task_name": "My Task Name",
#     "total_processed": 100,
#     "successful": 95,
#     "failed": 5,
#     "results": [...],
#     "errors": [...]
# }
```

### ProgressDialog

```python
from AnkiAI_ImageAddon.modules.bg_handler import ProgressDialog

progress = ProgressDialog("Processing images...", parent=mainwindow)
progress.show()

for i in range(1, 101):
    progress.update_progress(i, 100, f"Processing image {i}")
    # Do work...
    
    if progress.is_cancelled():
        break

progress.close()
```

---

## Complete Example

### Scenario: Thêm description vào note từ Wikipedia

```python
from aqt import mw
from AnkiAI_ImageAddon.modules.config import get_config_manager
from AnkiAI_ImageAddon.modules.ui import BrowserMenuManager
from AnkiAI_ImageAddon.modules.bg_handler import ProcessingTask, BackgroundProcessor

# Get browser and selected notes
def on_add_descriptions(browser):
    note_ids = BrowserMenuManager().get_selected_note_ids(browser)
    
    if not note_ids:
        BrowserMenuManager().show_warning("Warning", "Select some notes")
        return
    
    # Define task
    class WikiDescriptionTask(ProcessingTask):
        def process_note(self, note):
            try:
                word = note["Mặt trước"].strip()
                
                # Fetch from Wikipedia API
                import requests
                response = requests.get(
                    "https://en.wikipedia.org/api/rest_v1/page/summary/" + word,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    description = data.get("extract", "")
                    
                    # Add to note
                    if "Mô tả" in note:
                        note["Mô tả"] = description
                        note.flush()
                        return True, f"Added for {word}"
                
                return False, "No Wikipedia entry"
            
            except Exception as e:
                return False, str(e)
    
    # Run
    task = WikiDescriptionTask()
    processor = BackgroundProcessor()
    
    processor.process_cards_in_background(
        note_ids=note_ids,
        process_func=task.process_note,
        on_success=lambda res: print(task.get_summary()),
        title="Adding Wikipedia descriptions"
    )

# Hook into browser
from aqt import gui_hooks

def setup_menu(browser):
    action = browser.form.menu_Cards.addAction("Add Wikipedia descriptions")
    action.triggered.connect(lambda: on_add_descriptions(browser))

gui_hooks.browser_menus_did_init.append(setup_menu)
```

---

## Exceptions

```python
from AnkiAI_ImageAddon.modules.api_handler import APIError
from AnkiAI_ImageAddon.modules.image_handler import ImageError

try:
    # API call
    url = provider.get_image_url(...)
except APIError:
    # Handle API errors
    pass

try:
    # Image processing
    image_handler.download_image(...)
except ImageError:
    # Handle image errors
    pass
```

---

## Best Practices

1. **Always use get_config_manager() singleton**
   ```python
   # ✅ GOOD
   config = get_config_manager()
   
   # ❌ BAD
   config = ConfigManager()  # Creates new instance
   ```

2. **Call note.flush() after modifications**
   ```python
   # ✅ GOOD
   note["Field"] = "value"
   note.flush()
   
   # ❌ BAD
   note["Field"] = "value"  # Changes not saved
   ```

3. **Use mw.col.media.writeData() for images**
   ```python
   # ✅ GOOD
   mw.col.media.writeData(filename, image_data)
   
   # ❌ BAD
   with open(path, 'wb') as f:  # Not synced to AnkiWeb
       f.write(image_data)
   ```

4. **Handle exceptions gracefully**
   ```python
   # ✅ GOOD
   try:
       url = provider.get_image_url(...)
   except APIError as e:
       logger.error(f"API error: {e}")
       return False, str(e)
   ```

5. **Use background processing for long tasks**
   ```python
   # ✅ GOOD (doesn't freeze UI)
   processor.process_cards_in_background(...)
   
   # ❌ BAD (freezes UI)
   for note_id in note_ids:
       process_note(note_id)  # Blocking
   ```

---

**Last updated**: 2024
**API Version**: 1.0
