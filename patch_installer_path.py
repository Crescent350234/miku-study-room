import io, os, re

p = r"D:\MikuWallpaper-dist\Miku Study Room\installer.ps1"
t = io.open(p, encoding="utf-8-sig").read()

# 1) 增加路径解析函数
if "function Resolve-WE" not in t:
    t = t.replace("function Find-WallpaperEngine {", r'''function Resolve-WE($path) {
    if (-not $path) { return $null }
    $path = $path.Trim().Trim('"')
    if (Test-Path $path -PathType Leaf) { $path = Split-Path -Parent $path }
    if (Test-Path (Join-Path $path 'wallpaper32.exe')) { return $path }
    return $null
}

function Find-WallpaperEngine {''')

# 2) 检测逻辑：we.txt 优先 -> 自动 -> 手动输入
old = """    $we = Find-WallpaperEngine
    if (-not $we) {
        Write-Host '没有找到 Wallpaper Engine。' -ForegroundColor Red
        Write-Host '请确认已安装并至少启动过一次；或手动把 wallpaper 文件夹拖进 WE 的“创建壁纸 → 网页”。'
        Pause-Exit 1
    }
    Write-Host "Wallpaper Engine: $we\""""

new = """    $we = $null
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
    Write-Host "Wallpaper Engine: $we\""""

if old in t:
    t = t.replace(old, new)
else:
    raise SystemExit("detect anchor miss")

io.open(p, "w", encoding="utf-8-sig", newline="").write(t)
print("installer manual path patched")
