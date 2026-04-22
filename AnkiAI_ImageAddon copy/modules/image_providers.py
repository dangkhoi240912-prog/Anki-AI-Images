"""
Image Providers v4.1 - OPTIMIZED Multi-Provider System
Hỗ trợ: Pexels, Unsplash, Pixabay, Google, Lorem Picsum, Openverse, Wallhaven

v4.1 Optimizations:
- HTTP session pooling & connection reuse
- Aggressive timeout tuning (3-5s for fast providers)
- Parallel requests với timeout-first strategy
- Response caching với TTL
- Memory-efficient image scoring
- Early exit on cache hit
"""

import requests
import json
from typing import Optional, Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FuturesTimeoutError
import threading
from datetime import datetime, timedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class ImageProviderError(Exception):
    """Exception cho image provider errors"""
    pass


class ImageScore:
    """Điểm số cho mỗi ảnh (dùng cho smart selection)"""
    
    def __init__(self, url: str, provider: str, title: str = ""):
        self.url = url
        self.provider = provider
        self.title = title
        self.score = 0
        self.details = {}
    
    def calculate_score(self):
        """Tính điểm cho ảnh dựa trên nhiều tiêu chí"""
        # Base score từ provider (reliability)
        provider_score = {
            "pexels": 95,      # Highest quality, fast
            "unsplash": 90,    # Very good quality
            "pixabay": 85,     # Good quality
            "openverse": 75,   # Decent quality, slower
            "wallhaven": 80,   # Good, but need verification
            "lorem_picsum": 60 # Fast, but generic
        }
        
        self.score = provider_score.get(self.provider, 50)
        self.details["provider_base"] = self.score
        
        # URL length quality factor (shorter = cleaner)
        if self.url:
            url_length_penalty = min(len(self.url) / 500, 20)  # Max -20 points
            self.score -= url_length_penalty
            self.details["url_quality"] = -url_length_penalty
        
        # Title relevance (if available)
        if self.title:
            title_length_bonus = min(len(self.title) / 5, 10)  # Max +10 points
            self.score += title_length_bonus
            self.details["title_relevance"] = title_length_bonus
        
        return max(0, min(100, self.score))  # Clamp to 0-100


class ImageCache:
    """Cache cho image search results (lightweight, thread-safe)"""
    
    def __init__(self, ttl_minutes: int = 120):
        self.cache: Dict[str, Dict] = {}
        self.ttl = timedelta(minutes=ttl_minutes)
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[List[str]]:
        """Lấy URL list từ cache - O(1)"""
        with self.lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            if datetime.now() > entry["expires"]:
                del self.cache[key]
                return None
            
            return entry["urls"]
    
    def set(self, key: str, urls: List[str]):
        """Lưu URL list vào cache"""
        with self.lock:
            self.cache[key] = {
                "urls": urls,
                "expires": datetime.now() + self.ttl
            }
    
    def clear(self):
        """Xóa toàn bộ cache"""
        with self.lock:
            self.cache.clear()
    
    def size(self) -> int:
        """Lấy số items trong cache"""
        with self.lock:
            return len(self.cache)
            self.cache.clear()


