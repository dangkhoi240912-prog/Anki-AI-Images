import requests
import time
import re
import base64
import sys
import json
import os
from typing import Optional, Dict, Any, List, Tuple, Set
import logging
from urllib.parse import quote
from datetime import datetime

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cache file để lưu note đã xử lý
CACHE_FILE = "/Users/nguyenkhanh/Desktop/anki_image_cache.json"

# ========== CẤU HÌNH ==========
ANKI_URL = "http://localhost:8765"
DECK_NAME = "1 all"  # Ví dụ: "English_C2"
ANKI_FIELD_VOCAB = "Mặt trước"
ANKI_FIELD_EXAMPLE = "ví dụ"
ANKI_FIELD_IMAGE = "image"

# API Keys - để trống nếu không dùng
PIXABAY_API_KEY = "55117827-ef3b6373bdbb292c40b355dce"
UNSPLASH_API_KEY = "wAvIdPMKDnFoIBWtcCj7tRkG-xdKdM5U4u0yiTYH4sc"  # getkey từ unsplash.com
PEXELS_API_KEY = "d2NTv2i8ZmvdP7SXy3ehSiKLtnY1qDIIslE2FGZIoOsnbsQ7pbF0BKip"    # getkey từ pexels.com

# Cấu hình chần lựa chọn ảnh
MAX_RETRIES = 3
RETRY_DELAY = 2
IMAGE_QUALITY_MIN = 5000  # bytes (5KB), kích thước tối thiểu - Pexels images thường 6-14KB
INTERACTIVE_MODE = False  # True = hiển thị options để user chọn
MAX_ALTERNATIVES = 3  # Số lượng option tối đa để hiển thị
WATCH_MODE = True  # True = tự động chạy lại mỗi N giây
WATCH_INTERVAL = 60  # giây - kiểm tra mỗi 1 phút

def load_cache() -> Set[int]:
    """Tải danh sách note đã thêm ảnh thành công từ cache"""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                data = json.load(f)
                return set(data.get('processed_notes', []))
    except Exception as e:
        logger.warning(f"Lỗi load cache: {e}")
    return set()

def save_cache(processed_notes: Set[int]):
    """Lưu danh sách note đã thêm ảnh thành công vào cache"""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump({'processed_notes': list(processed_notes), 'last_update': datetime.now().isoformat()}, f)
    except Exception as e:
        logger.warning(f"Lỗi save cache: {e}")

class ImageSource:
    """Class cho mỗi source ảnh"""
    def get_images(self, query: str) -> List[Dict[str, Any]]:
        """Trả về list ảnh với info: {'url': str, 'source': str, 'title': str, 'likes': int}"""
        raise NotImplementedError

class PixabaySource(ImageSource):
    """Tìm ảnh từ Pixabay"""
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def get_images(self, query: str) -> List[Dict[str, Any]]:
        if not self.api_key or "DÁN_API_KEY" in self.api_key:
            return []
        
        try:
            url = f"https://pixabay.com/api/?key={self.api_key}&q={query}&image_type=photo&per_page=5&min_width=400&min_height=300"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            images = []
            for hit in data.get('hits', []):
                images.append({
                    'url': hit['webformatURL'],
                    'source': 'Pixabay',
                    'title': hit.get('tags', 'image'),
                    'likes': hit.get('likes', 0),
                    'size': hit.get('imageSize', 0)
                })
            return images
        except Exception as e:
            logger.warning(f"Lỗi Pixabay: {e}")
            return []

class UnsplashSource(ImageSource):
    """Tìm ảnh từ Unsplash"""
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def get_images(self, query: str) -> List[Dict[str, Any]]:
        if not self.api_key:
            return []
        
        try:
            url = "https://api.unsplash.com/search/photos"
            headers = {"Authorization": f"Client-ID {self.api_key}"}
            params = {"query": query, "per_page": 5, "order_by": "relevant"}
            
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            images = []
            for photo in data.get('results', []):
                images.append({
                    'url': photo['urls']['regular'],
                    'source': 'Unsplash',
                    'title': photo.get('description', photo.get('alt_description', 'image')),
                    'likes': photo.get('likes', 0),
                    'size': 0
                })
            return images
        except Exception as e:
            logger.warning(f"Lỗi Unsplash: {e}")
            return []

