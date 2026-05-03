#!/usr/bin/env python3
"""
Build script for AnkiAI add-on
Packages add-on thành file .ankiaddon để upload lên AnkiWeb
"""

import os
import sys
import shutil
import zipfile
import json
from pathlib import Path


def get_addon_root():
    """Lấy đường dẫn root của add-on"""
    return Path(__file__).parent / "AnkiAI_ImageAddon"


def get_manifest():
    """Lấy manifest.json"""
    manifest_path = get_addon_root() / "manifest.json"
    with open(manifest_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_addon(output_dir=None):
    """
    Build add-on thành .ankiaddon
    
    Args:
        output_dir: Thư mục output (default: current directory)
    """
    
    addon_root = get_addon_root()
    manifest = get_manifest()
    
    if not output_dir:
        output_dir = Path.cwd()
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(exist_ok=True)
    
    # Tên output file
    version = manifest.get("version", "1.0.0")
    output_file = output_dir / f"AnkiAI_ImageAddon-{version}.ankiaddon"
    
    print(f"📦 Building AnkiAI add-on v{version}...")
    print(f"📁 Source: {addon_root}")
    print(f"📤 Output: {output_file}")
    
    # Tạo zip file
    try:
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add tất cả files từ addon_root
            for root, dirs, files in os.walk(addon_root):
                for file in files:
                    # Skip __pycache__ và .pyc files
                    if '__pycache__' in root or file.endswith('.pyc'):
                        continue
                    
                    file_path = Path(root) / file
                    # Anki add-ons: archive path không include folder name
                    arcname = file_path.relative_to(addon_root)
                    
                    print(f"  ✓ Added: {arcname}")
                    zipf.write(file_path, arcname)
        
        print(f"\n✅ Build thành công!")
        print(f"📦 Output file: {output_file}")
        print(f"📊 File size: {output_file.stat().st_size / 1024:.1f} KB")
        print(f"\n📤 Để upload lên AnkiWeb:")
        print(f"   1. Vào https://ankiweb.net/")
        print(f"   2. Add-ons > Upload")
        print(f"   3. Chọn file: {output_file.name}")
        
        return output_file
    
    except Exception as e:
        print(f"\n❌ Build thất bại:")
        print(f"   Error: {e}")
        sys.exit(1)


def install_locally():
    """Cài đặt add-on ở local để test"""
    addon_root = get_addon_root()
    
    # Xác định đường dẫn addons folder
    if sys.platform == "darwin":  # macOS
        addons_path = Path.home() / "Library/Application Support/Anki2/addons21"
    elif sys.platform == "win32":  # Windows
        addons_path = Path.home() / "AppData/Roaming/Anki2/addons21"
    else:  # Linux
        addons_path = Path.home() / ".local/share/Anki2/addons21"
    
    target_path = addons_path / addon_root.name
    
    print(f"🔗 Installing locally for testing...")
    print(f"   From: {addon_root}")
    print(f"   To:   {target_path}")
    
    try:
        # Nếu đã có, backup cái cũ
        if target_path.exists():
            backup_path = target_path.parent / f"{addon_root.name}.backup"
            if backup_path.exists():
                shutil.rmtree(backup_path)
            shutil.move(str(target_path), str(backup_path))
            print(f"   📦 Backed up old version to {backup_path.name}")
        
        # Copy add-on
        shutil.copytree(addon_root, target_path)
        print(f"\n✅ Installed successfully!")
        print(f"🎯 Now open Anki to test")
        
    except Exception as e:
        print(f"\n❌ Installation failed:")
        print(f"   Error: {e}")
        sys.exit(1)


def clean():
    """Xóa __pycache__ và .pyc files"""
    addon_root = get_addon_root()
    
    print("🧹 Cleaning up...")
    
    for root, dirs, files in os.walk(addon_root):
        # Xóa __pycache__
        pycache_dir = Path(root) / '__pycache__'
        if pycache_dir.exists():
            shutil.rmtree(pycache_dir)
            print(f"   ✓ Removed: {pycache_dir}")
        
        # Xóa .pyc
        for file in files:
            if file.endswith('.pyc'):
                file_path = Path(root) / file
                file_path.unlink()
                print(f"   ✓ Removed: {file_path}")
    
    print("✅ Cleanup completed!")


def main():
    """Main entry point"""
    
    if len(sys.argv) < 2:
        print("""
AnkiAI Build Script
====================

Usage:
  python build.py build [output_dir]    - Build .ankiaddon file
  python build.py install               - Install locally for testing
  python build.py clean                 - Clean cache files

Examples:
  python build.py build                 # Create in current directory
  python build.py build ~/Desktop       # Create in Desktop
  python build.py install               # Install to Anki addons folder
  python build.py clean                 # Remove __pycache__
        """)
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "build":
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None
        build_addon(output_dir)
    
    elif command == "install":
        install_locally()
    
    elif command == "clean":
        clean()
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
