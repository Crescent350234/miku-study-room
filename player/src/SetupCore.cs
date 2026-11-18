using System;
using System.Diagnostics;
using System.IO;
using System.Text;

public static class SetupCore
{
    public static readonly string Data = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "MikuWallpaper");
    public static readonly string Bridge = Path.Combine(Data, "bridge");
    public static readonly string LogFile = Path.Combine(Data, "player.log");

    public static void Log(string message)
    {
        try
        {
            Directory.CreateDirectory(Data);
            File.AppendAllText(LogFile,
                DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + "  " + message + "\r\n",
                new UTF8Encoding(false));
        }
        catch { }
    }

    public static void StartBridge()
    {
        try
        {
            if (Process.GetProcessesByName("bridge").Length > 0) return;
            string exe = Path.Combine(Bridge, "bridge.exe");
            if (!File.Exists(exe)) { Log("bridge.exe missing: " + exe); return; }
            Process.Start(new ProcessStartInfo(exe)
            {
                WorkingDirectory = Bridge,
                UseShellExecute = true,
                WindowStyle = ProcessWindowStyle.Hidden
            });
        }
        catch (Exception ex) { Log("StartBridge failed: " + ex.Message); }
    }
}
