from pynput import keyboard
from typing import Callable, Set, Dict
from PySide6.QtCore import QObject, Signal, QTimer
from time import time
from collections import deque
from threading import Lock

class KeyboardMonitor(QObject):
    """键盘监控模块"""
    
    # 定义信号
    key_pressed = Signal(str, bool)  # 按键按下信号(key_str, is_long_press)
    key_released = Signal(str)  # 按键释放信号
    combination_pressed = Signal(list)  # 组合键按下信号
    
    # 长按判定时间（秒）
    LONG_PRESS_THRESHOLD = 0.5
    
    def __init__(self):
        super().__init__()
        self.listener = None
        self.is_running = True
        self._pressed_keys: Set[str] = set()  # 当前按下的键
        self._key_press_times: Dict[str, float] = {}  # 按键按下的时间
        self._key_map: Dict[str, str] = self._init_key_map()
        self._long_press_keys: Set[str] = set()  # 已经触发长按的键
        
        # 添加事件队列和锁
        self._event_queue = deque()
        self._lock = Lock()
        
        # 创建处理定时器
        self._process_timer = QTimer(self)
        self._process_timer.timeout.connect(self._process_events)
        self._process_timer.start(10)  # 每10ms处理一次事件队列
        
        self._start_listener()
    
    def _init_key_map(self) -> Dict[str, str]:
        """初始化按键映射"""
        return {
            # 基本按键
            'space': '空格',
            'enter': '回车',
            'backspace': '退格',
            'tab': 'Tab',
            'caps_lock': 'Caps Lock',
            'esc': 'ESC',
            
            # 修饰键
            'shift': 'Shift',
            'shift_r': 'Shift',  # 右Shift
            'shift_l': 'Shift',  # 左Shift
            'ctrl': 'Ctrl',
            'ctrl_r': 'Ctrl',    # 右Ctrl
            'ctrl_l': 'Ctrl',    # 左Ctrl
            'alt': 'Alt',
            'alt_r': 'Alt',      # 右Alt
            'alt_l': 'Alt',      # 左Alt
            'cmd': 'Win',
            
            # 方向键
            'up': '↑',
            'down': '↓',
            'left': '←',
            'right': '→',
            
            # 功能键
            'f1': 'F1',
            'f2': 'F2',
            'f3': 'F3',
            'f4': 'F4',
            'f5': 'F5',
            'f6': 'F6',
            'f7': 'F7',
            'f8': 'F8',
            'f9': 'F9',
            'f10': 'F10',
            'f11': 'F11',
            'f12': 'F12',
            
            # 数字键盘
            'num_lock': 'Num Lock',
            'num_0': 'Num 0',
            'num_1': 'Num 1',
            'num_2': 'Num 2',
            'num_3': 'Num 3',
            'num_4': 'Num 4',
            'num_5': 'Num 5',
            'num_6': 'Num 6',
            'num_7': 'Num 7',
            'num_8': 'Num 8',
            'num_9': 'Num 9',
            'num_decimal': 'Num .',
            'num_divide': 'Num /',
            'num_multiply': 'Num *',
            'num_subtract': 'Num -',
            'num_add': 'Num +',
            'num_enter': 'Num Enter',
            
            # 其他常用键
            'insert': 'Insert',
            'delete': 'Delete',
            'home': 'Home',
            'end': 'End',
            'page_up': 'Page Up',
            'page_down': 'Page Down',
            'menu': 'Menu',
            'pause': 'Pause',
            'print_screen': 'PrtSc',
            'scroll_lock': 'Scroll Lock'
        }
    
    def _format_key(self, key) -> str:
        """格式化按键名称"""
        try:
            # 特殊键
            if hasattr(key, 'vk') and 96 <= key.vk <= 105:  # 数字键盘的虚拟键码范围
                num = key.vk - 96  # 转换为对应的数字
                return f'Num {num}'
            
            if hasattr(key, 'vk'):  # 处理数字键盘的其他按键
                vk_map = {
                    106: 'Num *',   # 乘号
                    107: 'Num +',   # 加号
                    108: 'Num Enter',  # 回车
                    109: 'Num -',   # 减号
                    110: 'Num .',   # 小数点
                    111: 'Num /',   # 除号
                }
                if key.vk in vk_map:
                    return vk_map[key.vk]
            
            # 处理控制键组合
            if hasattr(key, 'char') and key.char:
                if key.char < ' ':  # 控制字符
                    # 获取对应的字母
                    ctrl_char = chr(ord(key.char) + ord('A') - 1)
                    return ctrl_char
                return key.char.upper()
            
            # 其他特殊键
            key_str = str(key).replace('Key.', '').lower()
            
            # 处理左右修饰键
            if key_str.startswith(('shift_', 'ctrl_', 'alt_')):
                key_str = key_str.split('_')[0]
            
            return self._key_map.get(key_str, key_str.upper())
            
        except AttributeError:
            return str(key)
    
    def _process_events(self):
        """处理事件队列"""
        with self._lock:
            while self._event_queue:
                event_type, key = self._event_queue.popleft()
                if event_type == 'press':
                    self._handle_press(key)
                else:  # release
                    self._handle_release(key)
    
    def _on_press(self, key):
        """按键按下回调（在监听线程中）"""
        with self._lock:
            self._event_queue.append(('press', key))
    
    def _on_release(self, key):
        """按键释放回调（在监听线程中）"""
        with self._lock:
            self._event_queue.append(('release', key))
    
    def _handle_press(self, key):
        """处理按键按下（在主线程中）"""
        key_str = self._format_key(key)
        if not key_str or key_str == 'F22':  # 过滤掉F22和无效按键
            return
            
        current_time = time()
        should_update_combo = False
        
        # 如果是新按下的键
        if key_str not in self._pressed_keys:
            self._pressed_keys.add(key_str)
            self._key_press_times[key_str] = current_time
            # 只有在不是组合键的情况下才发送单键信号
            if len(self._pressed_keys) == 1:
                self.key_pressed.emit(key_str, False)
            should_update_combo = True
            
        # 检查是否是长按
        elif (key_str not in self._long_press_keys and 
              current_time - self._key_press_times[key_str] > self.LONG_PRESS_THRESHOLD):
            self._long_press_keys.add(key_str)
            # 只有在不是组合键的情况下才发送长按信号
            if len(self._pressed_keys) == 1:
                self.key_pressed.emit(key_str, True)
            should_update_combo = True
        
        # 只在有多个按键时发送组合键信号
        if should_update_combo and len(self._pressed_keys) > 1:
            keys = []
            modifiers = {'Ctrl', 'Alt', 'Shift', 'Win'}
            
            # 先添加修饰键
            for k in sorted(self._pressed_keys):
                if k in modifiers:
                    if k in self._long_press_keys:
                        keys.append(f"长按{k}")
                    else:
                        keys.append(k)
            
            # 再添加其他键
            for k in sorted(self._pressed_keys):
                if k not in modifiers:
                    if k in self._long_press_keys:
                        keys.append(f"长按{k}")
                    else:
                        keys.append(k)
            
            self.combination_pressed.emit(keys)
    
    def _handle_release(self, key):
        """处理按键释放（在主线程中）"""
        key_str = self._format_key(key)
        if not key_str:
            return
            
        # 清理按键状态
        self._pressed_keys.discard(key_str)
        self._key_press_times.pop(key_str, None)
        self._long_press_keys.discard(key_str)
        
        # 发送释放信号
        self.key_released.emit(key_str)
    
    def _start_listener(self):
        """启动键盘监听"""
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
    
    def stop(self):
        """停止监听"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # 先停止处理定时器
        if hasattr(self, '_process_timer'):
            self._process_timer.stop()
            self._process_timer.deleteLater()
        
        # 清空事件队列
        with self._lock:
            self._event_queue.clear()
        
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
        self._pressed_keys.clear()
        self._key_press_times.clear()
        self._long_press_keys.clear()
    
    def __del__(self):
        """析构函数"""
        try:
            self.stop()
        except:
            pass
    
    def get_pressed_keys(self) -> Set[str]:
        """获取当前按下的键"""
        return self._pressed_keys.copy() 