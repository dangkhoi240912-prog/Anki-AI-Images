"""
API Handler Module v4.1 - OPTIMIZED Multi-AI + Smart Image Selection
Optimizations:
- Reduced redundant API calls
- Aggressive timeouts (Groq: 5s, Gemini: 8s, Images: 4-5s)
- Early cache hits skip all processing
- Fallback chain with minimal overhead
- Memory-efficient result handling
"""

import requests
import json
from typing import Optional, Dict, List, Tuple
import time
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FuturesTimeoutError
from .ai_providers import MultiAIProvider, AIProviderError, GeminiImageEvaluator
from .image_providers import (
    SmartImageSelector, 
    PexelsProvider, 
    UnsplashProvider, 
    PixabayProvider,
    GoogleImageProvider,
    OpenverseProvider,
    WallhavenProvider,
    LoremPicsumProvider,
    ImageProviderError
)


class APIError(Exception):
    """Exception cho API calls"""
    pass


class KeywordCache:
    """Cache cho keywords để tránh re-call AI (thread-safe)"""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, str] = {}
        self.max_size = max_size
        self.lock = __import__('threading').Lock()
    
    def get(self, key: str) -> Optional[str]:
        """Lấy keyword từ cache"""
        with self.lock:
            return self.cache.get(key)
    
    def set(self, key: str, value: str):
        """Lưu keyword vào cache"""
        with self.lock:
            if len(self.cache) >= self.max_size:
                # Remove oldest entry
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            self.cache[key] = value
    
    def clear(self):
        """Xóa toàn bộ cache"""
        with self.lock:
            self.cache.clear()
    
    def make_key(self, vocabulary: str, definition: str) -> str:
        """Tạo key từ vocabulary + definition"""
        return f"{vocabulary}_{definition}".lower().strip()


