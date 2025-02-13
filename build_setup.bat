@echo off
chcp 65001
echo 正在准备构建...

REM 编译安装程序
"D:\Program\Inno Setup 6\ISCC.exe" setup.iss

if %ERRORLEVEL% EQU 0 (
    echo 安装程序编译成功！输出文件: dist\KeyMouse-Setup.exe
) else (
    echo 编译失败，请检查错误信息。
)

pause 