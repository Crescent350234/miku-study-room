using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Threading.Tasks;
using System.Threading;
using System.Web.Script.Serialization;
using System.Windows;
using System.Windows.Interop;
using System.Windows.Media;
using System.Windows.Threading;
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.Wpf;
using Forms=System.Windows.Forms;

public sealed class DesktopOverlay : Window
{
    const int GWL_EXSTYLE=-20, WS_EX_TRANSPARENT=0x20, WS_EX_TOOLWINDOW=0x80, WS_EX_NOACTIVATE=0x08000000;
    const uint SWP_NOSIZE=1,SWP_NOMOVE=2,SWP_NOACTIVATE=0x10;
    const int WM_SHOWLAYER=0x8000+311;
    WebView2CompositionControl view=new WebView2CompositionControl();
    Forms.NotifyIcon tray=new Forms.NotifyIcon();
    DispatcherTimer orderTimer=new DispatcherTimer();
    List<InputProxy> proxies=new List<InputProxy>();
    List<Rect> regions=new List<Rect>();
    double pageWidth=1,pageHeight=1;
    IntPtr handle;bool ready,attached;volatile bool closing,shutdownComplete;
    readonly PlayerPresence presence;
    const string WindowTitle="Miku 桌面播放器";
    long guardHeartbeat=Stopwatch.GetTimestamp();
    long lastRegionTick=Stopwatch.GetTimestamp();
    JavaScriptSerializer json=new JavaScriptSerializer();
    string root=AppDomain.CurrentDomain.BaseDirectory;
    CoreWebView2Environment webEnvironment;
    DispatcherTimer guardTimer=new DispatcherTimer();
    bool safetyStopping;

