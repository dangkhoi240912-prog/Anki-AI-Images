"""
AnkiAI - Tự động thêm ảnh bằng AI
Main entry point cho add-on
"""

from aqt import mw
from aqt.browser import Browser
from aqt.qt import QMessageBox, QDialog
import sys
import os

# Import modules
from .modules.config import get_config_manager
from .modules.ui import BrowserMenuManager, FieldSelectionDialog, ConfigDialog, get_note_data
from .modules.api_handler import AIImageProvider, APIError
from .modules.image_handler import ImageHandler, ImageError
from .modules.bg_handler import BackgroundProcessor, ProcessingTask


# Global instances
browser_menu_manager = None
image_handler = None
bg_processor = None
config_manager = None


class AddImageTask(ProcessingTask):
    """Task để tự động thêm ảnh vào từng thẻ"""
    
    def __init__(self, ai_provider, image_handler_obj, vocab_field: str,
                 definition_field: str, image_field: str):
        super().__init__("Add Images with AI")
        self.ai_provider = ai_provider
        self.image_handler = image_handler_obj
        self.vocab_field = vocab_field
        self.definition_field = definition_field
        self.image_field = image_field
    
    def process_note(self, note) -> tuple:
        """
        Xử lý một note: Lấy từ vựng -> Gọi AI -> Tải ảnh -> Chèn vào note
        
        Args:
            note: Anki Note object
        
        Returns:
            Tuple (success, message)
        """
        try:
            # 1. Lấy từ vựng và định nghĩa từ note
            vocabulary = note[self.vocab_field].strip()
            definition = note[self.definition_field].strip() if self.definition_field in note else ""
            
            if not vocabulary:
                return False, "Từ vựng trống"
            
            # Bỏ HTML tags
            import re
            vocabulary = re.sub(r"<[^>]+>", "", vocabulary)
            definition = re.sub(r"<[^>]+>", "", definition)
            
            print(f"[TASK] Processing: {vocabulary}")
            
            # 2. Kiểm tra xem đã có ảnh không
            current_image = note[self.image_field] if self.image_field in note else ""
            if current_image and "<img" in current_image:
                return False, "Đã có ảnh"
            
            # 3. Gọi AI để lấy URL ảnh
            print(f"[TASK] Calling AI for '{vocabulary}'...")
            image_url = self.ai_provider.get_image_url(vocabulary, definition)
            
            if not image_url:
                return False, "AI không tìm được ảnh"
            
            # 4. Xử lý ảnh
            success, message = self.image_handler.process_image(
                image_url, note, vocabulary, self.image_field
            )
            
            if success:
                # 5. Lưu note
                try:
                    note.flush()
                    return True, f"Thêm ảnh thành công: {vocabulary}"
                except Exception as e:
                    return False, f"Lỗi lưu note: {str(e)}"
            else:
                return False, message
        
        except APIError as e:
            return False, f"API Error: {str(e)}"
        except ImageError as e:
            return False, f"Image Error: {str(e)}"
        except Exception as e:
            return False, f"Lỗi không xác định: {str(e)}"


