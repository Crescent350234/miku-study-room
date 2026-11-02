import io

p = r"D:\MikuWallpaper\bridge\AiSettings.cs"
t = io.open(p, encoding="utf-8").read()

# 主界面加按钮，并把背景按钮改窄
t = t.replace('btnBg.Location = new Point(245, 462);\n        btnBg.Width = 140;',
              'btnBg.Location = new Point(240, 462);\n        btnBg.Width = 120;')
if "btnMusic" not in t:
    t = t.replace('''        Controls.Add(btnBg);
''', '''        Controls.Add(btnBg);

        Button btnMusic = new Button();
        btnMusic.Text = "本地音乐…";
        btnMusic.Location = new Point(370, 462);
        btnMusic.Width = 120;
        btnMusic.Click += delegate { using (var f = new MusicForm()) f.ShowDialog(this); };
        Controls.Add(btnMusic);
''', 1)

music_class = r'''

public class MusicForm : Form
{
    private ListBox lst;
    private Label lbl;
    private Button btnImport;
    private Button btnClear;

    public MusicForm()
    {
        Text = "本地歌单";
        ClientSize = new Size(560, 420);
        StartPosition = FormStartPosition.CenterParent;
        FormBorderStyle = FormBorderStyle.FixedSingle;
        MaximizeBox = false;
        Font = new Font("Microsoft YaHei UI", 9.5f);
        BackColor = Color.FromArgb(24, 38, 35);

        Label title = new Label();
        title.Text = "本地歌单";
        title.Font = new Font("Microsoft YaHei UI", 12f, FontStyle.Bold);
        title.ForeColor = Color.FromArgb(220, 235, 231);
        title.Location = new Point(22, 18);
        title.AutoSize = true;
        Controls.Add(title);

        lbl = new Label();
        lbl.Text = "音乐和歌词会复制到壁纸工程的 music 文件夹。";
        lbl.ForeColor = Color.FromArgb(150, 175, 168);
        lbl.Location = new Point(24, 50);
        lbl.AutoSize = true;
        Controls.Add(lbl);

        lst = new ListBox();
        lst.Location = new Point(24, 82);
        lst.Width = 510;
        lst.Height = 240;
        lst.BackColor = Color.FromArgb(30, 46, 42);
        lst.ForeColor = Color.FromArgb(230, 242, 238);
        lst.BorderStyle = BorderStyle.FixedSingle;
        Controls.Add(lst);

        btnImport = new Button();
        btnImport.Text = "导入音乐（可多选）";
        btnImport.Location = new Point(24, 336);
        btnImport.Width = 200;
        btnImport.Height = 34;
        btnImport.Click += delegate { Import(); };
        Controls.Add(btnImport);

        btnClear = new Button();
        btnClear.Text = "清空歌单";
        btnClear.Location = new Point(238, 336);
        btnClear.Width = 120;
        btnClear.Height = 34;
        btnClear.Click += delegate {
            if (MessageBox.Show(this, "只清空歌单列表，不删除 music 里的文件。继续？", "确认", MessageBoxButtons.YesNo) == DialogResult.Yes)
            {
                if (ProjectDir() != null) File.WriteAllText(Path.Combine(ProjectDir(), "music", "playlist.json"), "[]", new UTF8Encoding(false));
                LoadList();
            }
        };
        Controls.Add(btnClear);

        Button close = new Button();
        close.Text = "关闭";
        close.Location = new Point(440, 336);
        close.Width = 94;
        close.Height = 34;
        close.Click += delegate { Close(); };
        Controls.Add(close);

        Style(this);
        LoadList();
    }

    private static void Style(Control root)
    {
        foreach (Control c in root.Controls)
        {
            Button b = c as Button;
            if (b != null)
            {
                b.FlatStyle = FlatStyle.Flat;
                b.FlatAppearance.BorderColor = Color.FromArgb(72, 102, 94);
                b.BackColor = Color.FromArgb(38, 56, 51);
                b.ForeColor = Color.FromArgb(230, 242, 238);
                b.Cursor = Cursors.Hand;
            }
            Style(c);
        }
    }

    private static string ProjectDir()
    {
        string we = null;
        try
        {
            string ini = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), @"MikuWallpaper\installer.ini");
            if (File.Exists(ini))
            {
                foreach (string line in File.ReadAllLines(ini))
                {
                    if (line.StartsWith("we=", StringComparison.OrdinalIgnoreCase)) { we = line.Substring(3).Trim(); break; }
                }
            }
        }
        catch { }

        var candidates = new List<string>();
        if (!string.IsNullOrEmpty(we)) candidates.Add(we);
        candidates.Add(@"C:\Program Files (x86)\Steam\steamapps\common\wallpaper_engine");
        candidates.Add(@"C:\Program Files\Steam\steamapps\common\wallpaper_engine");
        candidates.Add(@"D:\Steam\steamapps\common\wallpaper_engine");
        candidates.Add(@"D:\SteamLibrary\steamapps\common\wallpaper_engine");
        candidates.Add(@"E:\Steam\steamapps\common\wallpaper_engine");

        foreach (string c in candidates)
        {
            string proj = Path.Combine(c, @"projects\myprojects\Miku Study Room");
            if (Directory.Exists(proj)) return proj;
        }
        return null;
    }

    private string MusicDir()
    {
        string proj = ProjectDir();
        if (proj == null) return null;
        string dir = Path.Combine(proj, "music");
        Directory.CreateDirectory(dir);
        return dir;
    }

    private void LoadList()
    {
        lst.Items.Clear();
        try
        {
            string proj = ProjectDir();
            if (proj == null) return;
            string file = Path.Combine(proj, "music", "playlist.json");
            if (!File.Exists(file)) return;
            string json = File.ReadAllText(file, Encoding.UTF8).Trim();
            if (json.Length < 3) return;
            int pos = 0;
            while (true)
            {
                int i = json.IndexOf("\"file\":\"", pos, StringComparison.Ordinal);
                if (i < 0) break;
                i += 8;
                int j = json.IndexOf('"', i);
                if (j < 0) break;
                lst.Items.Add(json.Substring(i, j - i));
                pos = j;
            }
        }
        catch { }
    }

    private void Import()
    {
        string music = MusicDir();
        if (music == null)
        {
            MessageBox.Show(this, "找不到已安装的壁纸工程，请先用安装器安装一次。", "未安装", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            return;
        }

        using (var dlg = new OpenFileDialog())
        {
            dlg.Title = "选择音乐文件（可多选）";
            dlg.Multiselect = true;
            dlg.Filter = "音频|*.mp3;*.flac;*.wav;*.m4a;*.ogg;*.aac|所有文件|*.*";
            if (dlg.ShowDialog(this) != DialogResult.OK) return;

            // 可选：再选一次同名 lrc
            string[] lyrics = new string[0];
            if (MessageBox.Show(this, "是否同时选择对应的 .lrc 歌词文件？", "歌词", MessageBoxButtons.YesNo, MessageBoxIcon.Question) == DialogResult.Yes)
            {
                using (var dlg2 = new OpenFileDialog())
                {
                    dlg2.Title = "选择歌词文件（可多选，可取消）";
                    dlg2.Multiselect = true;
                    dlg2.Filter = "歌词|*.lrc|所有文件|*.*";
                    if (dlg2.ShowDialog(this) == DialogResult.OK) lyrics = dlg2.FileNames;
                }
            }

            try
            {
                var entries = new List<string>();
                foreach (string src in dlg.FileNames)
                {
                    string name = Path.GetFileNameWithoutExtension(src);
                    string ext = Path.GetExtension(src);
                    string target = Path.Combine(music, name + ext);
                    File.Copy(src, target, true);

                    string lrcName = "";
                    foreach (string l in lyrics)
                    {
                        if (string.Equals(Path.GetFileNameWithoutExtension(l), name, StringComparison.OrdinalIgnoreCase))
                        {
                            File.Copy(l, Path.Combine(music, name + ".lrc"), true);
                            lrcName = name + ".lrc";
                            break;
                        }
                    }

                    entries.Add("{\"name\":" + Q(name) + ",\"artist\":\"本地\",\"file\":" + Q(name + ext) + ",\"lrc\":" + Q(lrcName) + "}");
                }

                string playlist = Path.Combine(music, "playlist.json");
                string existing = "[]";
                if (File.Exists(playlist))
                {
                    existing = File.ReadAllText(playlist, Encoding.UTF8).Trim();
                    if (existing.Length <= 2) existing = "[]";
                }

                string merged;
                if (existing == "[]") merged = "[" + string.Join(",", entries.ToArray()) + "]";
                else merged = existing.TrimEnd(']') + "," + string.Join(",", entries.ToArray()) + "]";

                File.WriteAllText(playlist, merged, new UTF8Encoding(false));
                LoadList();
                MessageBox.Show(this, "已导入 " + entries.Count + " 首。\n\n重载壁纸后，内置播放会使用本地歌单。",
                    "完成", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            catch (Exception ex)
            {
                MessageBox.Show(this, "导入失败：" + ex.Message, "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
    }

    private static string Q(string s)
    {
        if (s == null) return "\"\"";
        return "\"" + s.Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"";
    }
}
'''

if "class MusicForm" not in t:
    t = t.rstrip() + "\n" + music_class

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("MusicForm added")
