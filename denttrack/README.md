# DentTrack — Dental Patient Record System (Django Edition)

A clinic-wide dental patient record system: login + audit logging, an
interactive clickable tooth chart, patient records, and appointments — all
running on a shared SQLite database over your clinic's local network (LAN).

This is the Django rebuild of the original single-computer Tkinter version.
The data model and features are the same; the difference is that any
computer on the same Wi-Fi/Ethernet network can now open it in a browser.

---

## What's new: surface-level tooth charting

The tooth chart now draws real tooth shapes (different outlines for
incisors, canines, premolars, molars, and wisdom teeth, upper vs lower)
instead of plain colored rectangles, and each tooth is divided into 5
clinically-laid-out surfaces you can chart independently:

| Surface | Where it sits on the tooth |
|---|---|
| Mesial | Left third of the crown |
| Distal | Right third of the crown |
| Occlusal / Incisal | Center third (the biting surface) |
| Buccal | Outer rim around the whole crown |
| Lingual | Small inner core |

Drag a procedure icon from the palette onto any surface to chart it.
Whole-tooth procedures (crown, root canal, extraction, implant, bridge)
apply to all 5 surfaces at once and update the tooth's overall status —
an extracted tooth renders with a red X, matching the convention used by
commercial dental charting software.

This added one new database table (`ToothSurfaceRecord`) and one new
migration file. If you're pulling this update into an existing install,
just run `python manage.py migrate` as usual — your existing patient and
tooth data is untouched.

---

## 1. How this works on a LAN (read this first)

One computer (e.g. the front-desk PC) runs the Django **server**. Every
other computer/tablet/phone on the same network just opens a **browser**
and goes to that server's address — no installation needed on those other
machines.

```
                     ┌─────────────────────────┐
                     │   Server PC (runs        │
                     │   `python manage.py       │
                     │   runserver 0.0.0.0:8000`)│
                     │   dental_records.db lives │
                     │   here                    │
                     └────────────┬─────────────┘
                                   │  Wi-Fi / Ethernet (LAN)
            ┌──────────────────────┼──────────────────────┐
            │                      │                       │
   ┌────────▼───────┐    ┌─────────▼────────┐    ┌─────────▼────────┐
   │ Dentist Chair 1 │    │ Dentist Chair 2   │    │ Reception Desk    │
   │ (any browser)   │    │ (any browser)     │    │ (any browser)     │
   └─────────────────┘    └───────────────────┘    └────────────────────┘
```

SQLite is fine here because a small clinic (a handful of simultaneous
users, mostly reading, occasional writes) won't hit its concurrency limits.
If this ever grows into a multi-branch clinic with dozens of concurrent
users, the natural next step is switching `DATABASES` in `config/settings.py`
to PostgreSQL — everything else in the app stays the same.

---

## 2. First-time setup (on the server PC)

```bash
# 1. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create the database tables
python manage.py migrate

# 4. Create the default admin account (admin / admin123)
python manage.py seed_admin

# 5. Run the server, making it reachable from other computers on the LAN
python manage.py runserver 0.0.0.0:8000
```

Then on the **server PC itself**, open: `http://127.0.0.1:8000/`

> ⚠️ **Change the default password** after your first login — go to
> Settings → Change Password.

---

## 3. Connecting other computers on the clinic network

1. On the server PC, find its local IP address:
   - **Windows:** open Command Prompt → `ipconfig` → look for "IPv4 Address" (e.g. `192.168.1.50`)
   - **Mac/Linux:** open Terminal → `ifconfig` or `ip addr` → look for something like `192.168.1.50`