class PexelsProvider:
    """Pexels API - Fast, high quality, FREE - OPTIMIZED"""
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ImageProviderError("Pexels API key required")
        self.api_key = api_key
        self.base_url = "https://api.pexels.com/v1"
        self.name = "pexels"
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create optimized session"""
        session = requests.Session()
        adapter = HTTPAdapter(
            pool_connections=5,
            pool_maxsize=5,
            max_retries=Retry(total=1, backoff_factor=0.05)
        )
        session.mount('https://', adapter)
        return session
    
    def search(self, keyword: str, per_page: int = 3) -> List[Dict]:
        """Tìm ảnh trên Pexels - FAST"""
        try:
            response = self.session.get(
                f"{self.base_url}/search",
                headers={"Authorization": self.api_key},
                params={
                    "query": keyword,
                    "per_page": per_page,
                    "page": 1
                },
                timeout=4  # ⚡ Giảm từ 6s
            )
            
            if response.status_code != 200:
                raise ImageProviderError(f"Pexels {response.status_code}")
            
            results = response.json().get("photos", [])
            if not results:
                raise ImageProviderError("No results")
            
            return [
                {
                    "url": photo["src"]["large"],
                    "title": photo.get("alt", keyword),
                    "provider": self.name
                }
                for photo in results[:per_page]
            ]
        
        except requests.exceptions.Timeout:
            raise ImageProviderError("Pexels timeout")
        except Exception as e:
            raise ImageProviderError(str(e))


class UnsplashProvider:
    """Unsplash API - Very good quality, FREE - OPTIMIZED"""
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ImageProviderError("Unsplash API key required")
        self.api_key = api_key
        self.base_url = "https://api.unsplash.com"
        self.name = "unsplash"
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create optimized session"""
        session = requests.Session()
        adapter = HTTPAdapter(
            pool_connections=5,
            pool_maxsize=5,
            max_retries=Retry(total=1, backoff_factor=0.05)
        )
        session.mount('https://', adapter)
        return session
    
    def search(self, keyword: str, per_page: int = 3) -> List[Dict]:
        """Tìm ảnh trên Unsplash - FAST"""
        try:
            response = self.session.get(
                f"{self.base_url}/search/photos",
                headers={"Authorization": f"Client-ID {self.api_key}"},
                params={
                    "query": keyword,
                    "per_page": per_page,
                    "page": 1,
                    "orientation": "landscape"
                },
                timeout=4  # ⚡ Giảm từ 6s
            )
            
            if response.status_code != 200:
                raise ImageProviderError(f"Unsplash {response.status_code}")
            
            results = response.json().get("results", [])
            if not results:
                raise ImageProviderError("No results")
            
            return [
                {
                    "url": photo["urls"]["regular"],
                    "title": photo.get("description", keyword),
                    "provider": self.name
                }
                for photo in results[:per_page]
            ]
        
        except requests.exceptions.Timeout:
            raise ImageProviderError("Unsplash timeout")
        except Exception as e:
            raise ImageProviderError(str(e))


class PixabayProvider:
    """Pixabay API - Good quality, FREE - OPTIMIZED"""
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ImageProviderError("Pixabay API key required")
        self.api_key = api_key
        self.base_url = "https://pixabay.com/api"
        self.name = "pixabay"
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create optimized session"""
        session = requests.Session()
        adapter = HTTPAdapter(
            pool_connections=5,
            pool_maxsize=5,
            max_retries=Retry(total=1, backoff_factor=0.05)
        )
        session.mount('https://', adapter)
        return session
    
    def search(self, keyword: str, per_page: int = 3) -> List[Dict]:
        """Tìm ảnh trên Pixabay - FAST"""
        try:
            response = self.session.get(
                self.base_url,
                params={
                    "key": self.api_key,
                    "q": keyword,
                    "image_type": "photo",
                    "per_page": per_page,
                    "safesearch": True,
                    "order": "popular"
                },
                timeout=4  # ⚡ Giảm từ 6s
            )
            
            if response.status_code != 200:
                raise ImageProviderError(f"Pixabay {response.status_code}")
            
            results = response.json().get("hits", [])
            if not results:
                raise ImageProviderError("No results")
            
            return [
                {
                    "url": photo["largeImageURL"],
                    "title": keyword,
                    "provider": self.name
                }
                for photo in results[:per_page]
            ]
        
        except requests.exceptions.Timeout:
            raise ImageProviderError("Pixabay timeout")
        except Exception as e:
            raise ImageProviderError(str(e))


class GoogleImageProvider:
    """Google Custom Search API - Comprehensive image results - OPTIMIZED"""
    
    def __init__(self, api_key: str, cx: str):
        """Khởi tạo Google Custom Search API provider"""
        if not api_key or not cx:
            raise ImageProviderError("Google API key and CX required")
        self.api_key = api_key.strip()
        self.cx = cx.strip()
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.name = "google"
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create optimized session"""
        session = requests.Session()
        adapter = HTTPAdapter(
            pool_connections=3,
            pool_maxsize=3,
            max_retries=Retry(total=1, backoff_factor=0.05)
        )
        session.mount('https://', adapter)
        return session
    
    def search(self, keyword: str, per_page: int = 3) -> List[Dict]:
        """Tìm ảnh bằng Google Custom Search - FAST"""
        try:
            response = self.session.get(
                self.base_url,
                params={
                    "q": keyword,
                    "cx": self.cx,
                    "searchType": "image",
                    "num": min(per_page, 10),
                    "imgSize": "large",
                    "imgType": "photo",
                    "key": self.api_key
                },
                timeout=5  # ⚡ Giảm từ 6s
            )
            
            if response.status_code != 200:
                error_info = response.json().get("error", {})
                error_msg = error_info.get("message", response.text)
                raise ImageProviderError(f"Google {error_msg}")
            
            results = response.json().get("items", [])
            if not results:
                raise ImageProviderError("No results")
            
            return [
                {
                    "url": result.get("link", ""),
                    "title": result.get("title", keyword),
                    "provider": self.name
                }
                for result in results[:per_page]
            ]
        
        except requests.exceptions.Timeout:
            raise ImageProviderError("Google timeout")
        except Exception as e:
            raise ImageProviderError(str(e))


