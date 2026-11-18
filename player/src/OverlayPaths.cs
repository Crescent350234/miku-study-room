using System;
using System.IO;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Security.Principal;
using Microsoft.Win32;
public static class OverlayPaths
{
    public static readonly string Home=Path.Combine(SetupCore.Data,"DesktopPlayer");
    public static readonly string Bridge=SetupCore.Bridge;
    public static void OpenSettings() {
        Process.Start(new ProcessStartInfo(Path.Combine(Bridge,"AiSettings.exe")){WorkingDirectory=Bridge});
    }
    public static void Shortcut(string folder,string name,string target,string args) {
        dynamic shell=Activator.CreateInstance(Type.GetTypeFromProgID("WScript.Shell"));
        dynamic link=shell.CreateShortcut(Path.Combine(folder,name+".lnk"));link.TargetPath=target;link.Arguments=args;link.WorkingDirectory=Path.GetDirectoryName(target);link.Save();
        Marshal.FinalReleaseComObject(link);Marshal.FinalReleaseComObject(shell);
    }
}
