import io, os

p = r"D:\MikuWallpaper\bridge\AiSettings.cs"
t = io.open(p, encoding="utf-8").read()

if "btnDeleteBg" not in t:
    anchor = """        Button close = new Button();
        close.Text = "关闭";
        close.Location = new Point(384, 208);"""
    add = """        Button btnDeleteBg = new Button();
        btnDeleteBg.Text = "删除自定义背景";
        btnDeleteBg.Location = new Point(24, 208);
        btnDeleteBg.Width = 180;
        btnDeleteBg.Height = 30;
        btnDeleteBg.Click += delegate { DeleteCustomBg(); };
        Controls.Add(btnDeleteBg);

        Button close = new Button();
        close.Text = "关闭";
        close.Location = new Point(384, 208);"""
    t = t.replace(anchor, add, 1)

    # 删除方法
    anchor2 = """    private void PickVideo()"""
    method = """    private void DeleteCustomBg()
    {
        string dir = CustomDir();
        if (dir == null)
        {
            MessageBox.Show(this, "找不到已安装的壁纸工程。", "未安装", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            return;
        }

        var r = MessageBox.Show(this,
            "删除自定义背景（bg.jpg / bg.png / bg.webm）？\\n\\n删除后请在壁纸设置 → 背景里重新选择其他场景。",
            "确认删除", MessageBoxButtons.YesNo, MessageBoxIcon.Question);
        if (r != DialogResult.Yes) return;

        int n = 0;
        foreach (string name in new string[] { "bg.jpg", "bg.png", "bg.webm" })
        {
            try
            {
                string f = Path.Combine(dir, name);
                if (File.Exists(f)) { File.Delete(f); n++; }
            }
            catch { }
        }
        SetStatus(n > 0 ? "已删除 " + n + " 个文件。请在壁纸设置里切换背景。" : "没有可删除的自定义背景。");
    }

    private void PickVideo()"""
    t = t.replace(anchor2, method, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("delete bg added")
