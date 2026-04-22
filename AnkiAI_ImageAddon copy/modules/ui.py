"""
UI Handler Module - Giao diện người dùng & Browser Context Menu
Giai đoạn 1: Tạo menu trong Browser và trích xuất dữ liệu thẻ
"""

from aqt import mw
from aqt.browser import Browser
from aqt.qt import QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton
from typing import List, Optional
import functools


class BrowserMenuManager:
    """Quản lý context menu trong Browser"""
    
    def __init__(self):
        """Khởi tạo BrowserMenuManager"""
        self.browser: Optional[Browser] = None
    
    def setup_browser_menu(self, browser: Browser, callback_add_images: callable):
        """
        Hook vào Browser để thêm context menu
        
        Cách dùng: Người dùng bôi đen 100 thẻ, nhấn phải chuột, chọn "Tự động thêm ảnh bằng AI"
        
        Args:
            browser: Anki Browser window
            callback_add_images: Function được gọi khi người dùng chọn menu
        """
        self.browser = browser
        
        # Lấy danh sách các action trong context menu
        # Phiên bản cũ: browser.form.searchEdit.customContextMenuRequested.connect()
        # Phiên bản mới: Hook browser_menus_did_init
        
        # Tạo action cho menu
        try:
            # Phương pháp mới (Anki 24.04+)
            action = browser.form.menu_Cards.addAction("AnkiAI: Tự động thêm ảnh bằng AI")
            action.triggered.connect(lambda: callback_add_images(browser))
            print("[AnkiAI] Menu added to Cards menu")
        except Exception as e1:
            print(f"[AnkiAI] Failed to add to Cards menu: {e1}")
            # Thử menu_Notes (Anki 25+)
            try:
                action = browser.form.menu_Notes.addAction("AnkiAI: Tự động thêm ảnh bằng AI")
                action.triggered.connect(lambda: callback_add_images(browser))
                print("[AnkiAI] Menu added to Notes menu")
            except Exception as e2:
                print(f"[AnkiAI] Failed to add to Notes menu: {e2}")
                # Fallback: Dùng phương pháp cũ
                try:
                    action = browser.menuBar().addAction("AnkiAI: Tự động thêm ảnh")
                    action.triggered.connect(lambda: callback_add_images(browser))
                    print("[AnkiAI] Menu added to menuBar")
                except Exception as e3:
                    print(f"[AnkiAI] Error setting up browser menu: {e3}")
    
    def get_selected_note_ids(self, browser: Browser) -> List[int]:
        """
        Lấy danh sách Note IDs của các thẻ được chọn
        
        Args:
            browser: Anki Browser window
        
        Returns:
            Danh sách Note IDs
        """
        try:
            # Cách lấy thẻ được chọn trong Browser
            selected_cids = browser.selected_cards()
            
            if not selected_cids:
                return []
            
            # Convert card IDs sang Note IDs
            note_ids = set()
            for cid in selected_cids:
                card = mw.col.get_card(cid)
                note_ids.add(card.nid)
            
            return list(note_ids)
        
        except Exception as e:
            print(f"Error getting selected note IDs: {e}")
            return []
    
    def show_error(self, title: str, message: str):
        """Hiển thị lỗi"""
        QMessageBox.critical(self.browser, title, message)
    
    def show_warning(self, title: str, message: str):
        """Hiển thị cảnh báo"""
        QMessageBox.warning(self.browser, title, message)
    
    def show_info(self, title: str, message: str):
        """Hiển thị thông tin"""
        QMessageBox.information(self.browser, title, message)
    
    def show_question(self, title: str, message: str) -> bool:
        """Hiển thị câu hỏi, trả về True nếu người dùng chọn Yes"""
        reply = QMessageBox.question(self.browser, title, message)
        return reply == QMessageBox.StandardButton.Yes


