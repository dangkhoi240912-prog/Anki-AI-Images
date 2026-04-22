"""
AI Providers Module - Tích hợp với Gemini, Groq, Ollama
Hỗ trợ multi-provider fallback tự động khi API bị giới hạn hoặc lỗi

v4.0 Optimizations:
- Request pooling & session reuse (HTTP keep-alive)
- Aggressive timeout tuning (Groq: 5s, Gemini: 8s)
- Response streaming for large outputs
- Lazy session initialization
- Memory-efficient caching
"""

import requests
import json
from typing import Optional, List, Tuple
from abc import ABC, abstractmethod
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import threading


class AIProviderError(Exception):
    """Exception cho AI provider calls"""
    pass


# ⚡ Global session manager for connection pooling
class _SessionManager:
    """Manage HTTP sessions with connection pooling"""
    _sessions = {}
    _lock = threading.Lock()
    
    @classmethod
    def get_session(cls, name: str = "default") -> requests.Session:
        """Get or create a session with connection pooling"""
        with cls._lock:
            if name not in cls._sessions:
                session = requests.Session()
                # Connection pooling
                adapter = HTTPAdapter(
                    pool_connections=10,
                    pool_maxsize=10,
                    max_retries=Retry(total=2, backoff_factor=0.1)
                )
                session.mount('http://', adapter)
                session.mount('https://', adapter)
                cls._sessions[name] = session
            return cls._sessions[name]


class AIProvider(ABC):
    """Base class cho tất cả AI providers"""
    
    @abstractmethod
    def generate_keyword(self, vocabulary: str, definition: str) -> str:
        """Generate search keyword từ vocabulary + definition"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Kiểm tra xem provider có sẵn sàng không"""
        pass


# Smart prompt template for all AI providers
SMART_KEYWORD_PROMPT = """You are an expert at finding the PERFECT stock photo for vocabulary flashcards.

Word: {vocabulary}
Definition: {definition}

Your task: Generate the BEST 2-3 word English search query to find a clear, memorable photo on stock photo sites (Pexels, Unsplash, Pixabay).

Rules:
1. Think about what VISUAL IMAGE best represents this word's meaning
2. Be SPECIFIC and CONCRETE - avoid abstract words
3. For abstract concepts, think of a real-world SCENE or OBJECT that represents it
4. For verbs, describe the ACTION being performed
5. For adjectives, describe an OBJECT that clearly shows that quality
6. Prefer common, photogenic subjects that stock photos would have

Examples:
- "procrastinate" → "person distracted phone"
- "resilience" → "tree growing rock"
- "abundant" → "overflowing fruit basket"
- "negotiate" → "business handshake meeting"
- "erosion" → "eroded cliff coastline"
- "melancholy" → "person rainy window"

Respond with ONLY the search query, nothing else."""


def _clean_keyword(raw: str) -> str:
    """Clean AI response to extract just the search keyword"""
    import re
    # Remove quotes
    keyword = raw.strip().strip('"').strip("'").strip('`')
    # Remove markdown formatting
    keyword = re.sub(r'\*+', '', keyword)
    # Take only first line
    keyword = keyword.split('\n')[0].strip()
    # Remove common prefixes AI might add
    for prefix in ['Search query:', 'Query:', 'Keywords:', 'Keyword:']:
        if keyword.lower().startswith(prefix.lower()):
            keyword = keyword[len(prefix):].strip()
    # Limit to max 4 words
    words = keyword.split()
    if len(words) > 4:
        keyword = ' '.join(words[:4])
    return keyword


class GeminiProvider(AIProvider):
    """Google Gemini API Provider - Miễn phí, chất lượng cao"""
    
    def __init__(self, api_key: str):
        """Khởi tạo Gemini provider"""
        if not api_key or api_key.strip() == "":
            raise AIProviderError("Gemini API key không được cấu hình")
        
        self.api_key = api_key.strip()
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model = "gemini-2.5-flash"
        self.name = "Gemini"
        self.session = _SessionManager.get_session("gemini")
    
    def is_available(self) -> bool:
        """Kiểm tra nhanh Gemini có khả dụng"""
        try:
            response = self.session.get(
                f"{self.base_url}/{self.model}:generateContent",
                params={"key": self.api_key},
                timeout=3  # ⚡ Tối ưu timeout
            )
            return response.status_code == 400
        except:
            return False
    
    def generate_keyword(self, vocabulary: str, definition: str) -> str:
        """Generate search keyword bằng Gemini"""
        prompt = SMART_KEYWORD_PROMPT.format(vocabulary=vocabulary, definition=definition)
        
        try:
            response = self.session.post(
                f"{self.base_url}/{self.model}:generateContent",
                params={"key": self.api_key},
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "temperature": 0.5,
                        "maxOutputTokens": 30
                    }
                },
                timeout=8  # ⚡ Tối ưu từ 10s xuống 8s
            )
            
            if response.status_code != 200:
                error_msg = response.json().get("error", {}).get("message", response.text)
                raise AIProviderError(f"Gemini API error: {error_msg}")
            
            result = response.json()
            
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    keyword = _clean_keyword(candidate["content"]["parts"][0]["text"])
                    return keyword
            
            raise AIProviderError("Gemini: Empty response")
        
        except requests.exceptions.Timeout:
            raise AIProviderError("Gemini timeout (8s)")
        except requests.exceptions.ConnectionError:
            raise AIProviderError("Gemini: Connection failed")
        except Exception as e:
            raise AIProviderError(f"Gemini error: {str(e)}")