def on_browser_menu_add_images(browser: Browser):
    """
    Callback khi người dùng chọn "Tự động thêm ảnh"
    
    Quy trình:
    1. Lấy danh sách thẻ được chọn
    2. Hiển thị dialog chọn fields
    3. Hiển thị dialog cấu hình API
    4. Chạy xử lý background
    """
    
    # Bước 1: Lấy danh sách thẻ được chọn
    note_ids = browser_menu_manager.get_selected_note_ids(browser)
    
    if not note_ids:
        browser_menu_manager.show_warning(
            "Cảnh báo",
            "Vui lòng chọn ít nhất 1 thẻ"
        )
        return
    
    print(f"[ADDON] Selected {len(note_ids)} notes")
    
    # Force reload config từ Anki (meta.json) trước khi kiểm tra
    config_manager.reload()
    
    # Bước 2: Kiểm tra API key (Groq hoặc Gemini)
    has_groq = bool(config_manager.get("groq_api_key"))
    has_gemini = bool(config_manager.get("gemini_api_key"))
    
    if not has_groq and not has_gemini:
        reply = browser_menu_manager.show_question(
            "Cấu hình",
            "Chưa có AI provider nào được cấu hình (Groq hoặc Gemini).\nBạn muốn cấu hình ngay bây giờ?"
        )
        
        if reply:
            config_dialog = ConfigDialog(browser, existing_config=config_manager.get_all())
            if config_dialog.exec() == QDialog.DialogCode.Accepted:
                try:
                    config = config_dialog.get_config()
                    config_manager.set("groq_api_key", config.get("groq_api_key", ""))
                    config_manager.set("gemini_api_key", config.get("gemini_api_key", ""))
                    config_manager.set("gemini_eval_api_key", config.get("gemini_eval_api_key", ""))  # v4.0
                    config_manager.set("gemini_backup_api_key", config.get("gemini_backup_api_key", ""))  # v4.0
                    config_manager.set("unsplash_api_key", config.get("unsplash_api_key", ""))
                    config_manager.set("pixabay_api_key", config.get("pixabay_api_key", ""))
                    config_manager.set("pexels_api_key", config.get("pexels_api_key", ""))
                    config_manager.set("google_api_key", config.get("google_api_key", ""))  # v4.0
                    config_manager.set("google_cx", config.get("google_cx", ""))  # v4.0
                    config_manager.set("enable_ai_evaluation", config.get("enable_ai_evaluation", True))  # v4.0
                except ValueError as e:
                    browser_menu_manager.show_error("Lỗi cấu hình", str(e))
                    return
            else:
                return
        else:
            return
    
    # Bước 3: Lấy note đầu tiên để xác định fields
    first_note = mw.col.get_note(note_ids[0])
    available_fields = list(first_note.keys())
    
    # Bước 4: Hiển thị dialog chọn fields (nếu chưa cấu hình)
    vocab_field = config_manager.get("vocabulary_field", "Mặt trước")
    definition_field = config_manager.get("definition_field", "Định nghĩa")
    image_field = config_manager.get("image_field", "Ảnh")
    
    # Kiểm tra xem fields còn hợp lệ không
    if vocab_field not in available_fields or image_field not in available_fields:
        field_dialog = FieldSelectionDialog(
            first_note.note_type()["name"],
            available_fields,
            browser
        )
        
        if field_dialog.exec() == QDialog.DialogCode.Accepted:
            vocab_field = field_dialog.selected_vocab_field
            definition_field = field_dialog.selected_definition_field
            image_field = field_dialog.selected_image_field
            
            # Lưu vào config
            config_manager.set("vocabulary_field", vocab_field)
            config_manager.set("definition_field", definition_field)
            config_manager.set("image_field", image_field)
        else:
            return
    
    # Bước 5: Chuẩn bị AI provider với tất cả providers (v4.0 - optimized)
    try:
        # Force reload config từ Anki (meta.json)
        config_manager.reload()
        
        # AI Providers
        gemini_key = config_manager.get("gemini_api_key", "")
        gemini_eval_key = config_manager.get("gemini_eval_api_key", "")  # v4.0
        gemini_backup_key = config_manager.get("gemini_backup_api_key", "")  # v4.0
        groq_key = config_manager.get("groq_api_key", "")
        use_ollama = config_manager.get("use_ollama", False)
        ollama_url = config_manager.get("ollama_url", "http://localhost:11434")
        
        # Image Providers (7 total)
        unsplash_key = config_manager.get("unsplash_api_key", "")
        pixabay_key = config_manager.get("pixabay_api_key", "")
        pexels_key = config_manager.get("pexels_api_key", "")
        wallhaven_key = config_manager.get("wallhaven_api_key", "")
        google_api_key = config_manager.get("google_api_key", "")  # v4.0
        google_cx = config_manager.get("google_cx", "")  # v4.0
        
        # AI Evaluation Settings (v4.0)
        enable_ai_evaluation = config_manager.get("enable_ai_evaluation", True)
        
        # Smart Selection Settings
        enable_smart_selection = config_manager.get("enable_smart_selection", True)
        max_concurrent_providers = config_manager.get("max_concurrent_providers", 6)
        
        ai_provider = AIImageProvider(
            # AI Providers
            gemini_key=gemini_key,
            gemini_eval_key=gemini_eval_key,
            gemini_backup_key=gemini_backup_key,
            groq_key=groq_key,
            use_ollama=use_ollama,
            ollama_url=ollama_url,
            # Image Providers
            unsplash_key=unsplash_key,
            pixabay_key=pixabay_key,
            pexels_key=pexels_key,
            wallhaven_key=wallhaven_key,
            google_api_key=google_api_key,
            google_cx=google_cx,
            # Settings
            enable_smart_selection=enable_smart_selection,
            enable_ai_evaluation=enable_ai_evaluation,
            max_concurrent_providers=max_concurrent_providers
        )
    except APIError as e:
        browser_menu_manager.show_error("Lỗi API", str(e))
        return
    
    # Bước 6: Hiển thị confirm dialog
    confirm_msg = f"""Bạn sắp thêm ảnh AI cho {len(note_ids)} thẻ.

Chế độ: Search (dùng Gemini/Groq/Ollama + Image Provider)
Field từ vựng: {vocab_field}
Field ảnh: {image_field}

Tiếp tục?"""
    
    if not browser_menu_manager.show_question("Xác nhận", confirm_msg):
        return
    
    # Bước 7: Chạy background processing
    task = AddImageTask(
        ai_provider,
        image_handler,
        vocab_field,
        definition_field,
        image_field
    )
    
    def on_progress(current, total, message):
        print(f"[PROGRESS] {message}")
    
    def on_success(result):
        print(f"[SUCCESS] {result}")
        successful = result.get("results", [])
        failed = result.get("errors", [])
        
        summary = f"""Hoàn thành!

Thành công: {len(successful)}
Thất bại: {len(failed)}"""
        
        if failed:
            summary += "\n\nLỗi:"
            for error in failed[:5]:  # Hiển thị 5 lỗi đầu
                summary += f"\n- {error.get('error', 'Unknown')}"
        
        browser_menu_manager.show_info("Kết quả", summary)
        
        # Refresh browser
        browser.search()
    
    def on_error(error_msg):
        print(f"[ERROR] {error_msg}")
        browser_menu_manager.show_error("Lỗi", error_msg)
    
    # Xử lý từng note ở background
    def process_func(note):
        success, message = task.process_note(note)
        return success, message
    
    bg_processor.process_cards_in_background(
        note_ids,
        process_func,
        on_progress=on_progress,
        on_success=on_success,
        on_error=on_error,
        title=f"AnkiAI - Đang thêm ảnh ({len(note_ids)} thẻ)"
    )


