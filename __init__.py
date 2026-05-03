# Import các thư viện cần thiết từ Anki
from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *

# 1. Tạo một hàm xử lý sự kiện (khi bấm nút thì làm gì)
def my_custom_function():
    # Hiện một hộp thoại thông báo
    showInfo("Xin chào! Đây là Add-on đầu tiên của tôi!")

# 2. Tạo một hành động (Action) trên thanh Menu
action = QAction("Chạy Add-on Của Tôi", mw)

# 3. Kết nối hành động đó với hàm xử lý ở trên
action.triggered.connect(my_custom_function)

# 4. Thêm nút bấm này vào menu "Tools" (Công cụ) của Anki
mw.form.menuTools.addAction(action)