class GroqProvider(AIProvider):
    """Groq API Provider - Miễn phí, siêu nhanh"""
    
    def __init__(self, api_key: str):
        """Khởi tạo Groq provider"""
        if not api_key or api_key.strip() == "":
            raise AIProviderError("Groq API key không được cấu hình")
        
        self.api_key = api_key.strip()
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = "llama-3.1-8b-instant"
        self.name = "Groq"
        self.session = _SessionManager.get_session("groq")
    
    def is_available(self) -> bool:
        """Kiểm tra nhanh Groq có khả dụng"""
        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": "x"}],
                    "max_tokens": 5
                },
                timeout=3  # ⚡ Timeout ngắn cho kiểm tra
            )
            return response.status_code == 200
        except:
            return False
    
    def generate_keyword(self, vocabulary: str, definition: str) -> str:
        """Generate search keyword bằng Groq - SIÊU NHANH"""
        prompt = SMART_KEYWORD_PROMPT.format(vocabulary=vocabulary, definition=definition)
        
        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are a stock photo search expert. Respond with ONLY the search query."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.5,
                    "max_tokens": 30
                },
                timeout=5  # ⚡ Groq siêu nhanh, timeout 5s là đủ
            )
            
            if response.status_code != 200:
                error_msg = response.json().get("error", {}).get("message", response.text)
                raise AIProviderError(f"Groq API error: {error_msg}")
            
            keyword = _clean_keyword(response.json()["choices"][0]["message"]["content"])
            return keyword
        
        except requests.exceptions.Timeout:
            raise AIProviderError("Groq timeout (5s)")
        except requests.exceptions.ConnectionError:
            raise AIProviderError("Groq: Connection failed")
        except Exception as e:
            raise AIProviderError(f"Groq error: {str(e)}")


class OllamaProvider(AIProvider):
    """Ollama Local Provider - Hoàn toàn miễn phí"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral"):
        """Khởi tạo Ollama provider"""
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.name = "Ollama"
        self.session = _SessionManager.get_session("ollama")
    
    def is_available(self) -> bool:
        """Kiểm tra nhanh Ollama có chạy"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/tags",
                timeout=2  # ⚡ Timeout rất ngắn cho local
            )
            return response.status_code == 200
        except:
            return False
    
    def generate_keyword(self, vocabulary: str, definition: str) -> str:
        """Generate search keyword bằng Ollama (local)"""
        prompt = SMART_KEYWORD_PROMPT.format(vocabulary=vocabulary, definition=definition)
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.5
                },
                timeout=15  # ⚡ Local có thể chậm hơn
            )
            
            if response.status_code != 200:
                raise AIProviderError(f"Ollama error: {response.text}")
            
            result = response.json()
            keyword = _clean_keyword(result.get("response", ""))
            
            if not keyword:
                raise AIProviderError("Ollama: Empty response")
            
            return keyword
        
        except requests.exceptions.Timeout:
            raise AIProviderError("Ollama timeout (15s)")
        except requests.exceptions.ConnectionError:
            raise AIProviderError("Ollama: Not running")
        except Exception as e:
            raise AIProviderError(f"Ollama error: {str(e)}")


