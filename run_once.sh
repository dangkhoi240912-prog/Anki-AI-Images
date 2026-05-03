#!/bin/bash
# Chạy script một lần - thêm ảnh cho tất cả từ mới chưa có ảnh
# Mặc định dùng deck "1 all", hoặc truyền deck qua argument

DECK="${1:-1 all}"

echo "🎨 Bắt đầu thêm ảnh vào thẻ Anki (chế độ một lần)"
echo "📚 Deck: $DECK"
echo "=================================================="
echo ""

/usr/local/bin/python3 /Users/nguyenkhanh/Desktop/anki_image.py --deck "$DECK"

echo ""
echo "✅ Hoàn thành!"
echo ""
