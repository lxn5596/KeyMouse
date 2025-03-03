from PySide6.QtWidgets import QWidget, QVBoxLayout, QMenu, QSystemTrayIcon, QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon
from gui.keyboard_view import KeyboardView
from gui.mouse_view import MouseView
from pathlib import Path
import json

class MainView(QWidget):
    """主视图组件，集成键盘和鼠标显示"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置无边框窗口
        self.setWindowFlags(
            Qt.FramelessWindowHint |  # 无边框
            Qt.WindowStaysOnTopHint | # 置顶
            Qt.Tool  # 不在任务栏显示
        )
        # 设置背景透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.is_locked = True  # 默认锁定状态
        self.is_positioning = False  # 添加定位模式标志
        
        self.tray_icon = None  # 添加托盘图标引用
        
        self.init_ui()
        self.load_position()  # 加载保存的位置
        
        # 确保在所有初始化完成后创建托盘图标
        QTimer.singleShot(0, self.create_tray_icon)
        
        # 添加右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)  # 设置键盘和鼠标显示之间的间距
        self.setLayout(layout)
        
        # 创建键盘和鼠标显示组件
        self.kb_view = KeyboardView()
        self.mouse_view = MouseView()
        
        # 禁用子组件的窗口特性
        for widget in [self.kb_view, self.mouse_view]:
            widget.setWindowFlags(Qt.Widget)
            widget.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
        # 添加到布局
        layout.addWidget(self.kb_view)
        layout.addWidget(self.mouse_view)
    
    def create_tray_icon(self):
        """创建系统托盘图标"""
        # 创建托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        
        # 设置图标
        icon_path = str(Path(__file__).parent.parent / 'assets' / 'icon.ico')
        self.tray_icon.setIcon(QIcon(icon_path))
        
        # 创建托盘菜单
        tray_menu = QMenu()
        
        # 只添加退出选项
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.force_quit)  # 使用新的退出方法
        tray_menu.addAction(exit_action)
        
        # 设置菜单并显示
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # 双击托盘图标时显示/隐藏窗口
        self.tray_icon.activated.connect(self._on_tray_activated)

    def _on_tray_activated(self, reason):
        """处理托盘图标激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.raise_()
                self.activateWindow()
    
    def toggle_position_mode(self):
        """切换位置调整模式"""
        if self.is_positioning:
            # 锁定位置
            self.is_positioning = False
            self.is_locked = True
            self.restore_window_style()
            self.save_position()
        else:
            # 开始调整位置
            self.is_positioning = True
            self.is_locked = False
            self.show()
            self.raise_()
            self.activateWindow()
            self.highlight_window()
    
    def highlight_window(self):
        """高亮窗口"""
        self.setStyleSheet("""
            QWidget {
                border: 2px solid #4CAF50;
                border-radius: 5px;
                background-color: rgba(76, 175, 80, 0.2);
            }
        """)
    
    def restore_window_style(self):
        """恢复窗口样式"""
        self.setStyleSheet("")
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton and not self.is_locked:
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if hasattr(self, '_drag_pos') and not self.is_locked:
            new_pos = event.globalPosition().toPoint()
            self.move(self.pos() + new_pos - self._drag_pos)
            self._drag_pos = new_pos
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if hasattr(self, '_drag_pos'):
            del self._drag_pos
            self.save_position()
            event.accept()
    
    def save_position(self):
        """保存窗口位置"""
        config = {
            'position': {
                'x': self.x(),
                'y': self.y()
            },
            'is_locked': self.is_locked
        }
        
        config_dir = Path.home() / '.keymouse'
        config_dir.mkdir(exist_ok=True)
        
        with open(config_dir / 'window.json', 'w') as f:
            json.dump(config, f)
    
    def load_position(self):
        """加载保存的窗口位置"""
        config_file = Path.home() / '.keymouse' / 'window.json'
        
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = json.load(f)
                
                self.move(config['position']['x'], config['position']['y'])
                self.is_locked = config.get('is_locked', True)
            except:
                self.reset_position()
        else:
            self.reset_position()
    
    def reset_position(self):
        """重置窗口位置到屏幕中央"""
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
        self.save_position()
    
    def show_context_menu(self, pos):
        """显示右键菜单"""
        menu = QMenu(self)
        
        # 根据当前状态设置动作文本
        position_action = QAction("锁定位置" if not self.is_locked else "修改位置", self)
        position_action.triggered.connect(self.toggle_position_mode)
        menu.addAction(position_action)
        
        # 重置位置动作
        reset_action = QAction("重置位置", self)
        reset_action.triggered.connect(self.reset_position)
        menu.addAction(reset_action)
        
        menu.addSeparator()
        
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.force_quit)  # 使用 force_quit 而不是 close
        menu.addAction(quit_action)
        
        menu.exec(self.mapToGlobal(pos))

    def closeEvent(self, event):
        """处理窗口关闭事件"""
        # 停止监控
        self.kb_view.monitor.stop()
        self.mouse_view.monitor.stop()
        
        # 移除托盘图标
        if self.tray_icon is not None:
            self.tray_icon.hide()
            self.tray_icon.deleteLater()
        
        # 接受关闭事件
        event.accept()
        
        # 完全退出程序
        QApplication.quit()

    def force_quit(self):
        """强制退出程序"""
        self.close()  # 这会触发 closeEvent 