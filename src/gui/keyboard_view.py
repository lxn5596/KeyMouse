from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, 
                             QMenu, QSystemTrayIcon, QApplication)
from PySide6.QtCore import Qt, Slot, QTimer, QPoint
from PySide6.QtGui import QFont, QAction, QIcon, QPixmap, QPainter, QColor
from core.keyboard_monitor import KeyboardMonitor
from typing import Dict
import json
from pathlib import Path
from time import time

class KeyLabel(QLabel):
    """按键显示标签"""
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.init_ui()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fade_out)
        self.is_valid = True  # 添加标志来标记标签是否有效
        
    def init_ui(self):
        """初始化UI"""
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: #4CAF50;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 16px;
                margin: 2px;
            }
        """)
        
    def show_for_duration(self, duration: int = 2000):
        """显示指定时长（毫秒）"""
        self.show()
        self.timer.start(duration)
        
    def fade_out(self):
        """淡出并移除"""
        self.timer.stop()
        self.hide()
        self.is_valid = False  # 标记为无效
        self.deleteLater()

class KeyboardView(QWidget):
    """键盘可视化组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置无边框窗口
        self.setWindowFlags(Qt.Widget)  # 改为普通部件
        
        self.monitor = KeyboardMonitor()
        self.key_labels = []  # 存储标签
        self.display_duration = 2000  # 默认显示2秒
        self._shown_keys = {}  # 仍然使用字典来跟踪显示时间
        self.is_locked = True  # 默认锁定状态
        self.is_positioning = False  # 添加定位模式标志
        self.cleanup_timer = QTimer(self)  # 添加清理定时器
        self.cleanup_timer.timeout.connect(self.cleanup_labels)
        self.cleanup_timer.start(1000)  # 每秒清理一次
        
        self.init_ui()
        self.connect_signals()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)  # 设置边距
        self.setLayout(layout)
        
        # 按键显示区域
        self.keys_layout = QHBoxLayout()
        self.keys_layout.setAlignment(Qt.AlignCenter)
        layout.addLayout(self.keys_layout)
        
        # 创建组合键容器
        combo_container = QWidget()
        combo_container.setLayout(QHBoxLayout())
        combo_container.layout().setContentsMargins(0, 0, 0, 0)
        combo_container.layout().setAlignment(Qt.AlignCenter)
        
        # 组合键显示
        self.combo_label = QLabel()
        self.combo_label.setAlignment(Qt.AlignCenter)
        self.combo_label.setStyleSheet("""
            QLabel {
                background-color: rgba(51, 51, 51, 200);
                color: white;
                padding: 3px 5px;  /* 减小水平内边距 */
                border-radius: 3px;
                font-size: 15px;   /* 增大字体 */
                margin-top: 3px;
                min-width: 10px;   /* 设置最小宽度 */
                max-width: 300px;  /* 设置最大宽度 */
            }
        """)
        self.combo_label.hide()
        combo_container.layout().addWidget(self.combo_label)
        layout.addWidget(combo_container)
        
        # 初始化组合键计时器
        self.combo_timer = QTimer(self)
        self.combo_timer.timeout.connect(self.hide_combo_label)
    
    def connect_signals(self):
        """连接信号"""
        self.monitor.key_pressed.connect(self.on_key_pressed)
        self.monitor.combination_pressed.connect(self.on_combination)
    
    @Slot(str, bool)
    def on_key_pressed(self, key: str, is_long_press: bool):
        """处理按键按下"""
        current_time = time()
        
        # 检查是否可以再次显示这个按键
        if key in self._shown_keys:
            last_show_time = self._shown_keys[key]
            if not is_long_press and current_time - last_show_time < 0.01:  # 减少到10ms的最小间隔
                return
        
        # 创建新的按键标签
        display_text = f"长按{key}" if is_long_press else key
        label = KeyLabel(display_text)
        self.keys_layout.addWidget(label)
        label.show_for_duration(self.display_duration)
        
        # 记录显示时间
        self._shown_keys[key] = current_time
        
        # 保存标签引用
        self.key_labels.append(label)
        
        # 限制最大显示数量
        if len(self.key_labels) > 15:  # 增加最大显示数量
            oldest_label = self.key_labels.pop(0)
            if oldest_label.is_valid:
                oldest_label.fade_out()
    
    def cleanup_labels(self):
        """清理已经无效的标签"""
        try:
            # 只保留有效的标签
            self.key_labels = [label for label in self.key_labels if label.is_valid]
        except:
            # 如果出现异常，清空列表重新开始
            self.key_labels = []
    
    @Slot(list)
    def on_combination(self, keys: list):
        """处理组合键"""
        if not keys:  # 如果没有组合键，隐藏标签
            self.hide_combo_label()
            return
            
        # 调整组合键标签大小
        text = " + ".join(keys)
        self.combo_label.setText(text)
        self.combo_label.setWordWrap(False)  # 禁止文字换行
        self.combo_label.adjustSize()  # 根据内容调整大小
        self.combo_label.show()
        
        # 重置计时器
        self.combo_timer.stop()
        self.combo_timer.start(self.display_duration)
    
    def hide_combo_label(self):
        """隐藏组合键标签"""
        self.combo_timer.stop()
        self.combo_label.hide()
    
    @Slot(str)
    def on_key_released(self, key: str):
        """处理按键释放"""
        pass  # 不再需要在释放时处理标签
    
    def set_display_duration(self, duration: int):
        """设置显示持续时间（毫秒）"""
        self.display_duration = duration