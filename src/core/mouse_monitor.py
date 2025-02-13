from pynput import mouse
from typing import Set, Dict
from PySide6.QtCore import QObject, Signal
from time import time

class MouseMonitor(QObject):
    """鼠标监控模块"""
    
    # 定义信号
    click_pressed = Signal(str)  # 点击按下信号
    click_released = Signal(str)  # 点击释放信号
    wheel_moved = Signal(str)    # 滚轮移动信号
    mouse_moved = Signal(tuple)  # 鼠标移动信号(x, y)
    
    def __init__(self):
        super().__init__()
        self.listener = None
        self.is_running = True
        self._click_times: Dict[str, int] = {}  # 记录连续点击次数
        self._last_click_time: Dict[str, float] = {}  # 记录最后点击时间
        self._double_click_threshold = 0.5  # 双击判定时间（秒）
        self._start_listener()
        
    def _start_listener(self):
        """启动鼠标监听"""
        self.listener = mouse.Listener(
            on_click=self._on_click,
            on_scroll=self._on_scroll
        )
        self.listener.start()
    
    def _format_button(self, button) -> str:
        """格式化按钮名称"""
        if button == mouse.Button.left:
            return "左键"
        elif button == mouse.Button.right:
            return "右键"
        elif button == mouse.Button.middle:
            return "中键"
        return str(button)
    
    def _on_click(self, x, y, button, pressed):
        """点击回调"""
        btn_str = self._format_button(button)
        current_time = time()
        
        if pressed:
            # 处理连续点击
            if btn_str in self._last_click_time:
                if current_time - self._last_click_time[btn_str] < self._double_click_threshold:
                    self._click_times[btn_str] += 1
                else:
                    self._click_times[btn_str] = 1
            else:
                self._click_times[btn_str] = 1
            
            self._last_click_time[btn_str] = current_time
            
            # 发送点击信号
            if self._click_times[btn_str] > 1:
                self.click_pressed.emit(f"{self._click_times[btn_str]}击{btn_str}")
            else:
                self.click_pressed.emit(btn_str)
        else:
            self.click_released.emit(btn_str)
    
    def _on_scroll(self, x, y, dx, dy):
        """滚轮回调"""
        if dy > 0:
            self.wheel_moved.emit("滚轮上")
        elif dy < 0:
            self.wheel_moved.emit("滚轮下")
        elif dx > 0:
            self.wheel_moved.emit("滚轮右")
        elif dx < 0:
            self.wheel_moved.emit("滚轮左")
    
    def _on_move(self, x, y):
        """移动回调"""
        self.mouse_moved.emit((x, y))
    
    def stop(self):
        """停止监听"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # 停止监听器
        if self.listener:
            try:
                self.listener.stop()
                self.listener.join(timeout=0.1)
            except:
                pass
            finally:
                self.listener = None
        
        # 清理状态
        self._click_times.clear()
        self._last_click_time.clear()

    def __del__(self):
        """析构函数"""
        try:
            self.stop()
        except:
            pass 