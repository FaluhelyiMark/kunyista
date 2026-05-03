# ⚙ Kunyista — Windows Optimalizáló

Egy egyszerű, ingyenes Windows tweaker alkalmazás Python + Tkinter alapon.

## 📦 Telepítés

1. Töltsd le az `install.bat` fájlt
2. Futtasd **jobb klikk → Futtatás rendszergazdaként**
3. A telepítő automatikusan:
   - Telepíti a Pythont (ha nincs fent)
   - Letölti a `kunyista.py` fájlt erről a repo-ból
   - Létrehoz egy asztali parancsikont

## 🔧 Funkciók

| Kategória | Tweakek |
|-----------|---------|
| Teljesítmény | Vizuális effektek, hibernálás, energiaséma, SSD TRIM |
| Adatvédelem | Telemetria, reklám-azonosító, helymeghatározás, Cortana |
| Rendszer | Billentyűzet-layout, fájlkiterjesztések, tálca, rejtett fájlok |

## ⚠️ Megjegyzések

- Egyes tweakek **rendszergazdai jogosultságot** igényelnek
- Az alkalmazás indításkor automatikusan kéri a jogosultságot
- Minden tweak visszaállítható a „Visszaállítás" gombbal

## 🛠 Manuális futtatás

```bash
python kunyista.py
```

## 📁 Fájlstruktúra

```
kunyista/
├── kunyista.py      ← a fő alkalmazás
├── install.bat      ← telepítő szkript
├── requirements.txt ← Python függőségek
└── README.md
```
