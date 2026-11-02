import io

p = r"D:\MikuWallpaper\bridge\bridge.cs"
t = io.open(p, encoding="utf-8").read()

if "/focus.json" not in t:
    anchor = 'else if (path.StartsWith("/focus.toggle"))'
    add = '''else if (path.StartsWith("/focus.json"))
                        {
                            Send(stream, "application/json; charset=utf-8", Encoding.UTF8.GetBytes("{\\"focus\\":" + (FocusMode.IsOn ? "true" : "false") + "}"));
                        }
                        ''' + anchor
    t = t.replace(anchor, add, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("patched")