class FieldSelectionDialog(QDialog):
    """Dialog cho người dùng chọn các field"""
    
    def __init__(self, model_name: str, available_fields: List[str], parent=None):
        """
        Khởi tạo FieldSelectionDialog
        
        Args:
            model_name: Tên của Note Type
            available_fields: Danh sách các field có sẵn
            parent: Parent widget
        """
        super().__init__(parent)
        self.available_fields = available_fields
        self.selected_vocab_field = None
        self.selected_definition_field = None
        self.selected_image_field = None
        
        self.init_ui(model_name)
    
    def init_ui(self, model_name: str):
        """Tạo giao diện dialog"""
        self.setWindowTitle(f"Chọn fields - {model_name}")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Chọn field từ vựng
        layout.addWidget(QLabel("Chọn field Từ vựng:"))
        vocab_combo = QComboBox()
        vocab_combo.addItems(self.available_fields)
        # Thử tìm field mặc định
        if "Mặt trước" in self.available_fields:
            vocab_combo.setCurrentText("Mặt trước")
        layout.addWidget(vocab_combo)
        
        # Chọn field định nghĩa
        layout.addWidget(QLabel("Chọn field Định nghĩa:"))
        definition_combo = QComboBox()
        definition_combo.addItems(self.available_fields)
        if "Định nghĩa" in self.available_fields:
            definition_combo.setCurrentText("Định nghĩa")
        layout.addWidget(definition_combo)
        
        # Chọn field ảnh
        layout.addWidget(QLabel("Chọn field Ảnh:"))
        image_combo = QComboBox()
        image_combo.addItems(self.available_fields)
        if "Ảnh" in self.available_fields:
            image_combo.setCurrentText("Ảnh")
        layout.addWidget(image_combo)
        
        # Nút OK/Cancel
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Hủy")
        
        ok_button.clicked.connect(lambda: self.accept_with_values(
            vocab_combo.currentText(),
            definition_combo.currentText(),
            image_combo.currentText()
        ))
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def accept_with_values(self, vocab_field: str, definition_field: str, image_field: str):
        """Lưu lựa chọn và đóng dialog"""
        self.selected_vocab_field = vocab_field
        self.selected_definition_field = definition_field
        self.selected_image_field = image_field
        self.accept()