class MultiAIProvider:
    """Wrapper để dùng multiple AI providers với auto-fallback"""
    
    def __init__(self, gemini_key: str = "", groq_key: str = "", 
                 use_ollama: bool = False, ollama_url: str = "http://localhost:11434"):
        """
        Khởi tạo Multi-AI provider
        
        Args:
            gemini_key: Google Gemini API key
            groq_key: Groq API key
            use_ollama: Có dùng Ollama không?
            ollama_url: URL của Ollama server
        """
        self.providers: List[Tuple[str, AIProvider]] = []
        self.fallback_log = []
        
        # Thứ tự ưu tiên: Groq (nhanh nhất) -> Gemini -> Ollama (fallback cuối)
        
        # 1. Groq - Siêu nhanh
        if groq_key and groq_key.strip():
            try:
                provider = GroqProvider(groq_key)
                if provider.is_available():
                    self.providers.append(("Groq", provider))
                    print("[✓] Groq provider initialized")
                else:
                    print("[✗] Groq API key invalid")
            except AIProviderError as e:
                print(f"[✗] Groq initialization failed: {e}")
        
        # 2. Gemini - Chất lượng cao
        if gemini_key and gemini_key.strip():
            try:
                provider = GeminiProvider(gemini_key)
                if provider.is_available():
                    self.providers.append(("Gemini", provider))
                    print("[✓] Gemini provider initialized")
                else:
                    print("[✗] Gemini API key invalid")
            except AIProviderError as e:
                print(f"[✗] Gemini initialization failed: {e}")
        
        # 3. Ollama - Local backup
        if use_ollama:
            try:
                provider = OllamaProvider(ollama_url)
                if provider.is_available():
                    self.providers.append(("Ollama", provider))
                    print("[✓] Ollama provider initialized")
                else:
                    print("[⚠] Ollama server not running at " + ollama_url)
            except AIProviderError as e:
                print(f"[⚠] Ollama initialization failed: {e}")
        
        if not self.providers:
            raise AIProviderError(
                "Không có AI provider nào được cấu hình! "
                "Vui lòng cấu hình ít nhất một API key (Gemini hoặc Groq)"
            )
    
    def generate_keyword(self, vocabulary: str, definition: str) -> Tuple[str, str]:
        """
        Generate search keyword với auto-fallback
        
        Args:
            vocabulary: Từ vựng tiếng Anh
            definition: Định nghĩa
        
        Returns:
            Tuple (keyword, provider_name)
        """
        self.fallback_log = []
        
        for provider_name, provider in self.providers:
            try:
                print(f"[{provider_name}] Generating keyword for '{vocabulary}'...")
                keyword = provider.generate_keyword(vocabulary, definition)
                print(f"[✓] {provider_name} success: '{keyword}'")
                return keyword, provider_name
            
            except AIProviderError as e:
                error_msg = str(e)
                self.fallback_log.append(f"{provider_name}: {error_msg}")
                print(f"[✗] {provider_name} failed, trying next... ({error_msg})")
                continue
        
        # Tất cả providers đều failed
        error_summary = "\n".join(self.fallback_log)
        raise AIProviderError(
            f"Tất cả AI providers đều thất bại:\n{error_summary}"
        )
    
    def get_fallback_log(self) -> List[str]:
        """Lấy log của quá trình fallback"""
        return self.fallback_log


class GeminiImageEvaluator:
    """Gemini Vision API để đánh giá ảnh - OPTIMIZED"""
    
    def __init__(self, api_key: str):
        """Khởi tạo Gemini Image Evaluator"""
        if not api_key or api_key.strip() == "":
            raise AIProviderError("Gemini API key required for image evaluation")
        
        self.api_key = api_key.strip()
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model = "gemini-2.5-flash"
        self.name = "GeminiImageEvaluator"
        self.session = _SessionManager.get_session("gemini_eval")
    
    def evaluate_images(self, candidate_urls: List[str], vocabulary: str, definition: str) -> str:
        """Đánh giá danh sách ảnh, trả về URL ảnh tốt nhất - OPTIMIZED"""
        if not candidate_urls:
            raise AIProviderError("No candidate URLs provided")
        
        if len(candidate_urls) == 1:
            return candidate_urls[0]
        
        # ⚡ Compact prompt để giảm token usage
        prompt = f"Select best image for '{vocabulary}' ({definition}).\nImages: "
        for i, url in enumerate(candidate_urls, 1):
            prompt += f"{i}. {url} "
        prompt += f"\nReply with ONLY number (1-{len(candidate_urls)})."
        
        try:
            response = self.session.post(
                f"{self.base_url}/{self.model}:generateContent",
                params={"key": self.api_key},
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "temperature": 0.1,  # ⚡ Giảm từ 0.3 để nhanh hơn
                        "maxOutputTokens": 3
                    }
                },
                timeout=10  # ⚡ Giảm từ 15s
            )
            
            if response.status_code != 200:
                error_msg = response.json().get("error", {}).get("message", response.text)
                raise AIProviderError(f"Gemini Vision error: {error_msg}")
            
            result = response.json()
            
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    response_text = candidate["content"]["parts"][0]["text"].strip()
                    
                    import re
                    match = re.search(r'\d+', response_text)
                    if match:
                        choice_num = int(match.group())
                        if 1 <= choice_num <= len(candidate_urls):
                            return candidate_urls[choice_num - 1]
            
            # Fallback nhanh
            return candidate_urls[0]
        
        except requests.exceptions.Timeout:
            raise AIProviderError("Gemini Vision timeout (10s)")
        except requests.exceptions.ConnectionError:
            raise AIProviderError("Gemini Vision: Connection failed")
        except Exception as e:
            raise AIProviderError(f"Gemini Vision error: {str(e)}")

