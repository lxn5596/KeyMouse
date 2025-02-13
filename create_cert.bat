@echo off
"C:\Program Files\OpenSSL-Win64\bin\openssl.exe" req -x509 -newkey rsa:4096 -keyout keymouse.key -out keymouse.crt -days 365 -nodes -subj "/CN=KeyMouse Visualizer"
"C:\Program Files\OpenSSL-Win64\bin\openssl.exe" pkcs12 -export -out keymouse.pfx -inkey keymouse.key -in keymouse.crt -password pass:keymouse 