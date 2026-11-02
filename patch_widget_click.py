import io

p = r"D:\MikuWallpaper\pomodoro\Pomodoro.cs"
t = io.open(p, encoding="utf-8").read()

old = """        MouseDown += delegate (object s, MouseEventArgs e) {
            if (e.Button == MouseButtons.Left) Toggle();
        };"""
new = """        MouseEventHandler onDown = delegate (object s, MouseEventArgs e) {
            if (e.Button == MouseButtons.Left) Toggle();
        };
        MouseDown += onDown;
        lbl.MouseDown += onDown;
        lbl.ContextMenuStrip = menu;"""
t = t.replace(old, new)
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("patched")
