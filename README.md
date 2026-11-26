# 🎵 SoundCraft — Musical Instrument Inventory & E-Commerce System

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask%203.0+-green.svg)](https://flask.palletsprojects.com/)
[![Render](https://img.shields.io/badge/Deploy-Render.com-brightgreen.svg)](https://render.com)
[![Status](https://img.shields.io/badge/Status-Live%20Production-success.svg)](https://musicalinstrumentinventorysystem.onrender.com)
[![Database](https://img.shields.io/badge/Database-SQLite3-orange.svg)](https://sqlite.org)

A comprehensive, production-ready full-stack web application for musical instrument retail, inventory control, and customer e-commerce. Features **30 distinct, non-repeating acoustic and electronic instruments**, interactive Web Audio synthesis, studio-quality iconic preview tracks, customer cart & checkout, transactional stock deduction, dynamic analytics, and strict role-based access control.

---

## 🌐 Live Cloud Deployment
- **Live Public URL**: [https://musicalinstrumentinventorysystem.onrender.com](https://musicalinstrumentinventorysystem.onrender.com)
- **Customer Store**: [https://musicalinstrumentinventorysystem.onrender.com/store](https://musicalinstrumentinventorysystem.onrender.com/store)
- **Admin Portal**: [https://musicalinstrumentinventorysystem.onrender.com/login](https://musicalinstrumentinventorysystem.onrender.com/login)

---

## 🚀 Key Highlights & Features

### 1. 🎸 30 Unique Musical Instruments Catalog
- Exactly 30 distinct instruments spanning String, Percussion, Wind, Keyboard, and Electronic categories.
- Unique alphanumeric identification (`INS001` through `INS030`) with specifications, brand, price, and initial stock quantities.
- Zero duplicate or placeholder instruments.

### 2. 🎧 Studio Audio Engine & Iconic Track Previews
- **Web Audio Synthesis (`instrument_synth.js`)**: Real-time realistic acoustic modeling for Drum Kits (pitch-glide kick + noise snare), Tabla (dual-drum Bayan & Dayan), Acoustic Guitar (Karplus-Strong string pluck), Electric Guitar (overdrive crunch), Grand Piano, Flute (breath air noise), Violin, and Sitar.
- **46 Studio Audio Tracks**: High-fidelity `.wav` sound samples and iconic musical tracks mapped directly to catalog items for immersive customer exploration.

### 3. 🛒 Customer E-Commerce Storefront
- Dedicated customer registration, login, and secure session management.
- Dynamic responsive store catalog with real-time category filtering and search.
- Interactive Shopping Cart with live total calculations, quantity adjustments, and stock boundary checks.
- Direct checkout with simulated SMS order confirmations and permanent order history tracking.

### 4. 🛡️ Strict Role-Based Access Control (RBAC)
- Multi-tier authentication distinguishing **Store Administrators** from **Shoppers/Customers**.
- Protected administrative routes (`/dashboard`, `/manage-inventory`, `/admin/orders`) locked behind `@login_required` decorators.
- Customer accounts attempting to navigate to administrative areas are strictly blocked with security alerts.
- Password security via PBKDF2-SHA256 salted hashing.

### 5. 📊 Real-Time Admin Dashboard & Business Intelligence
- Executive summary metrics: Total Catalog Items, Inventory Stock Value, Units Sold, and Revenue Generated.
- Interactive Chart.js visual breakdowns of inventory by category and stock depletion levels.
- Automated Low Stock (1–5 units) and Out of Stock (0 units) warnings.
- Instant CSV export for inventory reports and sales audit trails.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3, Flask 3.0+, Gunicorn WSGI Server |
| **Frontend** | HTML5, CSS3, Modern ES6+ JavaScript, Chart.js, Font Awesome |
| **Audio Engine**| Web Audio API, Synthesized Dual-Oscillators, Studio WAV Assets |
| **Database** | SQLite3 with parameterized queries & atomic transactional commit/rollback |
| **Deployment** | Render Cloud Platform, GitHub CI/CD Sync |

---

## 📂 Project Directory Structure

```
MusicalInstrumentInventorySystem/
├── app.py                      # Main Flask application & route controllers
├── database.py                 # SQLite database schema, initialization & queries
├── musical_inventory.db        # SQLite database file
├── Procfile                    # Render production process command
├── requirements.txt            # Python dependencies
├── static/
│   ├── audio/                  # 46 studio instrument audio tracks (.wav)
│   ├── css/                    # Responsive styling & themes
│   └── js/
│       └── instrument_synth.js # Real-time acoustic synthesis engine
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Master layout with navigation
│   ├── store.html              # Customer e-commerce catalog
│   ├── dashboard.html          # Admin analytics dashboard
│   ├── inventory.html          # Inventory management table
│   ├── cart.html               # Shopping cart & checkout
│   ├── login.html              # Secure authentication portal
│   └── ...
└── documentation/              # Academic reports, viva guides & manuals
```

---

## 💻 Local Setup & Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Harsh-1600/MusicalInstrumentInventorySystem.git
   cd MusicalInstrumentInventorySystem
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the web app**:
   - Storefront: `http://127.0.0.1:5000/store`
   - Admin Login: `http://127.0.0.1:5000/login`

---

## 📄 License & Credits
Developed as an advanced academic project showcasing modern Python/Flask web development, cloud architecture, and multimedia interactive web design.
