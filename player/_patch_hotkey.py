import io

p = r"D:\MikuWallpaper\player\src\DesktopOverlay.cs"
t = io.open(p, encoding="utf-8-sig").read()

if "ToggleHotkeyPressed" not in t:
    t = t.replace("    void GuardNativeInput()\n    {", """    [DllImport("user32.dll")] static extern short GetAsyncKeyState(int key);
    bool hotkeyDown;

    void GuardNativeInput()
    {
        bool combo = (GetAsyncKeyState(0x11) & 0x8000) != 0 && (GetAsyncKeyState(0x12) & 0x8000) != 0 && (GetAsyncKeyState(0x58) & 0x8000) != 0;
        if (combo && !hotkeyDown) { hotkeyDown = true; Dispatcher.Invoke(new Action(Toggle)); }
        else if (!combo) hotkeyDown = false;
""", 1)
    print("hotkey added")
else:
    print("exists")

io.open(p, "w", encoding="utf-8", newline="").write(t)
