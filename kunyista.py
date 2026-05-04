import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import os
import sys
import ctypes
import shutil

# ── Admin check ───────────────────────────────────────────────
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit()

def run_ps(cmd):
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd],
            capture_output=True, text=True
        )
        return r.stdout.strip()
    except:
        return ""

# ── Funkciók ──────────────────────────────────────────────────
BLOATWARE = [
    "Microsoft.BingNews",
    "Microsoft.BingWeather",
    "Microsoft.GetHelp",
    "Microsoft.Getstarted",
    "Microsoft.MicrosoftOfficeHub",
    "Microsoft.MicrosoftSolitaireCollection",
    "Microsoft.PowerAutomateDesktop",
    "Microsoft.SecHealthUI",
    "Microsoft.People",
    "Microsoft.Todos",
    "Microsoft.WindowsAlarms",
    "Microsoft.WindowsCamera",
    "microsoft.windowscommunicationsapps",
    "Microsoft.WindowsFeedbackHub",
    "Microsoft.WindowsMaps",
    "Microsoft.WindowsSoundRecorder",
    "Microsoft.YourPhone",
    "Microsoft.ZuneMusic",
    "Microsoft.ZuneVideo",
    "MicrosoftTeams",
]

def debloat(status_var, btn):
    def task():
        btn.config(state="disabled")
        removed = 0
        for app in BLOATWARE:
            status_var.set(f"Eltávolítás: {app}...")
            run_ps(f"Get-AppxPackage *{app}* | Remove-AppxPackage -ErrorAction SilentlyContinue")
            run_ps(f"Get-AppxProvisionedPackage -Online | Where-Object DisplayName -like '*{app}*' | Remove-ProvisionedAppxPackage -Online -ErrorAction SilentlyContinue")
            removed += 1
        status_var.set(f"✔ Debloat kész! {removed} alkalmazás eltávolítva.")
        btn.config(state="normal")
    threading.Thread(target=task, daemon=True).start()

def disable_ads(status_var, btn):
    def task():
        btn.config(state="disabled")
        status_var.set("Reklámok letiltása...")
        cmds = [
            'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager" -Name "SubscribedContent-338389Enabled" -Value 0',
            'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager" -Name "SubscribedContent-353694Enabled" -Value 0',
            'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager" -Name "SubscribedContent-353696Enabled" -Value 0',
            'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager" -Name "SilentInstalledAppsEnabled" -Value 0',
            'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager" -Name "SystemPaneSuggestionsEnabled" -Value 0',
            'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo" /v Enabled /t REG_DWORD /d 0 /f',
        ]
        for cmd in cmds:
            run_ps(cmd)
        status_var.set("✔ Reklámok letiltva!")
        btn.config(state="normal")
    threading.Thread(target=task, daemon=True).start()

def disable_telemetry(status_var, btn):
    def task():
        btn.config(state="disabled")
        status_var.set("Telemetria letiltása...")
        cmds = [
            'Stop-Service DiagTrack -ErrorAction SilentlyContinue; Set-Service DiagTrack -StartupType Disabled',
            'Stop-Service dmwappushservice -ErrorAction SilentlyContinue; Set-Service dmwappushservice -StartupType Disabled',
            'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f',
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f',
        ]
        for cmd in cmds:
            run_ps(cmd)
        status_var.set("✔ Telemetria letiltva!")
        btn.config(state="normal")
    threading.Thread(target=task, daemon=True).start()

def remove_cortana(status_var, btn):
    def task():
        btn.config(state="disabled")
        status_var.set("Cortana eltávolítása...")
        run_ps("Get-AppxPackage -allusers Microsoft.549981C3F5F10 | Remove-AppxPackage -ErrorAction SilentlyContinue")
        run_ps('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search" /v AllowCortana /t REG_DWORD /d 0 /f')
        status_var.set("✔ Cortana eltávolítva!")
        btn.config(state="normal")
    threading.Thread(target=task, daemon=True).start()

