#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
KeyMouse Visualizer 主程序入口
"""

import sys
import signal
from PySide6.QtWidgets import QApplication
from gui.main_view import MainView

def signal_handler(signum, frame):
    """处理系统信号"""
    QApplication.quit()

def main():
    """程序主入口"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("KeyMouse Visualizer")
    app.setApplicationVersion("1.0.0")
    
    # 创建主视图窗口
    window = MainView()
    window.resize(400, 200)  # 设置初始大小
    window.show()
    
    # 在程序退出前停止监听
    def cleanup():
        window.kb_view.monitor.stop()
        window.mouse_view.monitor.stop()
    
    app.aboutToQuit.connect(cleanup)
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
