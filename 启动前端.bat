@echo off
cd /d "%~dp0mobile"
echo 正在启动前端服务...
echo 启动完成后请在浏览器打开 http://localhost:8081
npx expo start --web --port 8081
pause
