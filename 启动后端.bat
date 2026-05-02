@echo off
cd /d "%~dp0backend"
echo 正在启动后端服务，请勿关闭此窗口...
"D:\Python Lesson\Python\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
pause