class PexelsSource(ImageSource):
    """Tìm ảnh từ Pexels"""
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def get_images(self, query: str) -> List[Dict[str, Any]]:
        if not self.api_key:
            return []
        
        try:
            url = "https://api.pexels.com/v1/search"
            headers = {"Authorization": self.api_key}
            params = {"query": query, "per_page": 5}
            
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            images = []
            for photo in data.get('photos', []):
                images.append({
                    'url': photo['src']['medium'],
                    'source': 'Pexels',
                    'title': photo.get('photographer', 'image'),
                    'likes': 0,
                    'size': 0
                })
            return images
        except Exception as e:
            logger.warning(f"Lỗi Pexels: {e}")
            return []

def invoke(action: str, **params) -> Dict[str, Any]:
    """Gọi AnkiConnect API với retry logic"""
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.post(ANKI_URL, json={'action': action, 'version': 6, 'params': params}, timeout=10)
            resp.raise_for_status()
            result = resp.json()
            if 'error' in result and result['error']:
                logger.error(f"AnkiConnect error - {action}: {result['error']}")
                return {'error': result['error'], 'result': None}
            return result
        except requests.exceptions.ConnectionError:
            logger.warning(f"Lỗi kết nối AnkiConnect - {action} (lần {attempt + 1}/{MAX_RETRIES})")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout AnkiConnect - {action} (lần {attempt + 1}/{MAX_RETRIES})")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
        except Exception as e:
            logger.error(f"Lỗi gọi AnkiConnect - {action}: {type(e).__name__}: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    return {'error': f'AnkiConnect không phản hồi sau {MAX_RETRIES} lần thử', 'result': None}

def download_image(url: str) -> Optional[Tuple[str, int]]:
    """Tải ảnh từ URL, trả về (base64_data, size)"""
    try:
        resp = requests.get(url, timeout=10, allow_redirects=True, stream=True)
        resp.raise_for_status()
        data = resp.content
        size = len(data)
        
        # Kiểm tra kích thước tối thiểu
        if size < IMAGE_QUALITY_MIN:
            logger.warning(f"Ảnh quá nhỏ ({size} bytes), bỏ qua")
            return None
        
        # Encode to base64 for AnkiConnect
        base64_data = base64.b64encode(data).decode('utf-8')
        return (base64_data, size)
    except Exception as e:
        logger.error(f"Lỗi tải ảnh: {e}")
        return None

def extract_keywords(text: str, top_n: int = 3) -> List[str]:
    """Trích xuất từ khóa từ text (loại bỏ từ phổ biến và các ký tự đặc biệt)"""
    try:
        # Các từ phổ biến không cần, tập hợp tiếng Anh
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
                     'must', 'can', 'of', 'in', 'to', 'for', 'at', 'by', 'from', 'as', 'on', 'it', 'this', 'that',
                     'with', 'he', 'she', 'they', 'we', 'i', 'you', 'what', 'which', 'who', 'when', 'where', 'why', 'how'}
        
        # Extract từ từ HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Loại bỏ số và ký tự đặc biệt
        text = re.sub(r"[0-9'\"\(\)\[\]\{\}\.\,\!\?\;\:\-]*", ' ', text)
        
        # Normalize text và tách từ (hỗ trợ Unicode)
        text = text.lower()
        words = re.findall(r'\b[\w]+\b', text, re.UNICODE)
        # Lọc từ phổ biến và lấy top N
        keywords = [w for w in words if len(w) > 2 and w not in stopwords]
        
        return list(dict.fromkeys(keywords))[:top_n]  # Remove duplicates, lấy top N
    except Exception as e:
        logger.warning(f"Lỗi extract keywords: {e}")
        return []