2. On any other computer/tablet connected to the **same Wi-Fi/router**, open a
   browser and go to:
   ```
   http://192.168.1.50:8000/
   ```
   (replace with the server PC's actual IP)

3. Keep the server PC's terminal window open and that computer turned on —
   if it sleeps, restarts, or you close the terminal, the server stops and
   other computers lose access until you restart it.

**Tip:** giving the server PC a fixed/reserved IP address in your router's
settings (sometimes called "DHCP reservation" or "static IP") means the
address won't change after a reboot, so the other computers can always use
the same URL.

---

## 4. Project structure

```
denttrack/
├── manage.py
├── requirements.txt
├── dental_records.db          ← created after running migrate (SQLite file)
├── config/                    ← Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── records/                   ← the actual app: models, views, forms
│   ├── models.py              ← Patient, ToothRecord, ToothSurfaceRecord,
│   │                             Appointment, AuditLog, StaffProfile
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py                ← registers everything in Django's built-in /admin/
│   ├── signals.py              ← auto-logs logins/logouts, auto-creates staff profiles
│   ├── tooth_shapes.py          ← generates the SVG tooth outlines + 5 surface zones
│   ├── migrations/              ← 0001_initial, 0002_toothsurfacerecord, ...
│   └── management/commands/seed_admin.py
├── templates/
│   ├── base.html               ← sidebar layout shared by every page
│   ├── registration/login.html
│   └── records/                ← dashboard, patient pages, tooth chart, etc.
└── static/css/style.css        ← same color theme as the original desktop app
```

---

## 5. Features

- **Login & roles** — admin / dentist / receptionist, with every login,
  failed login, and logout automatically recorded in the audit log
  (handled by Django's built-in auth signals in `records/signals.py`).
- **Interactive tooth chart** — anatomically-shaped SVG teeth (FDI numbering,
  upper/lower arches, correct crown shape per tooth type) instead of plain
  colored boxes. Each tooth is split into 5 clickable/droppable surfaces —
  mesial, distal, occlusal/incisal, buccal, lingual — laid out the way a
  real clinical chart shows them (mesial/distal as left/right thirds,
  occlusal as the center, buccal as the outer rim, lingual as the inner
  core). Drag a procedure (caries, filling, sealant, crown, root canal,
  extraction, implant, bridge, fracture, watch, clear) from the palette
  onto a tooth surface to chart it instantly — whole-tooth procedures like
  crowns or extractions apply to all 5 surfaces at once and update the
  tooth's overall status (e.g. extracted teeth render with a red X).
  Click a tooth (not a specific surface) to open a panel on the right
  showing its full surface-by-surface breakdown plus a free-text notes box,
  saved with AJAX so the chart doesn't fully reload.
- **Patient records** — add/edit/search/delete, with medical history and
  allergy fields, and a "Full Record" view with tabs for personal info,
  tooth summary, and appointment history.
- **Appointments** — schedule and list appointments per patient/dentist.
- **Audit log** — visible to admins only, lists every significant action
  with timestamp and the user who did it.
- **Django admin** — `/admin/` gives you a second, more powerful interface
  for bulk edits or troubleshooting (login with the same admin account).

---

## 6. Adding more dentists/staff

As an admin, go to **Settings → Add New Dentist**, or use the Django admin
at `/admin/` → Users (then assign a `StaffProfile` role if needed — this
happens automatically based on what you pick in the in-app form).

---

## 7. Backing up your data

Your entire clinic's data lives in one file: `dental_records.db`. To back
up, just copy that file somewhere safe (an external drive, cloud folder,
etc.) — ideally do this when the server isn't actively being written to,
or briefly stop the server first to avoid copying a half-written file.

---

## 8. Pushing this to GitHub

A `.gitignore` is included that excludes `venv/`, `__pycache__/`, and
`dental_records.db`. That last one matters most: the database file holds
real patient records once you start using the app, so it should never be
committed to a public (or even private) repo. Each clinic's `dental_records.db`
stays local to their server PC.

If you're publishing this for the first time:

```bash
git init
git add .
git commit -m "Initial commit: DentTrack Django edition"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

Anyone cloning the repo afterward follows section 2 above (`pip install -r
requirements.txt`, `python manage.py migrate`, `python manage.py seed_admin`)
to get a fresh, empty database and the default admin login — none of your
clinic's actual patient data is part of the repo.

---

## 9. Going beyond `runserver` (optional, for later)

`python manage.py runserver` is meant for development. It works fine for a
small clinic's daily use, but if you want something more robust (auto-restart
if it crashes, runs in the background without a visible terminal window),
the next step is running it behind a production WSGI server like **gunicorn**
or **waitress**, optionally with **nginx** in front. This is an optional
upgrade — not required to use the app today.
