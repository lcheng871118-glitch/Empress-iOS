@echo off
chcp 65001 >nul
title 宝可梦竞技场2D · 局域网游戏服务器
cd /d "%~dp0game-web"

echo ============================================
echo   宝可梦竞技场2D · 局域网游戏服务器
echo ============================================
echo.

echo [1/3] 检查端口 3210 是否已被占用...
netstat -ano | findstr ":3210" | findstr "LISTENING" >nul
if %errorlevel%==0 (
  echo       服务已在运行，无需重复启动
  goto :done
)

echo [2/3] 启动游戏服务（最小化后台窗口）...
start "Empress-Pokemon2D-Server" /min cmd /c "node android-bootstrap.cjs"
echo       等待服务就绪...
timeout /t 3 /nobreak >nul

echo [3/3] 验证服务状态...
curl -s -m 5 http://127.0.0.1:3210/api/health >nul
if %errorlevel%==0 (
  echo       服务启动成功
) else (
  echo       警告：服务可能未就绪，请稍候或检查 node 是否安装
)

:done
echo.
echo ============================================
echo   iPhone 打开 Safari 访问：
echo       http://192.168.1.80:3210
echo.
echo   本机浏览器访问：
echo       http://127.0.0.1:3210
echo.
echo   存档位置：game-web\profile
echo   服务器窗口可最小化，不要关闭它
echo ============================================
echo.
pause