def get_best_images(vocab: str, example: str = "") -> List[Dict[str, Any]]:
    """Tìm ảnh từ nhiều source, sắp xếp theo quality"""
    
    # Xây dựng search query - loại bỏ ký tự đặc biệt từ vocab (e.g. "schedule (n)" -> "schedule")
    clean_vocab = re.sub(r"\s*\([^)]*\)", "", vocab).strip()  # Loại bỏ "(n)", "(v)", etc
    clean_vocab = re.sub(r"[0-9'\"\[\]\{\}\.\,\!\?\;\:\-]", "", clean_vocab).strip()  # Loại bỏ số và ký tự đặc biệt
    
    search_query = clean_vocab if clean_vocab else vocab
    if example:
        keywords = extract_keywords(example)
        if keywords:
            search_query = f"{clean_vocab} {keywords[0]}"
    
    logger.info(f"  Tìm kiếm: '{search_query}'")
    
    # Khởi tạo sources
    sources = []
    if PIXABAY_API_KEY and "DÁN_API_KEY" not in PIXABAY_API_KEY:
        sources.append(PixabaySource(PIXABAY_API_KEY))
    if UNSPLASH_API_KEY:
        sources.append(UnsplashSource(UNSPLASH_API_KEY))
    if PEXELS_API_KEY:
        sources.append(PexelsSource(PEXELS_API_KEY))
    
    # Nếu không có source nào được cấu hình
    if not sources:
        logger.warning("Chưa cấu hình API key cho bất kỳ image source nào!")
        return []
    
    # Tìm ảnh từ tất cả sources
    all_images = []
    for source in sources:
        try:
            images = source.get_images(search_query)
            all_images.extend(images)
            logger.debug(f"  {source.__class__.__name__}: tìm được {len(images)} ảnh")
        except Exception as e:
            logger.warning(f"Lỗi lấy ảnh từ {source.__class__.__name__}: {e}")
    
    if not all_images:
        logger.warning(f"Không tìm được ảnh nào cho '{vocab}'")
        return []
    
    # Sắp xếp theo: likes/popularity (giảm dần)
    all_images.sort(key=lambda x: x.get('likes', 0), reverse=True)
    
    logger.info(f"  Tìm được {len(all_images)} ảnh từ {len(sources)} source")
    return all_images

def select_image(images: List[Dict[str, Any]], vocab: str) -> Optional[Dict[str, Any]]:
    """Chọn ảnh tốt nhất hoặc yêu cầu user chọn"""
    
    if not images:
        return None
    
    if not INTERACTIVE_MODE:
        # Chế độ tự động: chọn ảnh đầu tiên (đã sắp xếp theo quality)
        return images[0]
    
    # Chế độ interactive: hiển thị options
    print(f"\n{'='*60}")
    print(f"📷 Chọn ảnh cho từ: {vocab}")
    print(f"{'='*60}")
    
    for idx, img in enumerate(images[:MAX_ALTERNATIVES], 1):
        print(f"\n[{idx}] {img['source']} - {img['title'][:50]}")
        print(f"    👍 Likes: {img['likes']}")
        print(f"    🔗 {img['url'][:60]}...")
    
    print(f"\n[0] Bỏ qua từ này")
    print(f"[99] Tìm lại")
    
    try:
        choice = input(f"\nChọn (1-{min(len(images), MAX_ALTERNATIVES)}, 0, hoặc 99): ").strip()
        choice = int(choice)
        
        if choice == 0:
            return None
        elif 1 <= choice <= min(len(images), MAX_ALTERNATIVES):
            return images[choice - 1]
        elif choice == 99:
            # Tìm lại với query khác
            new_query = input("Query mới: ").strip()
            if new_query:
                # Tái sử dụng hàm nhưng với query mới (đơn giản hoá)
                return None  # Returning None để skip, trong main loop sẽ retry nếu cần
    except (ValueError, KeyboardInterrupt):
        pass
    
    return images[0]  # Fallback: chọn ảnh đầu tiên

