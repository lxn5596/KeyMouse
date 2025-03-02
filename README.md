# KeyMouse 打包部署说明

## 一、环境准备
- **Python**: 3.8 或更高版本
- **Inno Setup 6**: 安装路径为 `D:\Program\Inno Setup 6`
- **Python 依赖包**：
  ```bash
  pip install pyinstaller
  pip install pyside6
  pip install pynput

  ```
  
二、项目结构
plaintext
```bash
KeyMouse/
├── src/
│   ├── assets/
│   │   └── icon.ico          # 程序图标
│   ├── core/
│   │   └── keyboard_monitor.py
│   ├── gui/
│   │   ├── keyboard_view.py
│   │   └── mouse_view.py
│   └── main.py
├── build.bat                 # 打包脚本
├── setup.iss                 # Inno Setup 配置
├── ChineseSimplified.isl    # 中文语言文件
└── requirements.txt          # 依赖列表

```
三、打包步骤
确认所有文件位置正确

运行 build.bat 脚本，自动执行以下流程：

🗑️ 清理旧构建文件

📦 PyInstaller 打包主程序

📂 复制资源文件到目标目录

🛠️ 调用 Inno Setup 生成安装程序

四、输出文件
打包完成后，在 dist 目录下生成：

📁 keymouse/：可直接运行的绿色版程序

⚙️ KeyMouse-Setup.exe：Windows 安装包

五、测试验证
程序功能测试
运行 dist/keymouse/keymouse.exe

验证功能：

键盘/鼠标操作实时显示

系统托盘图标交互

菜单功能响应

安装程序测试
执行 KeyMouse-Setup.exe

检查项：

✅ 安装路径选择

🔗 开始菜单快捷方式

⚡ 开机自启动选项

🗑️ 卸载残留检测

六、常见问题排查
问题类型	排查步骤
打包失败	1. 检查 Python 环境
2. 验证依赖完整性
3. 确认 Inno Setup 安装路径
程序运行异常	1. 检查 icon.ico 是否存在
2. 管理员权限运行测试
3. 系统兼容性验证
七、注意事项
⚠️ 打包前关闭所有关联进程

🧹 建议执行 pyinstaller --clean 清理缓存

🔍 重点检查以下路径：

bash

src/assets/
dist/keymouse/resources/
八、技术支持
访问官网获取帮助：https://yuansio.com


### 优化说明：
1. 使用更清晰的标题层级结构
2. 添加可视化图标增强可读性（⚠️可自行移除）
3. 表格化呈现常见问题
4. 代码块明确标注语言类型
5. 关键路径/命令使用行内代码标记

如需删除所有可视化图标，我可提供极简版本。
