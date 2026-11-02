import io

p = r"D:\MikuWallpaper\bridge\bridge.cs"
t = io.open(p, encoding="utf-8").read()

t = t.replace("private const int Port = 51789;",
              "private static int Port = 51789;\n    private static readonly int[] PortCandidates = { 51789, 52789, 53789, 54789 };")

old = """            TcpListener listener;
            try
            {
                listener = new TcpListener(IPAddress.Loopback, Port);
                listener.Start();
            }
            catch
            {
                return;
            }"""

new = """            TcpListener listener = null;
            foreach (int candidate in PortCandidates)
            {
                try
                {
                    var probe = new TcpListener(IPAddress.Loopback, candidate);
                    probe.Start();
                    listener = probe;
                    Port = candidate;
                    break;
                }
                catch { }
            }
            if (listener == null) return;

            try
            {
                File.WriteAllText(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "port.txt"), Port.ToString());
            }
            catch { }"""

if old not in t:
    raise SystemExit("listener anchor miss")

t = t.replace(old, new)
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("bridge patched")