def get_field_value(note: Dict[str, Any], field_name: str) -> Optional[str]:
    """Lấy giá trị field an toàn"""
    try:
        return note.get('fields', {}).get(field_name, {}).get('value', '')
    except Exception as e:
        logger.error(f"Lỗi đọc field {field_name}: {e}")
        return None

def main():
    """Hàm chính"""
    processed_success = load_cache()  # Cache chỉ lưu thẻ đã thêm ảnh thành công
    run_count = 0
    
    while True:
        run_count += 1
        logger.info("="*60)
        logger.info(f"🎨 Lần chạy #{run_count} - {datetime.now().strftime('%H:%M:%S')}")
        logger.info("="*60)
        
        # Lấy tất cả note trong Deck
        result = invoke("findNotes", query=f'deck:"{DECK_NAME}"')
        if result.get('error'):
            logger.error(f"Lỗi tìm note: {result['error']}")
            if not WATCH_MODE:
                return
            time.sleep(WATCH_INTERVAL)
            continue
        
        notes = result.get('result', [])
        if not notes:
            logger.info(f"Không tìm được note nào trong deck {DECK_NAME}")
            if not WATCH_MODE:
                return
            time.sleep(WATCH_INTERVAL)
            continue
        
        logger.info(f"✓ Tìm được {len(notes)} note trong deck")
        
        # Lấy thông tin chi tiết tất cả note (để kiểm tra xem có ảnh hay không)
        result = invoke("notesInfo", notes=notes)
        if result.get('error'):
            logger.error(f"Lỗi lấy thông tin note: {result['error']}")
            if not WATCH_MODE:
                return
            time.sleep(WATCH_INTERVAL)
            continue
        
        notes_info = result.get('result', [])
        
        # Lọc những note chưa có ảnh và chưa được xử lý thành công
        notes_to_process = []
        for note in notes_info:
            image_value = get_field_value(note, ANKI_FIELD_IMAGE)
            note_id = note.get('noteId')
            # Nếu chưa có ảnh VÀ chưa được xử lý thành công → thêm vào danh sách
            if not image_value and note_id not in processed_success:
                notes_to_process.append(note)
        
        if not notes_to_process:
            status_msg = "Tất cả note đã có ảnh rồi!" if len(notes_info) > 0 else "Không có note nào"
            logger.info(f"⊘ {status_msg} (đã xử lý thành công: {len(processed_success)})")
            if not WATCH_MODE:
                logger.info("Hoàn thành!")
                return
            time.sleep(WATCH_INTERVAL)
            continue
        
        success_count = 0
        skip_count = 0
        error_count = 0
        
        logger.info(f"\n📋 Xử lý {len(notes_to_process)} note chưa có ảnh...\n")
        
        for idx, note in enumerate(notes_to_process, 1):
            try:
                note_id = note['noteId']
                vocab = get_field_value(note, ANKI_FIELD_VOCAB)
                if not vocab:
                    logger.warning(f"[{idx}/{len(notes_to_process)}] Không có từ vựng, bỏ qua")
                    skip_count += 1
                    continue
                
                example = get_field_value(note, ANKI_FIELD_EXAMPLE)
                logger.info(f"\n[{idx}/{len(notes_to_process)}] 🔍 Từ: {vocab}")
                
                # Tìm ảnh từ nhiều sources
                images = get_best_images(vocab, example)
                
                if images:
                    # Chọn ảnh tốt nhất
                    selected_image = select_image(images, vocab)
                    
                    if selected_image:
                        # Tải ảnh xuống
                        logger.info(f"  ⬇️  Tải ảnh từ {selected_image['source']}...")
                        img_result = download_image(selected_image['url'])
                        
                        if img_result:
                            img_data_base64, img_size = img_result
                            filename = f"image_{note['noteId']}.jpg"
                            
                            logger.debug(f"  [DEBUG] Kích thước ảnh: {img_size} bytes")
                            
                            # Lưu vào bộ nhớ media của Anki (base64 encoded)
                            logger.debug(f"  [DEBUG] Lưu file: {filename}")
                            result = invoke("storeMediaFile", filename=filename, data=img_data_base64)
                            if not result.get('error'):
                                # Cập nhật field Image
                                logger.debug(f"  [DEBUG] Cập nhật note: {note['noteId']}")
                                result = invoke("updateNoteFields", note={
                                    "id": note['noteId'],
                                    "fields": {ANKI_FIELD_IMAGE: f'<img src="{filename}">'}
                                })
                                if not result.get('error'):
                                    logger.info(f"  ✅ Thành công! ({img_size//1000}KB, {selected_image['source']})")
                                    success_count += 1
                                    processed_success.add(note_id)  # Chỉ lưu khi thành công
                                else:
                                    logger.error(f"  ❌ Lỗi cập nhật note: {result['error']}")
                                    error_count += 1
                            else:
                                logger.error(f"  ❌ Lỗi lưu ảnh: {result['error']}")
                                error_count += 1
                        else:
                            logger.warning(f"  ⚠️  Không tải được ảnh")
                            error_count += 1
                    else:
                        logger.info(f"  ⊘ Bỏ qua")
                        skip_count += 1
                else:
                    logger.warning(f"  ⚠️  Không tìm được ảnh nào")
                    skip_count += 1
                    
            except Exception as e:
                logger.error(f"[{idx}] ❌ Lỗi xử lý note: {e}")
                error_count += 1
        
        # Lưu cache (chỉ những thẻ đã thêm ảnh thành công)
        save_cache(processed_success)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 KẾT QUẢ LẦN CHẠY #{run_count}")
        logger.info(f"{'='*60}")
        logger.info(f"  ✅ Thành công: {success_count}")
        logger.info(f"  ⊘ Bỏ qua: {skip_count}")
        logger.info(f"  ❌ Lỗi: {error_count}")
        logger.info(f"  📝 Tổng note đã thêm ảnh: {len(processed_success)}")
        logger.info(f"{'='*60}\n")
        
        # Nếu không ở chế độ watch, thoát
        if not WATCH_MODE:
            logger.info("✨ Hoàn thành!")
            return
        
        # Chế độ watch: đợi rồi chạy lại
        logger.info(f"⏳ Chế độ Watch - kiểm tra lại trong {WATCH_INTERVAL}s...")
        logger.info(f"Nhấn Ctrl+C để dừng\n")
        try:
            time.sleep(WATCH_INTERVAL)
        except KeyboardInterrupt:
            logger.info("\n\n👋 Dừng Watch Mode")
            return

if __name__ == "__main__":
    # Kiểm tra command line arguments
    watch_mode = "--watch" in sys.argv or "--auto" in sys.argv
    interval_arg = None
    deck_arg = None
    
    # Tìm --interval N
    for i, arg in enumerate(sys.argv):
        if arg == "--interval" and i + 1 < len(sys.argv):
            try:
                interval_arg = int(sys.argv[i + 1])
            except ValueError:
                pass
        elif arg == "--deck" and i + 1 < len(sys.argv):
            deck_arg = sys.argv[i + 1]
    
    # Nếu có --deck argument, override DECK_NAME
    if deck_arg:
        DECK_NAME = deck_arg
    
    if watch_mode:
        logger.info(f"🔄 Bắt đầu ở chế độ WATCH (tự động chạy lại)")
        WATCH_MODE = True
        if interval_arg:
            WATCH_INTERVAL = interval_arg
    else:
        logger.info("▶️  Chế độ một lần")
        WATCH_MODE = False
    
    logger.info(f"📚 Deck: {DECK_NAME}\n")
    
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\n👋 Dừng chương trình")
        sys.exit(0)