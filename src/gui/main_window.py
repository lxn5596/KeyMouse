from PySide6.QtWidgets import QMainWindow, QSystemTrayIcon, QMenu, QWidget, QVBoxLayout
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

from gui.keyboard_view import KeyboardView
from gui.mouse_view import MouseView
from gui.settings_dialog import SettingsDialog
from utils.config_manager import ConfigManager

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.init_ui()
        self.setup_tray_icon()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("KeyMouse Visualizer")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        # 创建中心部件
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # 创建键盘和鼠标可视化组件
        self.kb_view = KeyboardView(self)
        self.mouse_view = MouseView(self)
        
        # 添加到布局
        layout.addWidget(self.kb_view)
        layout.addWidget(self.mouse_view)
        
        # 设置中心部件
        self.setCentralWidget(central_widget)
        
    def setup_tray_icon(self):
        """设置系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_menu = QMenu()
        
        # 添加托盘菜单项
        self.tray_menu.addAction("显示/隐藏", self.toggle_window)
        self.tray_menu.addAction("设置", self.show_settings)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction("退出", self.close)
        
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()
        
    def toggle_window(self):
        """切换窗口显示状态"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            
    def show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self)
        dialog.exec() 