    public DesktopOverlay()
    {
        presence=new PlayerPresence();
        if (presence.Port == 0) SetupCore.Log("独立播放器已启动，壁纸去重端口暂不可用。");
        Title=WindowTitle;
        WindowStyle=WindowStyle.None;ResizeMode=ResizeMode.NoResize;
        AllowsTransparency=true;Background=Brushes.Transparent;
        ShowInTaskbar=false;ShowActivated=false;Topmost=false;
        FitScreen();
        view.DefaultBackgroundColor=System.Drawing.Color.Transparent;
        Content=view;
        SourceInitialized+=delegate {
            handle=new WindowInteropHelper(this).Handle;
            SetWindowLong(handle,GWL_EXSTYLE,GetWindowLong(handle,GWL_EXSTYLE)|WS_EX_TOOLWINDOW|WS_EX_NOACTIVATE|WS_EX_TRANSPARENT);
            HwndSource.FromHwnd(handle).AddHook(WindowMessage);
            PlaceAtDesktop();
        };
        Loaded+=async delegate {await Initialize();};
        Forms.ContextMenuStrip menu=new Forms.ContextMenuStrip();
        menu.Items.Add("显示 / 隐藏歌词播放器",null,delegate {Dispatcher.Invoke(new Action(Toggle));});
        menu.Items.Add("原版设置（歌词特效 / 字体）",null,delegate {Dispatcher.Invoke(new Action(async delegate {if(!IsVisible)Show();if(ready)await view.CoreWebView2.ExecuteScriptAsync("document.getElementById('settingsBtn').click()");}));});
        menu.Items.Add("设置 API / 网易云快捷键",null,delegate {try{OverlayPaths.OpenSettings();}catch(Exception ex){Forms.MessageBox.Show(ex.Message,"设置未能打开");}});
        Forms.ToolStripMenuItem startup=new Forms.ToolStripMenuItem("开机显示歌词播放器");
        startup.Checked=File.Exists(Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Startup),"MikuDesktopOverlay.lnk"));
        startup.CheckOnClick=true;
        startup.CheckedChanged+=delegate {
            try {
                string folder=Environment.GetFolderPath(Environment.SpecialFolder.Startup);
                if(startup.Checked)OverlayPaths.Shortcut(folder,"MikuDesktopOverlay",Path.Combine(root,"Miku Player.exe"),"");
                else {string file=Path.Combine(folder,"MikuDesktopOverlay.lnk");if(File.Exists(file))File.Delete(file);}
            }catch(Exception ex){Forms.MessageBox.Show(ex.Message,"开机启动设置失败");}
        };
        menu.Items.Add(startup);menu.Items.Add(new Forms.ToolStripSeparator());
        menu.Items.Add("退出桌面歌词",null,delegate {Dispatcher.Invoke(new Action(Close));});
        tray.Icon=System.Drawing.SystemIcons.Application;tray.Text=WindowTitle;tray.ContextMenuStrip=menu;tray.Visible=true;
        tray.DoubleClick+=delegate{Dispatcher.Invoke(new Action(Toggle));};
        orderTimer.Interval=TimeSpan.FromMilliseconds(900);orderTimer.Tick+=delegate{if(IsVisible)PlaceAtDesktop();};orderTimer.Start();
        guardTimer.Interval=TimeSpan.FromMilliseconds(150);guardTimer.Tick+=delegate{GuardNativeInput();};guardTimer.Start();
        Thread emergency=new Thread(delegate(){
            while(!shutdownComplete){
                if(NativeInputGuard.EmergencyExitPressed())Environment.Exit(0);
                double silent=(Stopwatch.GetTimestamp()-Interlocked.Read(ref guardHeartbeat))/(double)Stopwatch.Frequency;
                if(silent>(closing?3:8))Environment.Exit(2);
                Thread.Sleep(75);
            }
        });emergency.IsBackground=true;emergency.Start();
        Microsoft.Win32.SystemEvents.DisplaySettingsChanged+=DisplayChanged;
        Closed+=delegate{
            presence.Dispose();
            closing=true;orderTimer.Stop();guardTimer.Stop();
            Interlocked.Exchange(ref guardHeartbeat,Stopwatch.GetTimestamp());
        if((Stopwatch.GetTimestamp()-Interlocked.Read(ref lastRegionTick))/(double)Stopwatch.Frequency>3&&proxies.Any(p=>p.Visible)){
            foreach(InputProxy proxy in proxies)proxy.Hide();
            presence.Active=false;
        }
            foreach(InputProxy proxy in proxies)proxy.Dispose();
            Microsoft.Win32.SystemEvents.DisplaySettingsChanged-=DisplayChanged;
            tray.Visible=false;tray.Dispose();view.Dispose();
            shutdownComplete=true;
        };
    }
    [DllImport("user32.dll")] static extern short GetAsyncKeyState(int key);
    bool hotkeyDown;

    void GuardNativeInput()
    {
        bool combo = (GetAsyncKeyState(0x11) & 0x8000) != 0 && (GetAsyncKeyState(0x12) & 0x8000) != 0 && (GetAsyncKeyState(0x58) & 0x8000) != 0;
        if (combo && !hotkeyDown) { hotkeyDown = true; Dispatcher.Invoke(new Action(Toggle)); }
        else if (!combo) hotkeyDown = false;

        if(handle==IntPtr.Zero||closing||safetyStopping)return;
        Interlocked.Exchange(ref guardHeartbeat,Stopwatch.GetTimestamp());
        try{
            var pids=new List<int>{Process.GetCurrentProcess().Id};
            if(webEnvironment!=null)pids.AddRange(webEnvironment.GetProcessInfos().Select(p=>(int)p.ProcessId));
            int changes;
            bool safe=NativeInputGuard.Enforce(handle,pids.ToArray(),proxies.Where(p=>p.IsHandleCreated).Select(p=>p.Handle).ToArray(),(int)(Width*VisualTreeHelper.GetDpi(this).DpiScaleX),(int)(Height*VisualTreeHelper.GetDpi(this).DpiScaleY),out changes);
            if(!safe){
                safetyStopping=true;presence.Active=false;Hide();foreach(InputProxy proxy in proxies)proxy.Hide();
                Directory.CreateDirectory(OverlayPaths.Home);
                File.WriteAllText(Path.Combine(OverlayPaths.Home,"safety-stop.txt"),"An unverified native fullscreen input surface was detected. Overlay stopped to preserve desktop input.");
                Close();
            }
        }catch{
            // Losing the ability to audit native input is itself a reason to stop the overlay.
            safetyStopping=true;Close();
        }
    }
    void DisplayChanged(object sender,EventArgs e){Dispatcher.BeginInvoke(new Action(FitScreen));}
    void FitScreen(){Rect work=SystemParameters.WorkArea;Left=work.Left;Top=work.Top;Width=work.Width;Height=work.Height;}
    void Toggle(){
        if(IsVisible){presence.Active=false;Hide();foreach(InputProxy proxy in proxies)proxy.Hide();}
        else{Show();SyncInputProxies();}
    }
    IntPtr WindowMessage(IntPtr hwnd,int message,IntPtr wParam,IntPtr lParam,ref bool handled)
    {
        if(message==0x21){handled=true;return new IntPtr(3);} // MA_NOACTIVATE
        if(message==0x84){handled=true;return new IntPtr(-1);} // Never hit-test the fullscreen visual layer.
        if(message==WM_SHOWLAYER){if(!IsVisible)Show();SyncInputProxies();handled=true;}
        return IntPtr.Zero;
    }
    void PlaceAtDesktop()
    {
        if(handle==IntPtr.Zero)return;
        IntPtr previous=IntPtr.Zero,after=IntPtr.Zero;bool found=false;
        EnumWindows(delegate(IntPtr window,IntPtr state){
            if(window==handle || proxies.Any(p=>p.IsHandleCreated&&p.Handle==window))return true;
            if(FindWindowEx(window,IntPtr.Zero,"SHELLDLL_DefView",null)!=IntPtr.Zero){
                after=previous;found=true;return false;
            }
            if(IsWindowVisible(window))previous=window;
            return true;
        },IntPtr.Zero);
        attached=found && IsVisible && SetWindowPos(handle,after,0,0,0,0,SWP_NOMOVE|SWP_NOSIZE|SWP_NOACTIVATE);
        if(attached){
            foreach(InputProxy proxy in proxies)if(proxy.Visible)SetWindowPos(proxy.Handle,after,0,0,0,0,SWP_NOMOVE|SWP_NOSIZE|SWP_NOACTIVATE);
        }
        else {foreach(InputProxy proxy in proxies)proxy.Hide();}
        presence.Active=attached && ready && !closing && !safetyStopping && proxies.Any(p=>p.Visible);
    }
    void SyncInputProxies()
    {
        if(handle==IntPtr.Zero || closing)return;
        // Fail closed: the fullscreen render surface NEVER receives mouse input.
        int style=GetWindowLong(handle,GWL_EXSTYLE);
        if((style&WS_EX_TRANSPARENT)==0)SetWindowLong(handle,GWL_EXSTYLE,style|WS_EX_TRANSPARENT);
        List<Rect> safe=SafeInputRegions(regions,pageWidth,pageHeight).ToList();
        while(proxies.Count<safe.Count)proxies.Add(new InputProxy(this));
        for(int i=0;i<proxies.Count;i++){
            InputProxy proxy=proxies[i];
            if(!IsVisible || i>=safe.Count){proxy.Hide();continue;}
            Rect r=safe[i];
            Point a=view.PointToScreen(new Point(r.Left*view.ActualWidth/pageWidth,r.Top*view.ActualHeight/pageHeight));
            Point b=view.PointToScreen(new Point(r.Right*view.ActualWidth/pageWidth,r.Bottom*view.ActualHeight/pageHeight));
            proxy.Bounds=new System.Drawing.Rectangle((int)Math.Floor(a.X),(int)Math.Floor(a.Y),Math.Max(1,(int)Math.Ceiling(b.X-a.X)),Math.Max(1,(int)Math.Ceiling(b.Y-a.Y)));
            if(!proxy.Visible)proxy.Show();
        }
        PlaceAtDesktop();
    }
    public static Rect[] SafeInputRegions(IEnumerable<Rect> source,double width,double height)
    {
        if(width<=0 || height<=0 || Double.IsNaN(width) || Double.IsNaN(height) || Double.IsInfinity(width) || Double.IsInfinity(height))return new Rect[0];
        Rect viewport=new Rect(0,0,width,height);
        return source.Where(r=>!r.IsEmpty && !Double.IsNaN(r.X+r.Y+r.Width+r.Height) && !Double.IsInfinity(r.X+r.Y+r.Width+r.Height))
            .Select(r=>Rect.Intersect(r,viewport))
            .Where(r=>!r.IsEmpty && r.Width<width*.85 && r.Height<height*.82 && r.Width>=8 && r.Height>=8)
            .Take(8).ToArray();
    }
    async void ForwardMouse(string type,System.Drawing.Point screen,string button,int clicks,int delta)
    {
        if(!ready||closing)return;
        try{
            Point local=view.PointFromScreen(new Point(screen.X,screen.Y));
            var input=new Dictionary<string,object>{{"type",type},{"x",local.X*pageWidth/Math.Max(1,view.ActualWidth)},{"y",local.Y*pageHeight/Math.Max(1,view.ActualHeight)}};
            if(type=="mouseWheel"){input["deltaX"]=0;input["deltaY"]=delta;}
            else {input["button"]=button;input["clickCount"]=clicks;}
            await view.CoreWebView2.CallDevToolsProtocolMethodAsync("Input.dispatchMouseEvent",json.Serialize(input));
        }catch{}
    }

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

    async Task Initialize()
    {
        try {
            try { await Task.Run(() => SetupCore.StartBridge()); } catch(Exception ex) { SetupCore.Log(ex.Message); }
            Directory.CreateDirectory(OverlayPaths.Home);
            CoreWebView2EnvironmentOptions webOptions=new CoreWebView2EnvironmentOptions("--disable-web-security --allow-running-insecure-content --disable-features=BlockInsecurePrivateNetworkRequests");
            CoreWebView2Environment environment=await CoreWebView2Environment.CreateAsync(null,Path.Combine(OverlayPaths.Home,"WebViewCache"),webOptions);
            webEnvironment=environment;
            await view.EnsureCoreWebView2Async(environment);
            GuardNativeInput();if(safetyStopping||closing)return;
            view.CoreWebView2.Settings.AreDefaultContextMenusEnabled=false;
            view.CoreWebView2.Settings.IsStatusBarEnabled=false;
            view.CoreWebView2.Settings.AreDevToolsEnabled=false;
            view.CoreWebView2.SetVirtualHostNameToFolderMapping("miku-overlay.local",PageRoot(),CoreWebView2HostResourceAccessKind.DenyCors);
            view.CoreWebView2.WebMessageReceived+=delegate(object sender,CoreWebView2WebMessageReceivedEventArgs e){
                Uri uri;if(!Uri.TryCreate(e.Source,UriKind.Absolute,out uri)||uri.Host!="miku-overlay.local")return;
                try {
                    RegionMessage data=json.Deserialize<RegionMessage>(e.TryGetWebMessageAsString());
                    if(data.kind!="regions"||data.width<=0||data.height<=0)return;
                    lastRegionTick=Stopwatch.GetTimestamp();pageWidth=data.width;pageHeight=data.height;
                    regions=(data.rects??new RegionBox[0]).Where(r=>r.w>0&&r.h>0).Select(r=>new Rect(r.x,r.y,r.w,r.h)).ToList();
                    SyncInputProxies();
                }catch{}
            };
            view.CoreWebView2.NewWindowRequested+=delegate(object sender,CoreWebView2NewWindowRequestedEventArgs e){e.Handled=true;};
            view.CoreWebView2.NavigationStarting+=delegate(object sender,CoreWebView2NavigationStartingEventArgs e){Uri uri;if(!Uri.TryCreate(e.Uri,UriKind.Absolute,out uri)||uri.Host!="miku-overlay.local")e.Cancel=true;};
            view.CoreWebView2.ProcessFailed+=delegate {
                if(closing)return;
                presence.Active=false;ready=false;
                SetupCore.Log("桌面播放器的网页进程已停止。");
                Close();
            };
            view.CoreWebView2.NavigationCompleted+=delegate(object sender,CoreWebView2NavigationCompletedEventArgs e){
                if(!e.IsSuccess){presence.Active=false;Close();return;}
                ready=true;SyncInputProxies();
            };
            view.Source=new Uri("https://miku-overlay.local/index.html?desktop=1");
        }catch(Exception ex){
            Directory.CreateDirectory(OverlayPaths.Home);File.WriteAllText(Path.Combine(OverlayPaths.Home,"startup-error.txt"),ex.Message);
            Forms.MessageBox.Show("桌面歌词未能启动："+ex.Message,"Miku 桌面歌词");Close();
        }
    }
    public class RegionMessage{public string kind;public double width,height;public RegionBox[] rects;}
    public class RegionBox{public double x,y,w,h;}
    // Input is isolated into small windows covering only the visible controls.
    // A malformed or oversized DOM rectangle can never turn the desktop into a mouse blocker.
    sealed class InputProxy:Forms.Form
    {
        DesktopOverlay owner;DateTime lastMove=DateTime.MinValue;
        public InputProxy(DesktopOverlay owner){
            this.owner=owner;FormBorderStyle=Forms.FormBorderStyle.None;ShowInTaskbar=false;AutoScaleMode=Forms.AutoScaleMode.None;
            BackColor=System.Drawing.Color.Black;Opacity=1.0/255;Text="Miku 控件交互层";StartPosition=Forms.FormStartPosition.Manual;
            MouseMove+=delegate(object sender,Forms.MouseEventArgs e){if((DateTime.UtcNow-lastMove).TotalMilliseconds<25)return;lastMove=DateTime.UtcNow;owner.ForwardMouse("mouseMoved",PointToScreen(e.Location),Capture?"left":"none",0,0);};
            MouseDown+=delegate(object sender,Forms.MouseEventArgs e){if(e.Button!=Forms.MouseButtons.Left)return;Capture=true;owner.ForwardMouse("mousePressed",PointToScreen(e.Location),"left",e.Clicks,0);};
            MouseUp+=delegate(object sender,Forms.MouseEventArgs e){if(e.Button!=Forms.MouseButtons.Left)return;owner.ForwardMouse("mouseReleased",PointToScreen(e.Location),"left",1,0);Capture=false;};
            MouseWheel+=delegate(object sender,Forms.MouseEventArgs e){owner.ForwardMouse("mouseWheel",PointToScreen(e.Location),"none",0,-e.Delta);};
        }
        protected override bool ShowWithoutActivation{get{return true;}}
        protected override Forms.CreateParams CreateParams{
            get{Forms.CreateParams value=base.CreateParams;value.ExStyle|=WS_EX_TOOLWINDOW|WS_EX_NOACTIVATE;return value;}
        }
        protected override void WndProc(ref Forms.Message message){if(message.Msg==0x21){message.Result=new IntPtr(3);return;}base.WndProc(ref message);}
    }
    [StructLayout(LayoutKind.Sequential)]struct NativePoint{public int X,Y;}
    delegate bool EnumWindowsProc(IntPtr hwnd,IntPtr state);
    [DllImport("user32.dll")]static extern bool EnumWindows(EnumWindowsProc callback,IntPtr state);
    [DllImport("user32.dll",CharSet=CharSet.Unicode)]static extern IntPtr FindWindow(string className,string title);
    [DllImport("user32.dll",CharSet=CharSet.Unicode)]static extern IntPtr FindWindowEx(IntPtr parent,IntPtr after,string className,string title);
    [DllImport("user32.dll")]static extern bool IsWindowVisible(IntPtr window);
    [DllImport("user32.dll")]static extern bool SetWindowPos(IntPtr window,IntPtr after,int x,int y,int w,int h,uint flags);
    [DllImport("user32.dll")]static extern int GetWindowLong(IntPtr window,int index);
    [DllImport("user32.dll")]static extern int SetWindowLong(IntPtr window,int index,int value);
    [DllImport("user32.dll")]static extern bool GetCursorPos(out NativePoint point);
    [DllImport("user32.dll")]static extern bool PostMessage(IntPtr window,int message,IntPtr wParam,IntPtr lParam);

    [STAThread]public static void Main(string[] args)
    {
        IntPtr old=FindWindow(null,WindowTitle);
        if(old!=IntPtr.Zero){PostMessage(old,WM_SHOWLAYER,IntPtr.Zero,IntPtr.Zero);return;}
        try {
            using (var instance = new Mutex(false, @"Local\MikuWallpaperDesktopPlayer")) {
                bool owner;
                try { owner = instance.WaitOne(0); }
                catch (AbandonedMutexException) { owner = true; }
                if (!owner) return;
                try {
                    var app = new System.Windows.Application();
                    app.ShutdownMode = ShutdownMode.OnMainWindowClose;
                    app.Run(new DesktopOverlay());
                } finally { instance.ReleaseMutex(); }
            }
        }catch(Exception ex){
            SetupCore.Log("桌面播放器启动失败 · "+ex.Message);
            Forms.MessageBox.Show("桌面播放器启动失败："+ex.Message,WindowTitle);
        }
    }
}