def open_config_dialog():
    """Mở dialog cấu hình từ Addon Manager"""
    global config_manager
    
    # Luôn tạo mới config_manager để đảm bảo lấy config mới nhất từ Anki
    config_manager = get_config_manager()
    
    # Force reload config từ Anki
    fresh_config = mw.addonManager.getConfig(config_manager.ADDON_MODULE)
    if fresh_config:
        config_manager.config = fresh_config
        print(f"[open_config_dialog] Loaded fresh config from Anki")
    else:
        print(f"[open_config_dialog] No config found, using defaults")
    
    print(f"[open_config_dialog] Current config: {config_manager.get_all()}")
    
    config_dialog = ConfigDialog(mw, existing_config=config_manager.get_all())
    if config_dialog.exec() == QDialog.DialogCode.Accepted:
        try:
            config = config_dialog.get_config()
            print(f"[open_config_dialog] Saving config: {config}")
            # Lưu tất cả config values
            config_manager.set("groq_api_key", config.get("groq_api_key", ""))
            config_manager.set("gemini_api_key", config.get("gemini_api_key", ""))
            config_manager.set("use_ollama", config.get("use_ollama", False))
            config_manager.set("ollama_url", config.get("ollama_url", "http://localhost:11434"))
            config_manager.set("unsplash_api_key", config.get("unsplash_api_key", ""))
            config_manager.set("pixabay_api_key", config.get("pixabay_api_key", ""))
            config_manager.set("pexels_api_key", config.get("pexels_api_key", ""))
            config_manager.set("image_generation_mode", config.get("image_generation_mode", "search"))
            
            # Force save config
            config_manager.save_config()
            
            print(f"[open_config_dialog] Config saved. New config: {config_manager.get_all()}")
            QMessageBox.information(mw, "AnkiAI", "Đã lưu cấu hình thành công! ✓")
        except ValueError as e:
            QMessageBox.warning(mw, "Lỗi cấu hình", str(e))


def on_config_changed(new_config):
    """Callback khi config thay đổi từ Anki JSON editor"""
    global config_manager
    if config_manager is not None:
        config_manager.config = new_config
        print("[ADDON] Config updated from Anki editor")


def setup_addon():
    """Setup add-on khi Anki khởi động"""
    global browser_menu_manager, image_handler, bg_processor, config_manager
    
    print("[ADDON] Initializing AnkiAI...")
    
    try:
        # Khởi tạo các components
        config_manager = get_config_manager()
        browser_menu_manager = BrowserMenuManager()
        image_handler = ImageHandler(mw)
        bg_processor = BackgroundProcessor()
        
        # Hook vào Browser
        from aqt import gui_hooks
        
        def setup_browser_menus(browser):
            browser_menu_manager.setup_browser_menu(
                browser,
                on_browser_menu_add_images
            )
        
        gui_hooks.browser_menus_did_init.append(setup_browser_menus)
        
        print("[ADDON] AnkiAI initialized successfully!")
    
    except Exception as e:
        print(f"[ADDON] Error during initialization: {e}")
        import traceback
        traceback.print_exc()


# === Đăng ký config action NGAY khi addon được load (trước khi mở profile) ===
_addon_dir = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
mw.addonManager.setConfigAction(_addon_dir, open_config_dialog)
mw.addonManager.setConfigUpdatedAction(_addon_dir, on_config_changed)

# Hook vào Anki startup
from aqt import gui_hooks
gui_hooks.profile_did_open.append(setup_addon)
