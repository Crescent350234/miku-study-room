using System;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

internal sealed class PlayerPresence : IDisposable
{
    private readonly TcpListener listener;
    private volatile bool disposed;
    internal volatile bool Active;

    internal int Port { get; private set; }

    internal PlayerPresence() : this(Bind) { }

    internal PlayerPresence(Func<int, TcpListener> bind)
    {
        foreach (int port in new[] { 51802, 52802, 53802, 54802, 45802 })
        {
            try
            {
                listener = bind(port);
                Port = port;
                break;
            }
            catch (SocketException) { }
        }
        if (listener == null) return;
        var thread = new Thread(Listen) { IsBackground = true, Name = "Miku player status" };
        thread.Start();
    }

    private static TcpListener Bind(int port)
    {
        var candidate = new TcpListener(IPAddress.Loopback, port);
        try
        {
            candidate.ExclusiveAddressUse = true;
            candidate.Start();
            return candidate;
        }
        catch (SocketException)
        {
            candidate.Stop();
            throw;
        }
    }

    private void Listen()
    {
        while (!disposed)
        {
            TcpClient client;
            try { client = listener.AcceptTcpClient(); }
            catch (SocketException) { return; }
            catch (ObjectDisposedException) { return; }
            using (client)
            {
                client.ReceiveTimeout = 250;
                client.SendTimeout = 250;
                try { Reply(client.GetStream()); }
                catch (IOException) { }
                catch (SocketException) { }
            }
        }
    }

    private void Reply(NetworkStream stream)
    {
        var request = new byte[4096];
        int length = 0;
        while (length < request.Length)
        {
            int received = stream.Read(request, length, request.Length - length);
            if (received == 0) return;
            length += received;
            string headers = Encoding.ASCII.GetString(request, 0, length);
            if (!headers.Contains("\r\n\r\n")) continue;
            string[] line = headers.Substring(0, headers.IndexOf("\r\n", StringComparison.Ordinal)).Split(' ');
            bool validPath = line.Length == 3 && line[1] == "/player-status";
            bool get = validPath && line[0] == "GET";
            bool options = validPath && line[0] == "OPTIONS";
            string status = get ? "200 OK" : options ? "204 No Content" : "404 Not Found";
            string body = get ? (Active ? "miku-player-1:active" : "miku-player-1:inactive") : "";
            string reply = "HTTP/1.1 " + status + "\r\nConnection: close\r\nContent-Type: text/plain\r\n" +
                "Access-Control-Allow-Origin: *\r\nAccess-Control-Allow-Methods: GET, OPTIONS\r\n" +
                "Access-Control-Allow-Private-Network: true\r\nCache-Control: no-store\r\nContent-Length: " + body.Length + "\r\n\r\n" + body;
            byte[] bytes = Encoding.ASCII.GetBytes(reply);
            stream.Write(bytes, 0, bytes.Length);
            return;
        }
    }

    public void Dispose()
    {
        Active = false;
        disposed = true;
        if (listener != null) listener.Stop();
    }
}
