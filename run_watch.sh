#!/bin/bash
# Chạy script ở chế độ WATCH - tự động kiểm tra và thêm ảnh mỗi phút
# Mặc định dùng deck "1 all", hoặc truyền deck qua argument

DECK="${1:-1 all}"

echo "🔄 Bắt đầu Watch Mode - tự động thêm ảnh khi có từ mới"
echo "📚 Deck: $DECK"
echo "=================================================="
echo "Kiểm tra mỗi 60 giây"
echo "Nhấn Ctrl+C để dừng"
echo ""

/usr/local/bin/python3 /Users/nguyenkhanh/Desktop/anki_image.py --watch --interval 60 --deck "$DECK"

EXIT_CODE=$?
echo ""
echo "👋 Dừng Watch Mode (Exit code: $EXIT_CODE)"
echo ""
