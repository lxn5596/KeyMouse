from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel

class SettingsDialog(QDialog):
    """设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("设置")
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 临时标签，后续会添加实际的设置选项
        layout.addWidget(QLabel("设置选项将在这里显示")) 