class ConfigDialog(QDialog):
    """Dialog cài đặt API keys"""
    
    def __init__(self, parent=None, existing_config=None):
        """Khởi tạo ConfigDialog"""
        super().__init__(parent)
        self.config_values = {}
        self.existing_config = existing_config or {}
        self.init_ui()
        self.load_existing_config()
    
    def init_ui(self):
        """Tạo giao diện config"""
        from aqt.qt import QLineEdit, QCheckBox
        
        self.setWindowTitle("AnkiAI v3.0 - Cài đặt (Gemini + Groq + Ollama)")
        self.setMinimumWidth(550)
        
        layout = QVBoxLayout()
        
        # AI Providers (v3.0)
        layout.addWidget(QLabel("🤖 AI Providers (cấu hình ít nhất một):"))
        
        # Groq API Key
        layout.addWidget(QLabel("Groq API Key (⭐ Nên dùng - siêu nhanh, miễn phí):"))
        self.groq_input = QLineEdit()
        self.groq_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.groq_input.setPlaceholderText("Get from: console.groq.com/keys")
        layout.addWidget(self.groq_input)
        
        # Gemini API Keys (v4.0 - 3 keys for multi-Gemini architecture)
        layout.addWidget(QLabel("\n🔑 Gemini API Keys (Multi-key Architecture):"))
        
        layout.addWidget(QLabel("Gemini API Key #1 (⭐ Keyword Generator - cấp priority cao):"))
        self.gemini_input = QLineEdit()
        self.gemini_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.gemini_input.setPlaceholderText("Get from: makersuite.google.com/app/apikey (Key #1 - keyword generation)")
        layout.addWidget(self.gemini_input)
        
        layout.addWidget(QLabel("Gemini API Key #2 (tuỳ chọn - Image Evaluator):"))
        self.gemini_eval_input = QLineEdit()
        self.gemini_eval_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.gemini_eval_input.setPlaceholderText("Get from: makersuite.google.com/app/apikey (Key #2 - image evaluation)")
        layout.addWidget(self.gemini_eval_input)
        
        layout.addWidget(QLabel("Gemini API Key #3 (tuỳ chọn - Backup):"))
        self.gemini_backup_input = QLineEdit()
        self.gemini_backup_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.gemini_backup_input.setPlaceholderText("Get from: makersuite.google.com/app/apikey (Key #3 - backup)")
        layout.addWidget(self.gemini_backup_input)
        
        # Ollama Checkbox
        layout.addWidget(QLabel("Ollama (Local backup - hoàn toàn miễn phí):"))
        self.ollama_checkbox = QCheckBox("Sử dụng Ollama local")
        self.ollama_checkbox.setToolTip("Chạy trên máy của bạn, không cần internet. Yêu cầu: ollama pull mistral")
        layout.addWidget(self.ollama_checkbox)
        
        self.ollama_url_input = QLineEdit()
        self.ollama_url_input.setText("http://localhost:11434")
        self.ollama_url_input.setPlaceholderText("URL của Ollama server")
        layout.addWidget(self.ollama_url_input)
        
        # Image Search Providers (v4.0)
        layout.addWidget(QLabel("\n📷 Image Search Providers (cấu hình ít nhất một):"))
        
        layout.addWidget(QLabel("Pexels API Key (⭐ Nên cấu hình - nhanh, chất lượng cao):"))
        self.pexels_input = QLineEdit()
        self.pexels_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pexels_input.setPlaceholderText("Get from: pexels.com/api")
        layout.addWidget(self.pexels_input)
        
        layout.addWidget(QLabel("Unsplash API Key (tuỳ chọn):"))
        self.unsplash_input = QLineEdit()
        self.unsplash_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.unsplash_input.setPlaceholderText("Get from: unsplash.com/developers")
        layout.addWidget(self.unsplash_input)
        
        layout.addWidget(QLabel("Pixabay API Key (tuỳ chọn):"))
        self.pixabay_input = QLineEdit()
        self.pixabay_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pixabay_input.setPlaceholderText("Get from: pixabay.com/api/")
        layout.addWidget(self.pixabay_input)
        
        # Google Custom Search (v4.0)
        layout.addWidget(QLabel("\n🔍 Google Custom Search (tuỳ chọn):"))
        layout.addWidget(QLabel("Google API Key (for Custom Search):"))
        self.google_api_input = QLineEdit()
        self.google_api_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.google_api_input.setPlaceholderText("Get from: console.cloud.google.com (Custom Search API)")
        layout.addWidget(self.google_api_input)
        
        layout.addWidget(QLabel("Google Custom Search Engine ID (CX):"))
        self.google_cx_input = QLineEdit()
        self.google_cx_input.setEchoMode(QLineEdit.EchoMode.Normal)
        self.google_cx_input.setPlaceholderText("Get from: cse.google.com (Custom Search Engine setup)")
        layout.addWidget(self.google_cx_input)
        
        # AI Image Evaluation Settings (v4.0)
        layout.addWidget(QLabel("\n🎯 Image Evaluation Settings:"))
        self.enable_ai_eval_checkbox = QCheckBox("Sử dụng AI (Gemini Vision) để chọn ảnh tốt nhất")
        self.enable_ai_eval_checkbox.setToolTip("Gemini sẽ đánh giá tất cả ảnh candidate và chọn ảnh tốt nhất")
        self.enable_ai_eval_checkbox.setChecked(True)
        layout.addWidget(self.enable_ai_eval_checkbox)
        
        # Nút Test Connection
        test_ai_button = QPushButton("🔌 Test AI Connections")
        test_ai_button.clicked.connect(self.test_connection)
        layout.addWidget(test_ai_button)
        
        test_image_button = QPushButton("🖼️ Test Image Providers")
        test_image_button.clicked.connect(self.test_image_providers)
        layout.addWidget(test_image_button)
        
        # OK/Cancel
        button_layout = QHBoxLayout()
        ok_button = QPushButton("💾 Lưu")
        cancel_button = QPushButton("❌ Hủy")
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_existing_config(self):
        """Load existing config values into input fields"""
        try:
            if self.existing_config:
                # Load AI Provider Keys
                groq_key = self.existing_config.get("groq_api_key", "")
                if groq_key:
                    self.groq_input.setText(groq_key)
                
                gemini_key = self.existing_config.get("gemini_api_key", "")
                if gemini_key:
                    self.gemini_input.setText(gemini_key)
                
                # Load new Gemini keys (v4.0)
                gemini_eval_key = self.existing_config.get("gemini_eval_api_key", "")
                if gemini_eval_key:
                    self.gemini_eval_input.setText(gemini_eval_key)
                
                gemini_backup_key = self.existing_config.get("gemini_backup_api_key", "")
                if gemini_backup_key:
                    self.gemini_backup_input.setText(gemini_backup_key)
                
                use_ollama = self.existing_config.get("use_ollama", False)
                self.ollama_checkbox.setChecked(use_ollama)
                
                ollama_url = self.existing_config.get("ollama_url", "http://localhost:11434")
                self.ollama_url_input.setText(ollama_url)
                
                # Load Image Search Provider Keys
                unsplash_key = self.existing_config.get("unsplash_api_key", "")
                if unsplash_key:
                    self.unsplash_input.setText(unsplash_key)
                
                pixabay_key = self.existing_config.get("pixabay_api_key", "")
                if pixabay_key:
                    self.pixabay_input.setText(pixabay_key)
                
                pexels_key = self.existing_config.get("pexels_api_key", "")
                if pexels_key:
                    self.pexels_input.setText(pexels_key)
                
                # Load Google Custom Search keys (v4.0)
                google_api_key = self.existing_config.get("google_api_key", "")
                if google_api_key:
                    self.google_api_input.setText(google_api_key)
                
                google_cx = self.existing_config.get("google_cx", "")
                if google_cx:
                    self.google_cx_input.setText(google_cx)
                
                # Load AI evaluation setting (v4.0)
                enable_ai_eval = self.existing_config.get("enable_ai_evaluation", True)
                self.enable_ai_eval_checkbox.setChecked(enable_ai_eval)
        except Exception as e:
            print(f"[UI] Error loading config: {e}")
    
    def get_config(self) -> dict:
        """Lấy cấu hình từ dialog"""
        groq_key = self.groq_input.text().strip()
        gemini_key = self.gemini_input.text().strip()
        gemini_eval_key = self.gemini_eval_input.text().strip()
        gemini_backup_key = self.gemini_backup_input.text().strip()
        use_ollama = self.ollama_checkbox.isChecked()
        
        # Validate: at least one AI provider is configured
        if not groq_key and not gemini_key and not use_ollama:
            raise ValueError("Vui lòng cấu hình ít nhất một AI provider (Groq, Gemini, hoặc Ollama)")
        
        # Image providers
        pexels_key = self.pexels_input.text().strip()
        unsplash_key = self.unsplash_input.text().strip()
        pixabay_key = self.pixabay_input.text().strip()
        google_api_key = self.google_api_input.text().strip()
        google_cx = self.google_cx_input.text().strip()
        
        if not (pexels_key or unsplash_key or pixabay_key or (google_api_key and google_cx)):
            raise ValueError("Vui lòng cấu hình ít nhất một Image Provider (Pexels, Unsplash, Pixabay, hoặc Google Custom Search)")
        
        # AI evaluation setting
        enable_ai_eval = self.enable_ai_eval_checkbox.isChecked()
        
        return {
            "groq_api_key": groq_key,
            "gemini_api_key": gemini_key,
            "gemini_eval_api_key": gemini_eval_key,
            "gemini_backup_api_key": gemini_backup_key,
            "use_ollama": use_ollama,
            "ollama_url": self.ollama_url_input.text().strip(),
            "unsplash_api_key": unsplash_key,
            "pixabay_api_key": pixabay_key,
            "pexels_api_key": pexels_key,
            "google_api_key": google_api_key,
            "google_cx": google_cx,
            "enable_ai_evaluation": enable_ai_eval,
            "image_generation_mode": "search"
        }
    
    def test_connection(self):
        """Test kết nối AI providers"""
        groq_key = self.groq_input.text().strip()
        gemini_key = self.gemini_input.text().strip()
        use_ollama = self.ollama_checkbox.isChecked()
        ollama_url = self.ollama_url_input.text().strip()
        
        if not (groq_key or gemini_key or use_ollama):
            QMessageBox.warning(self, "Lỗi", "Vui lòng cấu hình ít nhất một AI provider")
            return
        
        results = []
        
        # Test Groq
        if groq_key:
            try:
                import requests
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {groq_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.1-8b-instant",
                        "messages": [{"role": "user", "content": "test"}],
                        "max_tokens": 5
                    },
                    timeout=5
                )
                
                if response.status_code == 200:
                    results.append("✓ Groq API: OK")
                else:
                    results.append(f"✗ Groq API: Error {response.status_code}")
            except Exception as e:
                results.append(f"✗ Groq API: {str(e)}")
        
        # Test Gemini
        if gemini_key:
            try:
                import requests
                response = requests.post(
                    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
                    params={"key": gemini_key},
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{"parts": [{"text": "test"}]}],
                        "generationConfig": {"maxOutputTokens": 5}
                    },
                    timeout=5
                )
                
                if response.status_code == 200:
                    results.append("✓ Gemini API: OK")
                else:
                    results.append(f"✗ Gemini API: Error {response.status_code}")
            except Exception as e:
                results.append(f"✗ Gemini API: {str(e)}")
        
        # Test Ollama
        if use_ollama:
            try:
                import requests
                response = requests.get(f"{ollama_url}/api/tags", timeout=3)
                
                if response.status_code == 200:
                    results.append("✓ Ollama: OK")
                else:
                    results.append(f"✗ Ollama: Error {response.status_code}")
            except Exception as e:
                results.append(f"✗ Ollama: Not running or unreachable")
        
        message = "\n".join(results)
        QMessageBox.information(self, "Test Results", message)
    
    def test_image_providers(self):
        """Test kết nối Image Providers"""
        pexels_key = self.pexels_input.text().strip()
        unsplash_key = self.unsplash_input.text().strip()
        pixabay_key = self.pixabay_input.text().strip()
        
        results = []
        
        # Test Pexels
        if pexels_key:
            try:
                import requests
                response = requests.get(
                    "https://api.pexels.com/v1/search",
                    headers={"Authorization": pexels_key},
                    params={"query": "test", "per_page": 1},
                    timeout=5
                )
                if response.status_code == 200:
                    results.append("✓ Pexels: OK")
                else:
                    results.append(f"✗ Pexels: Error {response.status_code}")
            except Exception as e:
                results.append(f"✗ Pexels: {str(e)}")
        else:
            results.append("○ Pexels: No API key (optional)")
        
        # Test Unsplash
        if unsplash_key:
            try:
                import requests
                response = requests.get(
                    "https://api.unsplash.com/search/photos",
                    headers={"Authorization": f"Client-ID {unsplash_key}"},
                    params={"query": "test", "per_page": 1},
                    timeout=5
                )
                if response.status_code == 200:
                    results.append("✓ Unsplash: OK")
                else:
                    results.append(f"✗ Unsplash: Error {response.status_code}")
            except Exception as e:
                results.append(f"✗ Unsplash: {str(e)}")
        else:
            results.append("○ Unsplash: No API key (optional)")
        
        # Test Pixabay
        if pixabay_key:
            try:
                import requests
                response = requests.get(
                    "https://pixabay.com/api",
                    params={"key": pixabay_key, "q": "test", "per_page": 1},
                    timeout=5
                )
                if response.status_code == 200:
                    results.append("✓ Pixabay: OK")
                else:
                    results.append(f"✗ Pixabay: Error {response.status_code}")
            except Exception as e:
                results.append(f"✗ Pixabay: {str(e)}")
        else:
            results.append("○ Pixabay: No API key (optional)")
        
        # Test Openverse (no API key needed)
        try:
            import requests
            response = requests.get(
                "https://api.openverse.engineering/v1/images",
                params={"q": "test", "page_size": 1},
                timeout=5,
                headers={"User-Agent": "AnkiAI/4.0"}
            )
            if response.status_code == 200:
                results.append("✓ Openverse: OK (no API key needed)")
            else:
                results.append(f"✗ Openverse: Error {response.status_code}")
        except Exception as e:
            results.append(f"✗ Openverse: {str(e)}")
        
        # Test Lorem Picsum (no API key needed)
        try:
            import requests
            # Use GET with allow_redirects=False to avoid downloading image
            response = requests.get("https://picsum.photos/200/300", timeout=3, allow_redirects=False)
            if response.status_code in [200, 301, 302]:
                results.append("✓ Lorem Picsum: OK (no API key needed)")
            else:
                results.append(f"✗ Lorem Picsum: Error {response.status_code}")
        except Exception as e:
            results.append(f"✗ Lorem Picsum: {str(e)}")
        
        message = "\n".join(results)
        QMessageBox.information(self, "Image Provider Test Results", message)
    

def get_note_data(note) -> tuple:
    """
    Trích xuất dữ liệu từ note
    
    Args:
        note: Anki Note object
    
    Returns:
        Tuple (vocabulary, definition)
    """
    try:
        # Thử lấy field phổ biến
        fields = {name: note[name] for name in note.keys()}
        
        # Ưu tiên các tên field tiếng Anh
        vocabulary = (
            fields.get("Front") or
            fields.get("Mặt trước") or
            fields.get("Word") or
            fields.get("Question") or
            list(fields.values())[0] if fields else ""
        )
        
        definition = (
            fields.get("Back") or
            fields.get("Mặt sau") or
            fields.get("Definition") or
            fields.get("Định nghĩa") or
            fields.get("Answer") or
            list(fields.values())[1] if len(fields) > 1 else ""
        )
        
        # Loại bỏ HTML tags
        import re
        vocabulary = re.sub(r"<[^>]+>", "", vocabulary).strip()
        definition = re.sub(r"<[^>]+>", "", definition).strip()
        
        return vocabulary, definition
    
    except Exception as e:
        print(f"Error getting note data: {e}")
        return "", ""
