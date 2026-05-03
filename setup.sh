#!/bin/bash
# Setup script - cấu hình ban đầu

echo "🎨 Anki Image Auto-Add System - Setup"
echo "======================================"
echo ""

# Make scripts executable
chmod +x /Users/nguyenkhanh/Desktop/run_once.sh
chmod +x /Users/nguyenkhanh/Desktop/run_watch.sh

echo "✅ Made scripts executable"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi
echo "✅ Python 3 found: $(python3 --version)"

# Check requests
python3 -c "import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ requests module not found"
    echo "Installing: pip install requests"
    pip3 install requests
fi
echo "✅ requests module found"

echo ""
echo "======================================"
echo "📋 SETUP CHECKLIST"
echo "======================================"
echo "✅ Python 3 installed"
echo "✅ requests module installed"
echo "✅ Scripts are executable"
echo ""
echo "📌 NEXT STEPS:"
echo ""
echo "1. Make sure Anki is running with AnkiConnect:"
echo "   https://github.com/FooSoft/anki-connect"
echo ""
echo "2. Configure API keys in anki_image.py:"
echo "   - PIXABAY_API_KEY"
echo "   - UNSPLASH_API_KEY"
echo "   - PEXELS_API_KEY"
echo ""
echo "3. Update Anki settings in anki_image.py:"
echo "   - DECK_NAME"
echo "   - ANKI_FIELD_VOCAB"
echo "   - ANKI_FIELD_EXAMPLE"
echo "   - ANKI_FIELD_IMAGE"
echo ""
echo "4. Run once to test:"
echo "   bash /Users/nguyenkhanh/Desktop/run_once.sh"
echo ""
echo "5. Or run in watch mode (auto-update):"
echo "   bash /Users/nguyenkhanh/Desktop/run_watch.sh"
echo ""
echo "📖 More info: cat /Users/nguyenkhanh/Desktop/README_ANKI_IMAGE.md"
echo ""
