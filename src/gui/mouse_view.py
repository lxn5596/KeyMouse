from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, Slot, QTimer
from core.mouse_monitor import MouseMonitor
from typing import Dict
from time import time

class MouseLabel(QLabel):
    """鼠标操作显示标签"""
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.init_ui()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fade_out)
        self.is_valid = True
        
    def init_ui(self):
        """初始化UI"""
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: #2196F3;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 16px;
                margin: 2px;
            }
        """)
        
    def show_for_duration(self, duration: int = 2000):
        """显示指定时长"""
        self.show()
        self.timer.start(duration)
        
    def fade_out(self):
        """淡出并移除"""
        self.timer.stop()
        self.hide()
        self.is_valid = False
        self.deleteLater()

class MouseView(QWidget):
    """鼠标可视化组件"""
    
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
        
        self.monitor = MouseMonitor()
        self.mouse_labels = []
        self.display_duration = 2000
        self._shown_actions = {}
        self.max_labels = 3  # 设置最大标签数量
        self.is_locked = True
        self.is_positioning = False
        
        self.init_ui()
        self.connect_signals()
        
        # 添加清理定时器
        self.cleanup_timer = QTimer(self)
        self.cleanup_timer.timeout.connect(self.cleanup_labels)
        self.cleanup_timer.start(1000)
    
    def cleanup_labels(self):
        """清理已经无效的标签"""
        try:
            self.mouse_labels = [label for label in self.mouse_labels if label.is_valid]
        except:
            self.mouse_labels = []
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)  # 设置边距
        self.setLayout(layout)
        
        # 鼠标动作显示区域 - 改用水平布局
        self.actions_layout = QHBoxLayout()  # 改为 QHBoxLayout
        self.actions_layout.setAlignment(Qt.AlignCenter)  # 居中对齐
        self.actions_layout.setSpacing(5)  # 设置间距
        layout.addLayout(self.actions_layout)
        
    def connect_signals(self):
        """连接信号"""
        self.monitor.click_pressed.connect(self.on_mouse_action)
        self.monitor.wheel_moved.connect(self.on_mouse_action)
        
    @Slot(str)
    def on_mouse_action(self, action: str):
        """处理鼠标动作"""
        current_time = time()
        
        # 检查是否可以再次显示这个动作
        if action in self._shown_actions:
            if current_time - self._shown_actions[action] < 0.01:
                return
        
        # 如果已经达到最大显示数量，移除最旧的标签
        while len(self.mouse_labels) >= self.max_labels:
            oldest_label = self.mouse_labels.pop(0)
            if oldest_label.is_valid:
                oldest_label.fade_out()
        
        # 创建新标签
        label = MouseLabel(action)
        self.actions_layout.addWidget(label)
        label.show_for_duration(self.display_duration)
        
        # 记录显示时间
        self._shown_actions[action] = current_time
        
        # 保存标签引用
        self.mouse_labels.append(label)

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton and self.is_positioning:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if hasattr(self, '_drag_pos') and self.is_positioning:
            new_pos = event.globalPosition().toPoint()
            self.move(self.pos() + new_pos - self._drag_pos)
            self._drag_pos = new_pos

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if hasattr(self, '_drag_pos'):
            del self._drag_pos 