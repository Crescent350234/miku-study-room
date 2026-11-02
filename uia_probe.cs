using System;
using System.Diagnostics;
using System.Linq;
using System.Windows.Automation;

class Probe
{
    [STAThread]
    static void Main()
    {
        try
        {
            var pids = Process.GetProcessesByName("cloudmusic").Select(x => x.Id).ToArray();
            Console.WriteLine("cloudmusic pids: " + string.Join(",", pids));

            var wins = AutomationElement.RootElement.FindAll(TreeScope.Children, Condition.TrueCondition);
            AutomationElement root = null;
            foreach (AutomationElement w in wins)
            {
                var name = w.Current.Name ?? "";
                if (pids.Contains(w.Current.ProcessId) && name.Length > 0)
                {
                    Console.WriteLine("win: [" + name + "] pid=" + w.Current.ProcessId);
                    if (root == null) root = w;
                }
            }
            if (root == null) { Console.WriteLine("no root"); return; }

            var sliders = root.FindAll(TreeScope.Descendants,
                new PropertyCondition(AutomationElement.ControlTypeProperty, ControlType.Slider));
            Console.WriteLine("sliders: " + sliders.Count);
            foreach (AutomationElement s in sliders)
            {
                string val = "";
                try { val = ((ValuePattern)s.GetCurrentPattern(ValuePattern.Pattern)).Current.Value; } catch { }
                Console.WriteLine("  slider name=[" + s.Current.Name + "] value=" + val);
            }

            var buttons = root.FindAll(TreeScope.Descendants,
                new PropertyCondition(AutomationElement.ControlTypeProperty, ControlType.Button));
            Console.WriteLine("buttons: " + buttons.Count);
            foreach (AutomationElement b in buttons)
            {
                var n = b.Current.Name;
                if (string.IsNullOrEmpty(n)) continue;
                if (n.Contains("播放") || n.Contains("暂停") || n.Contains("下一") || n.Contains("上一"))
                    Console.WriteLine("  button [" + n + "] enabled=" + b.Current.IsEnabled);
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("ERR " + ex.GetType().Name + " " + ex.Message);
        }
    }
}
