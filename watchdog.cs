using System;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

class Watchdog
{
    static string dir = AppDomain.CurrentDomain.BaseDirectory;
    static string exe = Path.Combine(dir, "bridge.exe");

    static void Main()
    {
        var t = new Thread(Listen);
        t.IsBackground = true;
        t.Start();

        int fails = 0;
        while (true)
        {
            bool ok = false;
            int[] ports = { 51789, 52789, 53789, 54789 };
            foreach (int port in ports)
            {
                try
                {
                    var req = (HttpWebRequest)WebRequest.Create("http://127.0.0.1:" + port + "/now.json");
                    req.Timeout = 2500;
                    using (var resp = (HttpWebResponse)req.GetResponse())
                    {
                        if (resp.StatusCode == HttpStatusCode.OK) { ok = true; break; }
                    }
                }
                catch { }
            }

            if (ok) fails = 0;
            else
            {
                fails++;
                if (fails >= 3) { RestartBridge(); fails = 0; }
            }

            Thread.Sleep(10000);
        }
    }

    static void RestartBridge()
    {
        try
        {
            foreach (var p in Process.GetProcessesByName("bridge"))
            {
                try { p.Kill(); } catch { }
            }
        }
        catch { }

        Thread.Sleep(600);

        if (!File.Exists(exe)) return;
        try
        {
            Process.Start(new ProcessStartInfo
            {
                FileName = exe,
                WorkingDirectory = dir,
                UseShellExecute = true,
                WindowStyle = ProcessWindowStyle.Hidden
            });
        }
        catch { }
    }

    static void Listen()
    {
        try
        {
            var srv = new TcpListener(IPAddress.Loopback, 51790);
            srv.Start();
            while (true)
            {
                var cli = srv.AcceptTcpClient();
                try
                {
                    using (cli)
                    using (var ns = cli.GetStream())
                    {
                        var buf = new byte[2048];
                        int n = ns.Read(buf, 0, buf.Length);
                        string req = Encoding.ASCII.GetString(buf, 0, n);

                        string origin = Hdr(req, "Origin");
                        string referer = Hdr(req, "Referer");
                        bool blockedOrigin = false;
                        if (!string.IsNullOrEmpty(origin))
                        {
                            string o = origin.ToLowerInvariant();
                            if (o != "null" && !o.StartsWith("file:")) blockedOrigin = true;
                        }
                        else if (!string.IsNullOrEmpty(referer))
                        {
                            string rf = referer.ToLowerInvariant();
                            if (rf.StartsWith("http://") || rf.StartsWith("https://")) blockedOrigin = true;
                        }
                        if (blockedOrigin)
                        {
                            Write(ns, "HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\nConnection: close\r\n\r\n");
                            continue;
                        }

                        if (req.StartsWith("OPTIONS"))
                        {
                            Write(ns, "HTTP/1.1 204 No Content\r\nAccess-Control-Allow-Origin: " + (string.IsNullOrEmpty(origin) ? "null" : origin) + "\r\nAccess-Control-Allow-Methods: GET, POST, OPTIONS\r\nAccess-Control-Allow-Private-Network: true\r\nContent-Length: 0\r\n\r\n");
                        }
                        else if (req.IndexOf("/restart") >= 0)
                        {
                            RestartBridge();
                            Write(ns, "HTTP/1.1 200 OK\r\nAccess-Control-Allow-Origin: " + (string.IsNullOrEmpty(origin) ? "null" : origin) + "\r\nContent-Type: text/plain\r\nContent-Length: 2\r\n\r\nok");
                        }
                        else
                        {
                            Write(ns, "HTTP/1.1 200 OK\r\nAccess-Control-Allow-Origin: " + (string.IsNullOrEmpty(origin) ? "null" : origin) + "\r\nContent-Type: text/plain\r\nContent-Length: 8\r\n\r\nwatchdog");
                        }
                    }
                }
                catch { }
            }
        }
        catch { }
    }


    static string Hdr(string req, string name)
    {
        foreach (string line in req.Split('\n'))
        {
            int c = line.IndexOf(':');
            if (c <= 0) continue;
            if (line.Substring(0, c).Trim().Equals(name, StringComparison.OrdinalIgnoreCase))
                return line.Substring(c + 1).Trim();
        }
        return null;
    }

    static void Write(NetworkStream ns, string s)
    {
        var b = Encoding.ASCII.GetBytes(s);
        ns.Write(b, 0, b.Length);
        ns.Flush();
    }
}