class LoremPicsumProvider:
    """Lorem Picsum - Instant, NO API KEY NEEDED! ✨"""
    
    def __init__(self):
        self.base_url = "https://picsum.photos"
        self.name = "lorem_picsum"
    
    def search(self, keyword: str, per_page: int = 3) -> List[Dict]:
        """
        Lorem Picsum không thực sự search, nhưng sinh ảnh random
        Vậy nên dùng nó như fallback nhanh
        """
        try:
            # Lorem Picsum không có search API
            # Nhưng có endpoint list
            # Vì thế dùng nó như quick fallback
            
            images = []
            for i in range(per_page):
                # Sử dụng seed để có consistent results
                url = f"{self.base_url}/600/400?random={i}"
                images.append({
                    "url": url,
                    "title": f"{keyword} (stock {i+1})",
                    "provider": self.name
                })
            
            return images
        
        except Exception as e:
            raise ImageProviderError(str(e))


class OpenverseProvider:
    """Openverse (Creative Commons images) - FREE - OPTIMIZED"""
    
    def __init__(self):
        self.base_url = "https://api.openverse.engineering/v1"
        self.name = "openverse"
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create optimized session"""
        session = requests.Session()
        adapter = HTTPAdapter(
            pool_connections=3,
            pool_maxsize=3,
            max_retries=Retry(total=1, backoff_factor=0.05)
        )
        session.mount('https://', adapter)
        return session
    
    def search(self, keyword: str, per_page: int = 3) -> List[Dict]:
        """Tìm ảnh từ Openverse - FAST"""
        try:
            response = self.session.get(
                f"{self.base_url}/images",
                params={
                    "q": keyword,
                    "page_size": per_page,
                    "page": 1,
                    "license": "CC0,CCBY,CCBYSA"
                },
                timeout=5,  # ⚡ Giảm từ 8s
                headers={"User-Agent": "AnkiAI/4.1"}
            )
            
            if response.status_code != 200:
                raise ImageProviderError(f"Openverse {response.status_code}")
            
            results = response.json().get("results", [])
            if not results:
                raise ImageProviderError("No results")
            
            return [
                {
                    "url": image["url"],
                    "title": image.get("title", keyword),
                    "provider": self.name
                }
                for image in results[:per_page]
            ]
        
        except requests.exceptions.Timeout:
            raise ImageProviderError("Openverse timeout")
        except Exception as e:
            raise ImageProviderError(str(e))


class WallhavenProvider:
    """Wallhaven API - Good quality wallpapers - OPTIMIZED"""
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.base_url = "https://wallhaven.cc/api/v1"
        self.name = "wallhaven"
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create optimized session"""
        session = requests.Session()
        adapter = HTTPAdapter(
            pool_connections=3,
            pool_maxsize=3,
            max_retries=Retry(total=1, backoff_factor=0.05)
        )
        session.mount('https://', adapter)
        return session
    
    def search(self, keyword: str, per_page: int = 3) -> List[Dict]:
        """Tìm ảnh từ Wallhaven - FAST"""
        try:
            params = {
                "q": keyword,
                "limit": per_page,
                "page": 1,
                "sorting": "relevance",
                "order": "desc"
            }
            
            if self.api_key:
                params["apikey"] = self.api_key
            
            response = self.session.get(
                f"{self.base_url}/search",
                params=params,
                timeout=5,  # ⚡ Giảm từ 7s
                headers={"User-Agent": "AnkiAI/4.1"}
            )
            
            if response.status_code != 200:
                raise ImageProviderError(f"Wallhaven {response.status_code}")
            
            results = response.json().get("data", [])
            if not results:
                raise ImageProviderError("No results")
            
            return [
                {
                    "url": wall["path"],
                    "title": wall.get("tags", [{}])[0].get("name", keyword) if wall.get("tags") else keyword,
                    "provider": self.name
                }
                for wall in results[:per_page]
            ]
        
        except requests.exceptions.Timeout:
            raise ImageProviderError("Wallhaven timeout")
        except Exception as e:
            raise ImageProviderError(str(e))