class AIImageProvider:
    """
    Wrapper cho Multi-AI + Smart Image Selection - v4.0
    Optimized for performance, quality, and reliability
    """
    
    def __init__(self, 
                 # AI Providers
                 gemini_key: str = "", 
                 gemini_eval_key: str = "",
                 gemini_backup_key: str = "",
                 groq_key: str = "", 
                 use_ollama: bool = False, 
                 ollama_url: str = "http://localhost:11434",
                 # Image Search Providers
                 unsplash_key: str = None, 
                 pixabay_key: str = None,
                 pexels_key: str = None,
                 wallhaven_key: str = None,
                 google_api_key: str = None,
                 google_cx: str = None,
                 # Settings
                 enable_smart_selection: bool = True,
                 enable_ai_evaluation: bool = True,
                 max_concurrent_providers: int = 6):
        """
        Khởi tạo AIImageProvider với smart image selection + Gemini Vision evaluation
        
        Args:
            gemini_key: Main Gemini API key (keyword generation)
            gemini_eval_key: Gemini API key for image evaluation (v4.0)
            gemini_backup_key: Gemini backup API key (v4.0)
            groq_key, use_ollama: Other AI providers
            unsplash_key, pixabay_key, pexels_key, wallhaven_key: Image provider keys
            google_api_key, google_cx: Google Custom Search credentials (v4.0)
            enable_smart_selection: Use SmartImageSelector
            enable_ai_evaluation: Use Gemini Vision to pick best image (v4.0)
            max_concurrent_providers: Max concurrent provider requests
        """
        # Initialize AI Provider
        try:
            self.ai_provider = MultiAIProvider(
                gemini_key=gemini_key,
                groq_key=groq_key,
                use_ollama=use_ollama,
                ollama_url=ollama_url
            )
            print("[✓] AI Provider initialized")
        except AIProviderError as e:
            raise APIError(f"AI Provider failed: {e}")
        
        # Initialize keyword cache
        self.keyword_cache = KeywordCache(max_size=1000)
        
        # Initialize Image Evaluator (v4.0)
        self.image_evaluator = None
        self.enable_ai_evaluation = enable_ai_evaluation
        
        if enable_ai_evaluation:
            # Try gemini_eval_key first, fallback to gemini_backup_key, then gemini_key
            eval_key = gemini_eval_key or gemini_backup_key or gemini_key
            if eval_key:
                try:
                    self.image_evaluator = GeminiImageEvaluator(eval_key)
                    print("[✓] Gemini Image Evaluator initialized")
                except AIProviderError as e:
                    print(f"[WARN] Image Evaluator init failed: {e}, will use smart selection only")
                    self.image_evaluator = None
        
        # Initialize Smart Image Selector
        self.smart_selector = None
        self.enable_smart_selection = enable_smart_selection
        
        if enable_smart_selection:
            self.smart_selector = SmartImageSelector(max_workers=max_concurrent_providers)
            
            # Add providers to smart selector (priority order)
            if pexels_key:
                try:
                    self.smart_selector.add_provider(
                        "pexels", 
                        PexelsProvider(pexels_key)
                    )
                except Exception as e:
                    print(f"[WARN] Pexels init failed: {e}")
            
            if unsplash_key:
                try:
                    self.smart_selector.add_provider(
                        "unsplash", 
                        UnsplashProvider(unsplash_key)
                    )
                except Exception as e:
                    print(f"[WARN] Unsplash init failed: {e}")
            
            if pixabay_key:
                try:
                    self.smart_selector.add_provider(
                        "pixabay", 
                        PixabayProvider(pixabay_key)
                    )
                except Exception as e:
                    print(f"[WARN] Pixabay init failed: {e}")
            
            # Google Custom Search (v4.0)
            if google_api_key and google_cx:
                try:
                    self.smart_selector.add_provider(
                        "google",
                        GoogleImageProvider(google_api_key, google_cx)
                    )
                except Exception as e:
                    print(f"[WARN] Google Custom Search init failed: {e}")
            
            # Free providers (no API key needed!)
            try:
                self.smart_selector.add_provider(
                    "openverse", 
                    OpenverseProvider()
                )
            except Exception as e:
                print(f"[WARN] Openverse init failed: {e}")
            
            if wallhaven_key:
                try:
                    self.smart_selector.add_provider(
                        "wallhaven", 
                        WallhavenProvider(wallhaven_key)
                    )
                except Exception as e:
                    print(f"[WARN] Wallhaven init failed: {e}")
            
            # Lorem Picsum (instant, NO API key!)
            try:
                self.smart_selector.add_provider(
                    "lorem_picsum", 
                    LoremPicsumProvider()
                )
            except Exception as e:
                print(f"[WARN] Lorem Picsum init failed: {e}")
            
            if not self.smart_selector.providers:
                raise APIError("Không có image provider nào được cấu hình!")
            
            print(f"[✓] Smart Image Selector initialized with {len(self.smart_selector.providers)} providers")
    
    def get_image_url(self, vocabulary: str, definition: str) -> str:
        """
        Lấy URL ảnh tốt nhất - OPTIMIZED
        
        Flow:
        1. Check keyword cache (FAST - O(1))
        2. Generate keyword từ AI (with fallback chain)
        3. Search images concurrently (all providers in parallel)
        4. If enable_ai_evaluation: Use Gemini Vision to pick best (with fallback)
        5. Otherwise: Return smart-ranked best
        """
        # ⚡ STEP 1: Try keyword cache FIRST (early exit)
        cache_key = self.keyword_cache.make_key(vocabulary, definition)
        cached_keyword = self.keyword_cache.get(cache_key)
        
        if cached_keyword:
            keyword = cached_keyword
        else:
            # STEP 2: Generate keyword từ AI
            try:
                keyword, provider_name = self.ai_provider.generate_keyword(
                    vocabulary, 
                    definition
                )
                self.keyword_cache.set(cache_key, keyword)
            except AIProviderError as e:
                raise APIError(f"Keyword generation failed: {e}")
        
        # ⚡ STEP 3: Smart image search (concurrent, with timeout)
        if not (self.enable_smart_selection and self.smart_selector):
            raise APIError("Image selection disabled")
        
        try:
            # ⚡ Get 8 candidates for evaluation (or use directly if no eval)
            top_n = 8 if (self.enable_ai_evaluation and self.image_evaluator) else 1
            candidate_urls = self.smart_selector.search_smart(keyword, top_n=top_n)
            
            if not candidate_urls:
                raise APIError(f"No images found for: '{keyword}'")
            
            # ⚡ STEP 4: AI Evaluation (if enabled)
            if self.enable_ai_evaluation and self.image_evaluator:
                try:
                    best_url = self.image_evaluator.evaluate_images(
                        candidate_urls,
                        vocabulary,
                        definition
                    )
                    return best_url
                except AIProviderError as e:
                    # ⚡ Fallback: return first from smart selection
                    return candidate_urls[0]
            else:
                # ⚡ Return smart-selected best directly
                return candidate_urls[0]
        
        except ImageProviderError as e:
            raise APIError(f"Image search failed: {e}")

