@echo off
chcp 65001 >nul
setlocal EnableExtensions

if "%~1"=="" (
  echo.
  echo  把视频文件拖到本文件上，即可转换成壁纸背景。
  echo  支持 mp4 / mkv / mov / avi 等，输出 VP9 WebM。
  echo.
  pause
  exit /b
)

set "SRC=%~1"
set "OUT=%~dp0wallpaper\custom"
if not exist "%OUT%" mkdir "%OUT%"

set "FF="
where ffmpeg >nul 2>nul && set "FF=ffmpeg"
if not defined FF (
  for /d %%D in ("%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg*") do (
    for /f "delims=" %%F in ('dir /s /b "%%D\ffmpeg.exe" 2^>nul') do set "FF=%%F"
  )
)

if not defined FF (
  echo.
  echo  没有找到 ffmpeg。
  echo.
  where winget >nul 2>nul
  if errorlevel 1 (
    echo  请手动安装 ffmpeg 后重试：
    echo  https://www.gyan.dev/ffmpeg/builds/
    pause
    exit /b 1
  )
  choice /c YN /m "是否现在用 winget 自动安装 ffmpeg"
  if errorlevel 2 (
    echo  已取消。
    pause
    exit /b 1
  )
  winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements
  for /d %%D in ("%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg*") do (
    for /f "delims=" %%F in ('dir /s /b "%%D\ffmpeg.exe" 2^>nul') do set "FF=%%F"
  )
)

if not defined FF (
  echo  安装后仍找不到 ffmpeg，请重开本窗口再试。
  pause
  exit /b 1
)

echo.
echo  输入：%SRC%
echo  输出：%OUT%\bg.webm
echo  正在转换，视频越长越慢...
echo.

"%FF%" -y -i "%SRC%" -c:v libvpx-vp9 -b:v 3M -an -vf "scale=1920:-2" "%OUT%\bg.webm"
if errorlevel 1 (
  echo.
  echo  转换失败。请确认视频能正常播放，或换一个文件。
  pause
  exit /b 1
)

"%FF%" -y -i "%SRC%" -frames:v 1 -q:v 2 "%OUT%\bg.jpg" >nul 2>nul

rem 同步到已安装的壁纸工程
set "WE="
if exist "%LOCALAPPDATA%\MikuWallpaper\installer.ini" (
  for /f "tokens=2 delims==" %%A in ('findstr /b "we=" "%LOCALAPPDATA%\MikuWallpaper\installer.ini" 2^>nul') do set "WE=%%A"
)
if defined WE (
  set "DEST=%WE%\projects\myprojects\Miku Study Room\custom"
  if exist "%WE%\projects\myprojects\Miku Study Room" (
    if not exist "%DEST%" mkdir "%DEST%"
    copy /y "%OUT%\bg.webm" "%DEST%\bg.webm" >nul
    if exist "%OUT%\bg.jpg" copy /y "%OUT%\bg.jpg" "%DEST%\bg.jpg" >nul
    echo  已同步到 Wallpaper Engine 工程。
  )
)

echo.
echo  转换完成。
echo  打开壁纸设置 - 背景 - 选择「自定义」即可。
echo.
pause
