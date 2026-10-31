$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$localAppData = $env:LOCALAPPDATA; if (-not $localAppData) { $localAppData = [Environment]::GetFolderPath('LocalApplicationData') }; $logDir = Join-Path $localAppData 'MikuWallpaper'
New-Item -ItemType Directory -Force $logDir | Out-Null
$log = Join-Path $logDir 'install.log'
Start-Transcript -Path $log -Force | Out-Null

function Pause-Exit($code) {
    Write-Host ''
    Write-Host "日志：$log" -ForegroundColor DarkGray
    Read-Host '按回车退出'
    exit $code
}

function Resolve-WE($path) {
    if (-not $path) { return $null }
    $path = $path.Trim().Trim('"')
    if (Test-Path $path -PathType Leaf) { $path = Split-Path -Parent $path }
    if (Test-Path (Join-Path $path 'wallpaper32.exe')) { return $path }
    return $null
}

function Find-WallpaperEngine {
    $candidates = @()

    foreach ($key in @(
        'HKCU:\Software\Valve\Steam',
        'HKLM:\SOFTWARE\WOW6432Node\Valve\Steam',
        'HKLM:\SOFTWARE\Valve\Steam'
    )) {
        $steam = (Get-ItemProperty $key -ErrorAction SilentlyContinue)
        if ($steam) {
            if ($steam.SteamPath) { $candidates += $steam.SteamPath }
            if ($steam.InstallPath) { $candidates += $steam.InstallPath }
        }
    }

    $libs = @()
    foreach ($steamPath in $candidates) {
        $vdf = Join-Path $steamPath 'steamapps\libraryfolders.vdf'
        if (Test-Path $vdf) {
            $txt = Get-Content $vdf -Raw
            foreach ($m in [regex]::Matches($txt, '"path"\s+"([^"]+)"')) {
                $libs += ($m.Groups[1].Value -replace '\\\\', '\')
            }
        }
    }

    $paths = @()
    foreach ($base in ($candidates + $libs)) {
        if ($base) { $paths += (Join-Path $base 'steamapps\common\wallpaper_engine') }
    }
    $paths += @(
        'C:\Program Files (x86)\Steam\steamapps\common\wallpaper_engine',
        'C:\Program Files\Steam\steamapps\common\wallpaper_engine',
        'D:\Steam\steamapps\common\wallpaper_engine',
        'D:\SteamLibrary\steamapps\common\wallpaper_engine',
        'E:\Steam\steamapps\common\wallpaper_engine',
        'E:\SteamLibrary\steamapps\common\wallpaper_engine'
    )

    foreach ($p in $paths) {
        if ($p -and (Test-Path (Join-Path $p 'wallpaper32.exe'))) { return $p }
    }
    return $null
}

try {
    Write-Host '=== Miku Study Room 音乐壁纸 安装 ===' -ForegroundColor Cyan

    if (-not (Test-Path (Join-Path $root 'wallpaper\index.html'))) {
        Write-Host '压缩包不完整：找不到 wallpaper\index.html' -ForegroundColor Red
        Pause-Exit 1
    }
    if (-not (Test-Path (Join-Path $root 'bridge\bridge.exe'))) {
        Write-Host '压缩包不完整：找不到 bridge\bridge.exe' -ForegroundColor Red
        Pause-Exit 1
    }

    $we = $null
    $weFile = Join-Path $root 'we.txt'

    # 优先读 we.txt（用户手动指定）
    if (Test-Path $weFile) {
        $manual = (Get-Content $weFile -TotalCount 1)
        if ($manual) { $we = Resolve-WE $manual }
        if ($we) { Write-Host "使用 we.txt 指定的路径：$we" -ForegroundColor Cyan }
    }

    if (-not $we) { $we = Find-WallpaperEngine }

    if (-not $we) {
        Write-Host '没有自动找到 Wallpaper Engine。' -ForegroundColor Yellow
        Write-Host '请输入 wallpaper_engine 文件夹路径（里面要有 wallpaper32.exe），直接回车退出。'
        for ($t = 0; $t -lt 3; $t++) {
            $manual = Read-Host '路径'
            if (-not $manual) { break }
            $we = Resolve-WE $manual
            if ($we) { break }
            Write-Host '这个路径里没有 wallpaper32.exe，请重试。' -ForegroundColor Red
        }
    }

    if (-not $we) {
        Write-Host '没有找到 Wallpaper Engine，安装终止。' -ForegroundColor Red
        Write-Host '也可以手动把 wallpaper 文件夹拖进 WE 的“创建壁纸 → 网页”。'
        Pause-Exit 1
    }

    # 记住手动路径，下次不用再填
    try { Set-Content -Path $weFile -Value $we -Encoding ASCII } catch { }
    Write-Host "Wallpaper Engine: $we"

    # 权限检查：WE 在 Program Files 时需要管理员
    $projects = Join-Path $we 'projects\myprojects'
    try {
        New-Item -ItemType Directory -Force $projects | Out-Null
        $probe = Join-Path $projects '.write-test'
        [System.IO.File]::WriteAllText($probe, 'x')
        Remove-Item $probe -Force
    } catch {
        Write-Host '当前没有写入 Wallpaper Engine 目录的权限，正在申请管理员权限...' -ForegroundColor Yellow
        $ps = Join-Path $PSHOME 'powershell.exe'
        Start-Process -FilePath $ps -Verb RunAs -ArgumentList @(
            '-NoProfile','-ExecutionPolicy','Bypass','-File',"`"$($MyInvocation.MyCommand.Path)`""
        )
        Stop-Transcript | Out-Null
        exit 0
    }

    Write-Host '正在复制壁纸工程...'
    robocopy (Join-Path $root 'wallpaper') (Join-Path $we 'projects\myprojects\Miku Study Room') /E /NFL /NDL /NJH /NJS /NC /NS | Out-Null
    if ($LASTEXITCODE -ge 8) {
        Write-Host '复制壁纸工程失败。请关闭 Wallpaper Engine 后重试。' -ForegroundColor Red
        Pause-Exit 1
    }

    $data = Join-Path $localAppData 'MikuWallpaper'
    $bridgeDir = Join-Path $data 'bridge'
    New-Item -ItemType Directory -Force $bridgeDir | Out-Null
    Get-Process bridge, watchdog -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 600

    Get-ChildItem (Join-Path $root 'bridge') | Where-Object { $_.Name -ne 'ai.ini' } | ForEach-Object {
        Copy-Item $_.FullName (Join-Path $bridgeDir $_.Name) -Recurse -Force
    }
    $dstAi = Join-Path $bridgeDir 'ai.ini'
    if (-not (Test-Path $dstAi)) { Copy-Item (Join-Path $root 'bridge\ai.ini') $dstAi -Force }

    $bridgeExe = Join-Path $bridgeDir 'bridge.exe'
    $watchdogExe = Join-Path $bridgeDir 'watchdog.exe'
    Start-Process $bridgeExe -WorkingDirectory $bridgeDir -WindowStyle Hidden
    if (Test-Path $watchdogExe) { Start-Process $watchdogExe -WorkingDirectory $bridgeDir -WindowStyle Hidden }

    $bridgePort = 0
    foreach ($port in @(51789, 52789, 53789, 54789)) {
        for ($i = 0; $i -lt 20; $i++) {
            try {
                $r = Invoke-WebRequest "http://127.0.0.1:$port/now.json" -UseBasicParsing -TimeoutSec 2
                if ($r.StatusCode -eq 200) { $bridgePort = $port; break }
            } catch { Start-Sleep -Milliseconds 400 }
        }
        if ($bridgePort) { break }
    }
    if ($bridgePort) {
        Write-Host "控制桥已启动（端口 $bridgePort）" -ForegroundColor Green
    } else {
        Write-Host '控制桥没有响应，网易云跟随会不可用。' -ForegroundColor Yellow
        Write-Host "可手动运行：$bridgeExe"
    }

    $wp = Join-Path $we 'projects\myprojects\Miku Study Room\index.html'
    Start-Process (Join-Path $we 'wallpaper32.exe') -ArgumentList @('-control','openWallpaper','-file',$wp)
    Start-Sleep -Milliseconds 1500

    try {
        $ws = New-Object -ComObject WScript.Shell
        $startup = [Environment]::GetFolderPath('Startup')
        $lnk = $ws.CreateShortcut((Join-Path $startup 'MikuWallpaperBridge.lnk'))
        $lnk.TargetPath = $bridgeExe
        $lnk.WorkingDirectory = $bridgeDir
        $lnk.Save()
        if (Test-Path $watchdogExe) {
            $lnkWD = $ws.CreateShortcut((Join-Path $startup 'MikuWallpaperWatchdog.lnk'))
            $lnkWD.TargetPath = $watchdogExe
            $lnkWD.WorkingDirectory = $bridgeDir
            $lnkWD.WindowStyle = 7
            $lnkWD.Save()
        }
        Write-Host '已添加开机自启。' -ForegroundColor Green
    } catch {
        Write-Host '添加开机自启失败（不影响本次使用）。' -ForegroundColor Yellow
    }

    try {
        $ws2 = New-Object -ComObject WScript.Shell
        $aiExe = Join-Path $bridgeDir 'AiSettings.exe'
        if (Test-Path $aiExe) {
            foreach ($dir in @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'))) {
                if (-not $dir) { continue }
                $lnk2 = $ws2.CreateShortcut((Join-Path $dir 'Miku 壁纸 AI 设置.lnk'))
                $lnk2.TargetPath = $aiExe
                $lnk2.WorkingDirectory = $bridgeDir
                $lnk2.Save()
            }
            Write-Host '已创建“Miku 壁纸 AI 设置”快捷方式。' -ForegroundColor Green
        }
    } catch {
        Write-Host '创建 AI 设置快捷方式失败（不影响壁纸）。' -ForegroundColor Yellow
    }

    Write-Host ''
    Write-Host '安装完成。' -ForegroundColor Green
    Write-Host '壁纸已应用到主显示器；如果没看到，在 WE 的“已安装”里选择 “Miku Study Room”。'
    Write-Host "控制桥位置：$bridgeDir"
    Pause-Exit 0
}
catch {
    Write-Host ''
    Write-Host '安装失败：' -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ($_.ScriptStackTrace) -ForegroundColor DarkGray
    Pause-Exit 1
}
finally {
    try { Stop-Transcript | Out-Null } catch { }
}