class SmartImageSelector:
    """
    Intelligent image selection system - OPTIMIZED
    Concurrent search, fast ranking, smart caching
    """
    
    def __init__(self, max_workers: int = 6):
        self.max_workers = min(max_workers, 8)  # ⚡ Cap tối đa 8 workers
        self.cache = ImageCache(ttl_minutes=120)
        self.providers: List[Tuple[str, any]] = []
    
    def add_provider(self, name: str, provider):
        """Thêm image provider"""
        self.providers.append((name, provider))
    
    def _search_provider(self, provider: Tuple[str, any], keyword: str) -> List[ImageScore]:
        """Search một provider, return scored images"""
        name, provider_obj = provider
        
        try:
            results = provider_obj.search(keyword, per_page=2)  # ⚡ Giảm từ 3 xuống 2 per provider
            scored_images = []
            
            for img in results:
                score_obj = ImageScore(
                    url=img["url"],
                    provider=provider_obj.name,
                    title=img.get("title", "")
                )
                score_obj.calculate_score()
                scored_images.append(score_obj)
            
            return scored_images
        
        except Exception as e:
            return []  # Silent fail, continue with next provider
    
    def search_smart(self, keyword: str, top_n: int = 8) -> List[str]:
        """
        Concurrent search từ tất cả providers
        Rank based on quality score
        Return top N best URLs - OPTIMIZED
        """
        cache_key = f"smart_{keyword}".lower()
        
        # ⚡ Try cache FIRST - early exit
        cached = self.cache.get(cache_key)
        if cached:
            return cached[:top_n]
        
        all_scored_images = []
        
        # ⚡ Parallel searches với timeout
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._search_provider, provider, keyword): provider[0]
                for provider in self.providers
            }
            
            for future in as_completed(futures, timeout=10):  # ⚡ Global timeout 10s
                try:
                    results = future.result(timeout=5)  # ⚡ Per-task timeout 5s
                    all_scored_images.extend(results)
                except FuturesTimeoutError:
                    continue
                except Exception:
                    continue
        
        if not all_scored_images:
            raise ImageProviderError(f"No images found for: '{keyword}'")
        
        # ⚡ Sort in-place để tiết kiệm memory
        all_scored_images.sort(key=lambda x: x.calculate_score(), reverse=True)
        
        # Return top N URLs
        top_urls = [img.url for img in all_scored_images[:top_n]]
        
        # Cache result
        self.cache.set(cache_key, top_urls)
        
        return top_urls
    
    def get_best_image_url(self, keyword: str) -> str:
        """Lấy ảnh tốt nhất (single best)"""
        urls = self.search_smart(keyword, top_n=1)
        return urls[0] if urls else None
