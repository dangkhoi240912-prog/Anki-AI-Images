#!/bin/bash
# Script để chọn deck và chạy Watch Mode

echo "🎨 Anki Image Auto-Add - Chọn Deck"
echo "===================================="
echo ""

# Danh sách các main decks
DECKS=(
    "1 all"
    "English Collocations in Use (Advanced)"
    "English Conversation Course - Beginner"
    "English Grammar In Use (Intermediate)"
    "English Idioms in Use (Advanced)"
    "English Vocabulary In Use (Academic)"
    "English Vocabulary In Use (Pre-Intermediate)"
    "IELTS"
    "Longman Communication 3000"
    "TOEIC VOCABULARY"
    "Vocabulary"
    "📕⭐ENGLISH-GRAMMAR"
)

echo "Chọn deck để xử lý:"
echo ""
for i in "${!DECKS[@]}"; do
    echo "  $((i+1)). ${DECKS[$i]}"
done
echo "  0. Quay lại"
echo ""

read -p "Nhập số (0-${#DECKS[@]}): " choice

if [ "$choice" -eq 0 ]; then
    echo "❌ Hủy"
    exit 0
fi

if [[ ! "$choice" =~ ^[0-9]+$ ]] || [ "$choice" -lt 1 ] || [ "$choice" -gt ${#DECKS[@]} ]; then
    echo "❌ Lựa chọn không hợp lệ"
    exit 1
fi

SELECTED_DECK="${DECKS[$((choice-1))]}"
echo ""
echo "✅ Đã chọn: $SELECTED_DECK"
echo ""

# Hỏi chế độ
echo "Chọn chế độ:"
echo "  1. Watch Mode (tự động chạy liên tục)"
echo "  2. Chạy một lần"
echo ""
read -p "Nhập số (1-2): " mode_choice

if [ "$mode_choice" -eq 1 ]; then
    echo "🔄 Bắt đầu Watch Mode (kiểm tra mỗi 60 giây)..."
    echo "Nhấn Ctrl+C để dừng"
    echo ""
    /usr/local/bin/python3 /Users/nguyenkhanh/Desktop/anki_image.py --watch --interval 60 --deck "$SELECTED_DECK"
elif [ "$mode_choice" -eq 2 ]; then
    echo "▶️  Bắt đầu (chạy một lần)..."
    echo ""
    /usr/local/bin/python3 /Users/nguyenkhanh/Desktop/anki_image.py --deck "$SELECTED_DECK"
else
    echo "❌ Lựa chọn không hợp lệ"
    exit 1
fi

echo ""
echo "👋 Hoàn thành"
