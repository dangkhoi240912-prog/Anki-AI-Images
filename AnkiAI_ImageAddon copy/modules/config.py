"""
Config Module - Quản lý cài đặt của add-on
Cho phép người dùng nhập API key, chọn field names, chọn mode (AI search vs AI generate)

v2.0 Improvements:
- Added Pexels API support
- Keyword cache enabled by default
- Image optimization settings
- Performance tuning defaults
"""

from aqt import mw
import json
import os
from typing import Dict, Any


class ConfigManager:
    """Quản lý cấu hình của add-on - v4.0"""
    
    DEFAULT_CONFIG = {
        # AI Providers (v4.0)
        "gemini_api_key": "",
        "gemini_eval_api_key": "",  # ✨ NEW: Key #2 for image evaluation
        "gemini_backup_api_key": "",  # ✨ NEW: Key #3 for backup
        "groq_api_key": "",
        "use_ollama": False,
        "ollama_url": "http://localhost:11434",
        
        # Image Search Providers (v4.0 - 7 providers!)
        "pexels_api_key": "",
        "unsplash_api_key": "",
        "pixabay_api_key": "",
        "wallhaven_api_key": "",
        "google_api_key": "",  # ✨ NEW: Google Custom Search API
        "google_cx": "",  # ✨ NEW: Google Custom Search Engine ID
        # No API keys needed for: Openverse, Lorem Picsum
        
        # AI Image Evaluation (v4.0)
        "enable_ai_evaluation": True,  # ✨ NEW: Use Gemini to pick best image
        
        # Smart Selection Settings
        "enable_smart_selection": True,  # ✨ Use smart ranking
        "max_concurrent_providers": 6,   # ✨ Concurrent requests
        "smart_cache_ttl_minutes": 120,  # ✨ Cache TTL
        
        # Image Download Settings (v4.0 - optimized)
        "image_download_timeout": 15,    # Reduced from 20 (more aggressive)
        "image_download_retries": 2,     # Reduced from 3 (faster)
        "enable_image_optimization": True,
        "image_max_width": 800,
        "image_quality": 80,             # Reduced from 85 (slightly smaller file)
        
        # Keyword Caching (v4.0)
        "enable_keyword_cache": True,
        "keyword_cache_size": 1000,      # Increased from 500
        
        # UI Settings
        "vocabulary_field": "Mặt trước",
        "definition_field": "Định nghĩa",
        "image_field": "Ảnh",
        "image_generation_mode": "search",
        
        # Concurrency Settings (v4.0)
        "max_concurrent_requests": 5,
        "enable_concurrent_downloads": True,
        
        # Other
        "auto_add_on_sync": False,
    }
    
    # Tên thư mục addon (dùng để Anki đọc/ghi config đúng)
    ADDON_MODULE = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    @property
    def addon_module(self):
        """Lấy tên addon module từ Anki"""
        # Thử lấy từ __name__ nếu có
        try:
            import __main__
            if hasattr(__main__, 'addonManager'):
                # Đang chạy trong Anki
                pass
        except:
            pass
        return self.ADDON_MODULE
    
    def __init__(self):
        """Khởi tạo config manager"""
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load config: merge defaults + meta.json user overrides"""
        config = self.DEFAULT_CONFIG.copy()
        
        # PRIMARY: read meta.json directly (most reliable)
        try:
            addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            meta_path = os.path.join(addon_dir, "meta.json")
            if os.path.exists(meta_path):
                with open(meta_path, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                user_config = meta.get("config", {})
                if user_config:
                    config.update(user_config)
                    return config
        except Exception:
            pass
        
        # FALLBACK: Anki's getConfig API
        try:
            anki_config = mw.addonManager.getConfig(self.ADDON_MODULE)
            if anki_config:
                config.update(anki_config)
                return config
        except Exception:
            pass
        
        return config
    
    def reload(self):
        """Force reload config from disk"""
        self.config = self._load_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Lấy giá trị config"""
        val = self.config.get(key, default if default is not None else self.DEFAULT_CONFIG.get(key))
        return val
    
    def set(self, key: str, value: Any) -> None:
        """Cập nhật giá trị config"""
        self.config[key] = value
        self.save_config()
    
    def save_config(self) -> None:
        """Lưu config vào Anki"""
        try:
            print(f"[ConfigManager] Saving config for module: {self.ADDON_MODULE}")
            mw.addonManager.writeConfig(self.ADDON_MODULE, self.config)
            print(f"[ConfigManager] Config saved via addonManager")
        except Exception as e:
            print(f"[ConfigManager] addonManager failed: {e}, trying direct file save...")
            # Fallback: Lưu trực tiếp vào file
            try:
                import json
                config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=4, ensure_ascii=False)
                print(f"[ConfigManager] Config saved directly to: {config_path}")
            except Exception as e2:
                print(f"[ConfigManager] Direct save also failed: {e2}")
                import traceback
                traceback.print_exc()
    
    def get_all(self) -> Dict[str, Any]:
        """Lấy toàn bộ config"""
        return self.config.copy()
    
    def reset_to_default(self) -> None:
        """Reset về cấu hình mặc định"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save_config()
    
    def validate_api_keys(self) -> Dict[str, bool]:
        """Kiểm tra xem API keys đã được cài đặt chưa"""
        # Check if at least one AI provider is configured
        has_AI_provider = (
            bool(self.get("gemini_api_key")) or
            bool(self.get("groq_api_key")) or
            self.get("use_ollama")
        )
        
        # Image search providers
        has_image_provider = (
            bool(self.get("pexels_api_key")) or
            bool(self.get("unsplash_api_key")) or
            bool(self.get("pixabay_api_key"))
        )
        
        return {
            "ai_provider": has_AI_provider,
            "image_provider": has_image_provider if self.get("image_generation_mode") == "search" else True,
        }


# Singleton instance
config_manager = None


def get_config_manager() -> ConfigManager:
    """Lấy singleton ConfigManager"""
    global config_manager
    if config_manager is None:
        config_manager = ConfigManager()
    return config_manager
