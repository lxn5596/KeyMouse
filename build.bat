@echo off
chcp 65001
echo 正在准备构建...

REM 清理旧的构建文件
echo 清理旧文件...
rmdir /s /q build dist
del /f /q *.spec

REM 使用 PyInstaller 打包
echo 开始打包程序...
pyinstaller --noconfirm ^
    --windowed ^
    --icon=src/assets/icon.ico ^
    --name keymouse ^
    --add-data "src/assets/icon.ico;assets" ^
    src/main.py

REM 复制语言文件
echo 复制语言文件...
copy "ChineseSimplified.isl" "."

REM 编译安装程序
echo 开始构建安装程序...
"D:\Program\Inno Setup 6\ISCC.exe" setup.iss

if %ERRORLEVEL% EQU 0 (
    echo 安装程序编译成功！输出文件: dist\KeyMouse-Setup.exe
) else (
    echo 编译失败，请检查错误信息。
)

echo 构建完成！
pause 