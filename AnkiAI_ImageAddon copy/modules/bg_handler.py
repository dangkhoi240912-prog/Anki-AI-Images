"""
Background Handler Module - Xử lý background để tránh UI freeze
Giai đoạn 4: Chạy xử lý ngầm với thanh tiến trình
"""

from aqt.operations import QueryOp
from aqt import mw
from typing import List, Callable, Optional, Tuple
import time


class BackgroundProcessor:
    """
    Xử lý các thao tác dài hạn ở background
    Sử dụng aqt.operations.QueryOp của Anki để chạy ngầm mà không freeze UI
    """
    
    def __init__(self):
        """Khởi tạo BackgroundProcessor"""
        self.is_running = False
        self.cancelled = False
    
    def process_cards_in_background(
        self,
        note_ids: List[int],
        process_func: Callable,
        on_progress: Optional[Callable] = None,
        on_success: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        title: str = "Processing..."
    ) -> None:
        """
        Xử lý một danh sách note_ids ở background với thanh tiến trình
        
        Args:
            note_ids: Danh sách Note IDs cần xử lý
            process_func: Function để xử lý từng note. Signature: process_func(note_id, progress_callback)
            on_progress: Callback khi cập nhật tiến trình: on_progress(current, total, message)
            on_success: Callback khi xong: on_success(results)
            on_error: Callback khi lỗi: on_error(error_message)
            title: Tiêu đề cho thao tác
        """
        self.is_running = True
        self.cancelled = False
        results = []
        errors = []
        
        def background_work(col):
            """Công việc chính ở background"""
            try:
                total = len(note_ids)
                
                for index, note_id in enumerate(note_ids):
                    if self.cancelled:
                        break
                    
                    try:
                        # Lấy note từ database
                        note = col.get_note(note_id)
                        
                        # Xử lý note
                        result = process_func(note)
                        results.append(result)
                        
                        # Cập nhật tiến trình
                        if on_progress:
                            progress_msg = f"Đang xử lý thẻ {index + 1}/{total}"
                            on_progress(index + 1, total, progress_msg)
                    
                    except Exception as e:
                        error_msg = f"Lỗi xử lý note {note_id}: {str(e)}"
                        errors.append(error_msg)
                        print(f"[ERROR] {error_msg}")
                
                return {"results": results, "errors": errors}
            
            except Exception as e:
                error_msg = f"Lỗi background: {str(e)}"
                print(f"[ERROR] {error_msg}")
                raise
        
        def on_done(result):
            """Callback khi xưng xong - Anki 25.x+ passes result directly"""
            try:
                self.is_running = False
                if on_success:
                    on_success(result)
            
            except Exception as e:
                self.is_running = False
                error_msg = f"Exception during background processing: {str(e)}"
                print(f"[ERROR] {error_msg}")
                if on_error:
                    on_error(error_msg)
        
        # Chạy QueryOp (Anki 25.x+ API: keyword args)
        op = QueryOp(parent=mw, op=background_work, success=on_done)
        op.with_progress(title).run_in_background()
    
    def cancel(self):
        """Hủy xử lý hiện tại"""
        self.cancelled = True
    
    def is_processing(self) -> bool:
        """Kiểm tra xem có đang xử lý không"""
        return self.is_running


class ProgressDialog:
    """Dialog hiển thị tiến trình xử lý"""
    
    def __init__(self, title: str = "Đang xử lý...", parent=None):
        """Khởi tạo progress dialog"""
        from aqt.qt import QDialog, QVBoxLayout, QProgressBar, QLabel, QPushButton
        
        self.dialog = QDialog(parent)
        self.dialog.setWindowTitle(title)
        self.dialog.setMinimumWidth(400)
        self.dialog.setModal(True)
        
        layout = QVBoxLayout()
        
        # Label hiển thị trạng thái
        self.status_label = QLabel("Khởi tạo...")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        layout.addWidget(self.progress_bar)
        
        # Nút hủy
        self.cancel_button = QPushButton("Hủy")
        self.cancel_button.clicked.connect(self.on_cancel)
        layout.addWidget(self.cancel_button)
        
        self.dialog.setLayout(layout)
        self.cancelled = False
    
    def update_progress(self, current: int, total: int, message: str = ""):
        """Cập nhật tiến trình"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.status_label.setText(f"{message}\n({current}/{total})")
    
    def on_cancel(self):
        """Người dùng nhấn hủy"""
        self.cancelled = True
        self.dialog.reject()
    
    def show(self):
        """Hiển thị dialog"""
        self.dialog.show()
    
    def close(self):
        """Đóng dialog"""
        self.dialog.close()
    
    def is_cancelled(self) -> bool:
        """Kiểm tra xem người dùng có nhấn hủy không"""
        return self.cancelled


class ProcessingTask:
    """Một công việc xử lý từng thẻ"""
    
    def __init__(self, name: str):
        """Khởi tạo ProcessingTask"""
        self.name = name
        self.results = []
        self.errors = []
    
    def process_note(self, note) -> Tuple[bool, str]:
        """
        Xử lý một note
        Override method này trong lớp con
        
        Args:
            note: Anki Note object
        
        Returns:
            Tuple (success, message)
        """
        raise NotImplementedError("Override process_note in subclass")
    
    def add_result(self, note_id: int, success: bool, message: str):
        """Lưu kết quả xử lý"""
        if success:
            self.results.append({"note_id": note_id, "message": message})
        else:
            self.errors.append({"note_id": note_id, "error": message})
    
    def get_summary(self) -> dict:
        """Lấy tóm tắt kết quả"""
        return {
            "task_name": self.name,
            "total_processed": len(self.results) + len(self.errors),
            "successful": len(self.results),
            "failed": len(self.errors),
            "results": self.results,
            "errors": self.errors
        }
