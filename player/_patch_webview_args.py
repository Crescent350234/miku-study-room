import io

p = r"D:\MikuWallpaper\player\src\DesktopOverlay.cs"
t = io.open(p, encoding="utf-8-sig").read()

old = "CoreWebView2Environment environment=await CoreWebView2Environment.CreateAsync(null,Path.Combine(OverlayPaths.Home,\"WebViewCache\"));"
new = """CoreWebView2EnvironmentOptions webOptions=new CoreWebView2EnvironmentOptions("--disable-web-security --allow-running-insecure-content --disable-features=BlockInsecurePrivateNetworkRequests");
            CoreWebView2Environment environment=await CoreWebView2Environment.CreateAsync(null,Path.Combine(OverlayPaths.Home,"WebViewCache"),webOptions);"""

if old in t:
    t = t.replace(old, new, 1)
    print("webview args patched")
else:
    print("anchor missing")

io.open(p, "w", encoding="utf-8", newline="").write(t)
