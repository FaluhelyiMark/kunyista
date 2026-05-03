using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;

class Kunyista {
    static void Main() {
        string exeDir = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
        string pyFile = Path.Combine(exeDir, "kunyista.py");

        // Megkeresi a pythonw.exe-t
        string pythonw = FindPythonW();
        if (pythonw == null) {
            System.Windows.Forms.MessageBox.Show(
                "Nem található a Python telepítés.",
                "Kunyista",
                System.Windows.Forms.MessageBoxButtons.OK,
                System.Windows.Forms.MessageBoxIcon.Error
            );
            return;
        }

        ProcessStartInfo psi = new ProcessStartInfo();
        psi.FileName = pythonw;
        psi.Arguments = "\"" + pyFile + "\"";
        psi.WorkingDirectory = exeDir;
        psi.UseShellExecute = true;
        psi.Verb = "runas";

        try {
            Process.Start(psi);
        } catch (Exception) {
            // Felhasználó visszautasította - indítás admin nélkül
            psi.Verb = "";
            Process.Start(psi);
        }
    }

    static string FindPythonW() {
        // 1. Keresi a LOCAL telepített Python verziókat
        string localPy = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        string pyBase = Path.Combine(localPy, "Programs", "Python");
        if (Directory.Exists(pyBase)) {
            foreach (string dir in Directory.GetDirectories(pyBase)) {
                string exe = Path.Combine(dir, "pythonw.exe");
                if (File.Exists(exe)) return exe;
            }
        }

        // 2. Keresi a Program Files-ban
        foreach (string pf in new[] {
            Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles),
            Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86)
        }) {
            string pyDir = Path.Combine(pf, "Python312");
            string exe = Path.Combine(pyDir, "pythonw.exe");
            if (File.Exists(exe)) return exe;
        }

        // 3. PATH-ban keresi
        foreach (string p in Environment.GetEnvironmentVariable("PATH").Split(';')) {
            try {
                string exe = Path.Combine(p.Trim(), "pythonw.exe");
                if (File.Exists(exe)) return exe;
            } catch { }
        }

        return null;
    }
}
