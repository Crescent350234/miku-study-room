import io

p = r"D:\MikuWallpaper\player\src\DesktopOverlay.cs"
t = io.open(p, encoding="utf-8-sig").read()

old = 'view.CoreWebView2.SetVirtualHostNameToFolderMapping("miku-overlay.local",Path.GetFullPath(Path.Combine(root,"..","wallpaper")),CoreWebView2HostResourceAccessKind.DenyCors);'
new = 'view.CoreWebView2.SetVirtualHostNameToFolderMapping("miku-overlay.local",PageRoot(),CoreWebView2HostResourceAccessKind.DenyCors);'
if old in t:
    t = t.replace(old, new, 1)
    print("mapping patched")
else:
    print("mapping not found")

helper = '''
    string PageRoot()
    {
        try
        {
            string ini = Path.Combine(root, "overlay.ini");
            if (File.Exists(ini))
                foreach (string line in File.ReadAllLines(ini))
                    if (line.StartsWith("wallpaper=", StringComparison.OrdinalIgnoreCase))
                        return Path.GetFullPath(line.Substring(10).Trim());
        }
        catch { }
        return Path.GetFullPath(Path.Combine(root, "..", "wallpaper"));
    }

'''
if "string PageRoot()" not in t:
    t = t.replace("    async Task Initialize()", helper + "    async Task Initialize()", 1)
    print("helper added")

io.open(p, "w", encoding="utf-8", newline="").write(t)
