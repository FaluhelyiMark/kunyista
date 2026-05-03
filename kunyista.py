import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import sys
import ctypes
import threading

# ── Admin check ──────────────────────────────────────────────────────────────
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

# ── Registry / PowerShell helpers ────────────────────────────────────────────
def run_ps(command, desc=""):
    """Run a PowerShell command silently."""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
            capture_output=True, text=True
        )
        return result.returncode == 0
    except Exception as e:
        return False

def run_reg(args):
    try:
        result = subprocess.run(["reg"] + args, capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

# ── Tweaks definition ─────────────────────────────────────────────────────────
TWEAKS = {
    "Teljesítmény": [
        {
            "name": "Vizuális effektek kikapcsolása",
            "desc": "Kikapcsolja az animációkat és átlátszóságokat a gyorsabb reakcióidőért.",
            "apply": lambda: run_reg(["ADD", r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
                                      "/v", "VisualFXSetting", "/t", "REG_DWORD", "/d", "2", "/f"]),
            "undo":  lambda: run_reg(["ADD", r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
                                      "/v", "VisualFXSetting", "/t", "REG_DWORD", "/d", "0", "/f"]),
        },
        {
            "name": "Hibernálás letiltása",
            "desc": "Letiltja a hibernálást és felszabadítja a hiberfil.sys helyet.",
            "apply": lambda: run_ps("powercfg /hibernate off"),
            "undo":  lambda: run_ps("powercfg /hibernate on"),
        },
        {
            "name": "Nagy teljesítményű energiaséma",
            "desc": "Beállítja a Nagy teljesítményű energiasémát.",
            "apply": lambda: run_ps("powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"),
            "undo":  lambda: run_ps("powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e"),
        },
        {
            "name": "SSD TRIM ütemező engedélyezése",
            "desc": "Engedélyezi az automatikus TRIM-et SSD meghajtókhoz.",
            "apply": lambda: run_ps("fsutil behavior set DisableDeleteNotify 0"),
            "undo":  lambda: run_ps("fsutil behavior set DisableDeleteNotify 1"),
        },
    ],
    "Adatvédelem": [
        {
            "name": "Telemetria letiltása",
            "desc": "Leállítja a DiagTrack (Connected User Experiences) szolgáltatást.",
            "apply": lambda: run_ps("Stop-Service DiagTrack; Set-Service DiagTrack -StartupType Disabled"),
            "undo":  lambda: run_ps("Set-Service DiagTrack -StartupType Automatic; Start-Service DiagTrack"),
        },
        {
            "name": "Reklám-azonosító letiltása",
            "desc": "Letiltja a hirdetési azonosítót az alkalmazásokban.",
            "apply": lambda: run_reg(["ADD", r"HKCU\Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo",
                                      "/v", "Enabled", "/t", "REG_DWORD", "/d", "0", "/f"]),
            "undo":  lambda: run_reg(["ADD", r"HKCU\Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo",
                                      "/v", "Enabled", "/t", "REG_DWORD", "/d", "1", "/f"]),
        },
        {
            "name": "Helymeghatározás letiltása",
            "desc": "Letiltja a rendszerszintű helymeghatározási szolgáltatást.",
            "apply": lambda: run_ps("Stop-Service lfsvc; Set-Service lfsvc -StartupType Disabled"),
            "undo":  lambda: run_ps("Set-Service lfsvc -StartupType Manual; Start-Service lfsvc"),
        },
        {
            "name": "Cortana letiltása",
            "desc": "Letiltja a Cortana keresési asszisztenst.",
            "apply": lambda: run_reg(["ADD", r"HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search",
                                      "/v", "AllowCortana", "/t", "REG_DWORD", "/d", "0", "/f"]),
            "undo":  lambda: run_reg(["DELETE", r"HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search",
                                      "/v", "AllowCortana", "/f"]),
        },
    ],
    "Rendszer": [
        {
            "name": "Gyorsbillentyűs váltás letiltása",
            "desc": "Letiltja a véletlenszerű billentyűzet-layout váltást (Ctrl+Shift).",
            "apply": lambda: run_reg(["ADD", r"HKCU\Keyboard Layout\Toggle",
                                      "/v", "Language Hotkey", "/t", "REG_SZ", "/d", "3", "/f"]),
            "undo":  lambda: run_reg(["ADD", r"HKCU\Keyboard Layout\Toggle",
                                      "/v", "Language Hotkey", "/t", "REG_SZ", "/d", "1", "/f"]),
        },
        {
            "name": "Fájlkiterjesztések megjelenítése",
            "desc": "Megjeleníti a fájlok kiterjesztéseit az Intézőben.",
            "apply": lambda: run_reg(["ADD", r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                                      "/v", "HideFileExt", "/t", "REG_DWORD", "/d", "0", "/f"]),
            "undo":  lambda: run_reg(["ADD", r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                                      "/v", "HideFileExt", "/t", "REG_DWORD", "/d", "1", "/f"]),
        },
        {
            "name": "Tálca kis ikonok módja",
            "desc": "Kis ikonokat jelenít meg a tálcán, több helyet adva.",
            "apply": lambda: run_reg(["ADD", r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                                      "/v", "TaskbarSmallIcons", "/t", "REG_DWORD", "/d", "1", "/f"]),
            "undo":  lambda: run_reg(["ADD", r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                                      "/v", "TaskbarSmallIcons", "/t", "REG_DWORD", "/d", "0", "/f"]),
        },
        {
            "name": "Rejtett fájlok megjelenítése",
            "desc": "Megjeleníti a rejtett fájlokat és mappákat az Intézőben.",
            "apply": lambda: run_reg(["ADD", r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                                      "/v", "Hidden", "/t", "REG_DWORD", "/d", "1", "/f"]),
            "undo":  lambda: run_reg(["ADD", r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                                      "/v", "Hidden", "/t", "REG_DWORD", "/d", "2", "/f"]),
        },
    ],
}

# ── GUI ───────────────────────────────────────────────────────────────────────
class KunyistaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kunyista")
        self.geometry("820x600")
        self.minsize(700, 500)
        self.configure(bg="#0f0f0f")
        self.resizable(True, True)

        self._tweak_vars = {}   # name -> BooleanVar
        self._tweak_map  = {}   # name -> tweak dict
        self._status_var = tk.StringVar(value="Készen áll.")

        self._build_ui()

    # ── Layout ─────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg="#111111", height=64)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="⚙  KUNYISTA", font=("Consolas", 20, "bold"),
                 fg="#e0ff00", bg="#111111").pack(side="left", padx=24, pady=14)
        tk.Label(header, text="Windows Optimalizáló", font=("Consolas", 10),
                 fg="#555555", bg="#111111").pack(side="left", pady=14)

        admin_text = "✔ Rendszergazda" if is_admin() else "✘ Nem rendszergazda  –  egyes tweakek nem működnek"
        admin_color = "#4cff91" if is_admin() else "#ff4c4c"
        tk.Label(header, text=admin_text, font=("Consolas", 9),
                 fg=admin_color, bg="#111111").pack(side="right", padx=20)

        # Body
        body = tk.Frame(self, bg="#0f0f0f")
        body.pack(fill="both", expand=True)

        # Sidebar – kategóriák
        sidebar = tk.Frame(body, bg="#111111", width=180)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="KATEGóRIÁK", font=("Consolas", 8, "bold"),
                 fg="#333333", bg="#111111").pack(anchor="w", padx=16, pady=(16, 4))

        self._cat_buttons = {}
        self._active_cat = tk.StringVar()
        first_cat = list(TWEAKS.keys())[0]
        self._active_cat.set(first_cat)

        for cat in TWEAKS:
            btn = tk.Button(sidebar, text=cat, font=("Consolas", 11),
                            bg="#111111", fg="#aaaaaa", bd=0, cursor="hand2",
                            activebackground="#1a1a1a", activeforeground="#e0ff00",
                            anchor="w", padx=16, pady=8,
                            command=lambda c=cat: self._show_category(c))
            btn.pack(fill="x")
            self._cat_buttons[cat] = btn

        # Divider
        tk.Frame(body, bg="#222222", width=1).pack(side="left", fill="y")

        # Content area
        content = tk.Frame(body, bg="#0f0f0f")
        content.pack(side="left", fill="both", expand=True)

        # Tweaks list (scrollable)
        list_outer = tk.Frame(content, bg="#0f0f0f")
        list_outer.pack(fill="both", expand=True, padx=0, pady=0)

        canvas = tk.Canvas(list_outer, bg="#0f0f0f", highlightthickness=0)
        scrollbar = tk.Scrollbar(list_outer, orient="vertical", command=canvas.yview)
        self._tweak_frame = tk.Frame(canvas, bg="#0f0f0f")

        self._tweak_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=self._tweak_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bottom bar
        bottom = tk.Frame(self, bg="#111111", height=48)
        bottom.pack(fill="x", side="bottom")
        bottom.pack_propagate(False)

        self._select_all_btn = tk.Button(
            bottom, text="Összes kijelölése", font=("Consolas", 9),
            bg="#1e1e1e", fg="#aaaaaa", bd=0, cursor="hand2",
            activebackground="#2a2a2a", activeforeground="#ffffff",
            padx=12, pady=6, command=self._select_all
        )
        self._select_all_btn.pack(side="left", padx=12, pady=8)

        tk.Button(
            bottom, text="Visszaállítás", font=("Consolas", 9),
            bg="#1e1e1e", fg="#ff6b6b", bd=0, cursor="hand2",
            activebackground="#2a2a2a", activeforeground="#ff4444",
            padx=12, pady=6, command=self._undo_selected
        ).pack(side="left", padx=4, pady=8)

        tk.Button(
            bottom, text="⚡  Alkalmazás", font=("Consolas", 10, "bold"),
            bg="#e0ff00", fg="#000000", bd=0, cursor="hand2",
            activebackground="#c8e600", activeforeground="#000000",
            padx=18, pady=6, command=self._apply_selected
        ).pack(side="right", padx=16, pady=8)

        tk.Label(bottom, textvariable=self._status_var, font=("Consolas", 9),
                 fg="#444444", bg="#111111").pack(side="right", padx=12)

        # Show first category
        self._show_category(first_cat)

    def _show_category(self, cat):
        self._active_cat.set(cat)
        # Update sidebar button styles
        for c, btn in self._cat_buttons.items():
            if c == cat:
                btn.configure(fg="#e0ff00", bg="#1a1a1a")
            else:
                btn.configure(fg="#aaaaaa", bg="#111111")

        # Clear tweak list
        for w in self._tweak_frame.winfo_children():
            w.destroy()

        tweaks = TWEAKS.get(cat, [])
        for i, tweak in enumerate(tweaks):
            name = tweak["name"]
            if name not in self._tweak_vars:
                self._tweak_vars[name] = tk.BooleanVar(value=False)
            self._tweak_map[name] = tweak

            row = tk.Frame(self._tweak_frame, bg="#0f0f0f")
            row.pack(fill="x", padx=24, pady=6)

            # Checkbox
            cb = tk.Checkbutton(row, variable=self._tweak_vars[name],
                                 bg="#0f0f0f", activebackground="#0f0f0f",
                                 selectcolor="#1a1a1a", fg="#e0ff00",
                                 cursor="hand2")
            cb.pack(side="left")

            # Text block
            text_block = tk.Frame(row, bg="#0f0f0f")
            text_block.pack(side="left", fill="x", expand=True, padx=8)

            tk.Label(text_block, text=name, font=("Consolas", 11, "bold"),
                     fg="#eeeeee", bg="#0f0f0f", anchor="w").pack(anchor="w")
            tk.Label(text_block, text=tweak["desc"], font=("Consolas", 9),
                     fg="#555555", bg="#0f0f0f", anchor="w",
                     wraplength=520, justify="left").pack(anchor="w")

            # Separator
            if i < len(tweaks) - 1:
                tk.Frame(self._tweak_frame, bg="#1a1a1a", height=1).pack(
                    fill="x", padx=24, pady=0)

    def _select_all(self):
        cat = self._active_cat.get()
        tweaks = TWEAKS.get(cat, [])
        any_unchecked = any(not self._tweak_vars[t["name"]].get() for t in tweaks
                            if t["name"] in self._tweak_vars)
        for t in tweaks:
            if t["name"] in self._tweak_vars:
                self._tweak_vars[t["name"]].set(any_unchecked)

    def _get_selected(self):
        return [name for name, var in self._tweak_vars.items() if var.get()]

    def _apply_selected(self):
        selected = self._get_selected()
        if not selected:
            messagebox.showinfo("Kunyista", "Jelölj ki legalább egy tweaket!")
            return
        if not messagebox.askyesno("Megerősítés",
                f"{len(selected)} tweak alkalmazása?\n\n" + "\n".join(f"• {n}" for n in selected)):
            return
        self._run_in_thread(selected, mode="apply")

    def _undo_selected(self):
        selected = self._get_selected()
        if not selected:
            messagebox.showinfo("Kunyista", "Jelölj ki legalább egy tweaket!")
            return
        if not messagebox.askyesno("Visszaállítás",
                f"{len(selected)} tweak visszaállítása?\n\n" + "\n".join(f"• {n}" for n in selected)):
            return
        self._run_in_thread(selected, mode="undo")

    def _run_in_thread(self, names, mode):
        def task():
            ok = 0
            fail = 0
            for name in names:
                self._status_var.set(f"{'Alkalmazás' if mode=='apply' else 'Visszaállítás'}: {name}…")
                tweak = self._tweak_map.get(name)
                if tweak:
                    fn = tweak["apply"] if mode == "apply" else tweak["undo"]
                    success = fn()
                    if success:
                        ok += 1
                    else:
                        fail += 1
            action = "alkalmazva" if mode == "apply" else "visszaállítva"
            msg = f"Kész! {ok} tweak {action}."
            if fail:
                msg += f"  ({fail} nem sikerült – rendszergazdai jogosultság szükséges?)"
            self._status_var.set(msg)
        threading.Thread(target=task, daemon=True).start()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not is_admin():
        answer = ctypes.windll.user32.MessageBoxW(
            0,
            "A Kunyista rendszergazdai jogosultságot igényel a legtöbb tweakhez.\n\n"
            "Újraindítod rendszergazdaként?",
            "Kunyista – Jogosultság",
            0x24  # MB_YESNO | MB_ICONQUESTION
        )
        if answer == 6:  # IDYES
            run_as_admin()
    app = KunyistaApp()
    app.mainloop()