def ultimate_power(status_var, btn):
    def task():
        btn.config(state="disabled")
        status_var.set("Ultimate energiaséma bekapcsolása...")
        run_ps("powercfg /duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61")
        out = run_ps("powercfg /list")
        guid = None
        for line in out.splitlines():
            if "Ultimate" in line or "e9a42b02" in line.lower():
                parts = line.split()
                for p in parts:
                    if len(p) == 36 and p.count("-") == 4:
                        guid = p
                        break
        if guid:
            run_ps(f"powercfg /setactive {guid}")
            status_var.set("✔ Ultimate energiaséma bekapcsolva!")
        else:
            run_ps("powercfg /setactive e9a42b02-d5df-448d-aa00-03f14749eb61")
            status_var.set("✔ Ultimate energiaséma bekapcsolva!")
        btn.config(state="normal")
    threading.Thread(target=task, daemon=True).start()

def delete_temp(status_var, btn):
    def task():
        btn.config(state="disabled")
        status_var.set("Ideiglenes fájlok törlése...")
        count = 0
        dirs = [
            os.environ.get("TEMP", ""),
            os.environ.get("TMP", ""),
            os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Temp"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp"),
        ]
        for d in dirs:
            if not d or not os.path.exists(d):
                continue
            for item in os.listdir(d):
                item_path = os.path.join(d, item)
                try:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                        count += 1
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path, ignore_errors=True)
                        count += 1
                except:
                    pass
        status_var.set(f"✔ {count} ideiglenes fájl törölve!")
        btn.config(state="normal")
    threading.Thread(target=task, daemon=True).start()

# ── GUI ───────────────────────────────────────────────────────
class KunyistaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kunyista")
        self.geometry("520x420")
        self.resizable(False, False)
        self.configure(bg="#0f0f0f")
        self._status = tk.StringVar(value="Készen áll.")
        self._build_ui()

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg="#111111", height=60)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="⚙  KUNYISTA", font=("Consolas", 18, "bold"),
                 fg="#e0ff00", bg="#111111").pack(side="left", padx=20, pady=12)
        tk.Label(hdr, text="Windows Optimalizáló", font=("Consolas", 9),
                 fg="#444444", bg="#111111").pack(side="left", pady=12)

        # Gombok
        content = tk.Frame(self, bg="#0f0f0f")
        content.pack(fill="both", expand=True, padx=30, pady=20)

        self._make_btn(content, "🧹  Debloat",
            "Eltávolítja a felesleges beépített Windows alkalmazásokat.",
            lambda b: debloat(self._status, b))

        self._make_btn(content, "🚫  Disable Ads",
            "Letiltja a Windows reklámokat és ajánlásokat.",
            lambda b: disable_ads(self._status, b))

        self._make_btn(content, "📡  Disable Telemetry",
            "Letiltja az adatgyűjtő és telemetria szolgáltatásokat.",
            lambda b: disable_telemetry(self._status, b))

        self._make_btn(content, "🔇  Remove Cortana",
            "Eltávolítja a Cortana asszisztenst.",
            lambda b: remove_cortana(self._status, b))

        self._make_btn(content, "⚡  Enable Ultimate Power Plan",
            "Bekapcsolja a maximális teljesítményű energiasémát.",
            lambda b: ultimate_power(self._status, b))

        self._make_btn(content, "🗑  Delete Temporary Files",
            "Törli az ideiglenes fájlokat a TEMP mappákból.",
            lambda b: delete_temp(self._status, b))

        # Státuszsor
        status_bar = tk.Frame(self, bg="#111111", height=32)
        status_bar.pack(fill="x", side="bottom")
        status_bar.pack_propagate(False)
        tk.Label(status_bar, textvariable=self._status, font=("Consolas", 9),
                 fg="#555555", bg="#111111").pack(side="left", padx=14, pady=6)

    def _make_btn(self, parent, text, desc, cmd):
        frame = tk.Frame(parent, bg="#0f0f0f")
        frame.pack(fill="x", pady=4)

        btn = tk.Button(
            frame, text=text, font=("Consolas", 10, "bold"),
            bg="#1a1a1a", fg="#e0ff00", bd=0, cursor="hand2",
            activebackground="#e0ff00", activeforeground="#000000",
            anchor="w", padx=16, pady=8, width=28
        )
        btn.config(command=lambda b=btn: cmd(b))
        btn.pack(side="left")

        tk.Label(frame, text=desc, font=("Consolas", 8),
                 fg="#444444", bg="#0f0f0f", anchor="w").pack(side="left", padx=12)

# ── Entry point ───────────────────────────────────────────────
if __name__ == "__main__":
    app = KunyistaApp()
    app.mainloop()
