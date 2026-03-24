@echo off
REM 启动API服务器（Windows批处理脚本）
echo Starting De Anza College API Server...
cd /d %~dp0
python run_api_server.py
pause


