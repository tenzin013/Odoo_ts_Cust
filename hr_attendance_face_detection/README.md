# HR Attendance Face Detection
### Odoo 18 Community — Custom Module

Contactless, AI-driven attendance with **Face Recognition** + **GPS Geofencing**.

---

## Features

| Feature | Description |
|---|---|
| 🎭 Face Recognition Check-In/Out | Webcam-based attendance marking |
| 📍 GPS Geofencing | Multi-location radius enforcement |
| 🖥️ Kiosk Mode | Full-screen shared terminal at `/hr_attendance_face/kiosk` |
| 📸 Snapshot Audit Trail | Stores webcam captures with each record |
| ⚙️ Configurable Tolerance | Tune recognition threshold (0.40–0.65) |
| 🕛 Auto Check-Out | Midnight cron closes open records |
| 🏢 Multi-Company | Location rules respect company boundaries |

---

## Requirements

### Python packages (install on the Odoo server)

```bash
pip install face_recognition numpy Pillow
```

> `face_recognition` depends on `dlib`. On Ubuntu/Debian:
> ```bash
> sudo apt-get install build-essential cmake libopenblas-dev liblapack-dev
> pip install dlib face_recognition numpy Pillow
> ```

### Odoo dependencies
- `hr_attendance` (core Community module)
- `hr`
- `web`

---

## Installation

1. Copy the `hr_attendance_face_detection` folder into your Odoo **custom addons** directory.
2. Restart the Odoo service.
3. In the Odoo backend: **Apps → Update Apps List**
4. Search for **"HR Attendance Face Detection"** and click **Install**.

---

## Configuration

### 1 — Enable the module
Go to **Attendances → Configuration → Settings** and enable:
- ✅ Enable Face Recognition Attendance
- ✅ Require GPS Geofencing *(optional)*
- ✅ Save Face Snapshots *(recommended for audit)*
- Set **Recognition Tolerance** (default: `0.55`)

### 2 — Add GPS Locations *(if geofencing is on)*
Go to **Attendances → Configuration → Attendance Locations**
- Enter the site name, latitude, longitude
- Set the allowed radius in metres (e.g. `100`)

### 3 — Enrol employee faces
Open any **Employee** record → **Face Recognition** tab:
1. Upload a clear frontal face photo in **Face Image**
2. Click **Generate Face Encoding**
3. A green confirmation confirms the 128-d encoding is stored

### 4 — Use the Kiosk
- From the backend: **Attendances → Face Kiosk Mode** (opens in a new tab)
- Or navigate directly to: `http://your-odoo/hr_attendance_face/kiosk`
- The page auto-scans every 4 seconds and shows check-in/out results

---

## How It Works

```
Browser webcam
     │
     ▼ JPEG frame (base64)
POST /hr_attendance_face/kiosk/verify
     │
     ├─ GPS geofence check (if enabled)
     │
     ├─ face_recognition.face_locations()   ← detect face in frame
     ├─ face_recognition.face_encodings()   ← extract 128-d descriptor
     ├─ face_recognition.face_distance()    ← compare with all employees
     │
     └─ if distance < threshold → create/close hr.attendance record
```

---

## File Structure

```
hr_attendance_face_detection/
├── __manifest__.py
├── __init__.py
├── controllers/
│   ├── main.py          # /verify + /test_location JSON endpoints
│   └── kiosk.py         # /kiosk HTTP page
├── models/
│   ├── hr_employee.py          # face_encoding field + generate action
│   ├── hr_attendance.py        # snapshot + GPS fields
│   ├── face_attendance_location.py  # geofence model
│   └── res_config_settings.py  # settings fields
├── wizard/
│   └── face_capture_wizard.py
├── views/
│   ├── hr_employee_views.xml
│   ├── hr_attendance_views.xml
│   ├── face_attendance_location_views.xml
│   ├── res_config_settings_views.xml
│   ├── kiosk_templates.xml
│   └── menu_items.xml
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
├── data/
│   └── ir_cron_data.xml        # midnight auto-checkout cron
└── static/src/
    ├── css/
    │   ├── face_detection.css  # backend styles
    │   └── kiosk.css           # full-screen kiosk dark UI
    └── js/
        ├── face_enrollment.js  # backend webcam capture widget
        └── face_api_kiosk.js   # kiosk scan loop + GPS
```

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `No face detected` | Use a well-lit, clear frontal photo. Avoid glasses/masks. |
| `face_recognition not installed` | Run `pip install face_recognition dlib numpy Pillow` |
| `GPS required` | Allow browser location access in kiosk tab |
| Multiple faces in enrollment photo | Upload a photo with exactly one person |
| Low confidence / wrong match | Lower the tolerance value (e.g. 0.45) in Settings |

---

## License
LGPL-3 — Free to use and modify.
