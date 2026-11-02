import io

p = r"D:\MikuWallpaper\bridge\AiSettings.cs"
t = io.open(p, encoding="utf-8").read()

helper = '''    private static void StyleDark(Control root)
    {
        foreach (Control c in root.Controls)
        {
            Label l = c as Label;
            if (l != null) l.ForeColor = Color.FromArgb(220, 235, 231);
            CheckBox cb = c as CheckBox;
            if (cb != null) cb.ForeColor = Color.FromArgb(220, 235, 231);
            TextBox tb = c as TextBox;
            if (tb != null)
            {
                tb.BackColor = Color.FromArgb(30, 46, 42);
                tb.ForeColor = Color.FromArgb(236, 246, 243);
            }
            ComboBox cmb = c as ComboBox;
            if (cmb != null)
            {
                cmb.BackColor = Color.FromArgb(30, 46, 42);
                cmb.ForeColor = Color.FromArgb(236, 246, 243);
            }
            Button b = c as Button;
            if (b != null)
            {
                b.BackColor = Color.FromArgb(38, 56, 51);
                b.ForeColor = Color.FromArgb(230, 242, 238);
                b.FlatAppearance.BorderColor = Color.FromArgb(72, 102, 94);
            }
            StyleDark(c);
        }
    }

'''

if "private static void StyleDark" not in t:
    idx = t.find("    private static void StyleUi(Control root)")
    if idx < 0:
        idx = t.find("private static void StyleUi(Control root)")
    if idx < 0:
        raise SystemExit("StyleUi anchor missing")
    t = t[:idx] + helper + t[idx:]

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("StyleDark inserted")
