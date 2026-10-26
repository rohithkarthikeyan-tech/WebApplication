# Aether - Modern Glassmorphic Django Web Application

A full-stack, responsive web application engineered with **Django 6**, modern **dark glassmorphism**, ambient animated gradients, built-in user authentication, and SQLite persistence.

---

## Highlights & Features

- **Premium Dark Aesthetics**: Styled with real-time CSS backdrop filters (`backdrop-filter: blur(18px)`), cyan (`#00f2fe`) and purple (`#9b51e0`) glowing gradients, and responsive typography (*Outfit* & *Plus Jakarta Sans*).
- **Animated Background**: Dynamic ambient gradient orbs with subtle cursor-driven motion and grid mesh overlay.
- **7 Fully Realized Pages**:
  1. **Home**: Hero section, live system status monitor, stats counter strip, and interactive 3D feature cards.
  2. **About**: Architectural milestones timeline, platform story, high-tech holographic visuals, and technology stack breakdown.
  3. **Contact**: Working contact form that saves submitted messages directly into the SQLite database (`ContactMessage` model) with CSRF protection and live message counter.
  4. **Registration**: Clean registration gateway with validation, minimum password strength rules, and password confirmation checks.
  5. **Login / Logout**: Built-in Django session authentication with redirect handling.
  6. **Protected Dashboard**: Secured via `@login_required`, displaying user identity, quick action tiles, live system metrics, and message activity.
  7. **Custom 404 Page**: Futuristic signal-lost error page with navigation return actions.
- **Interactive Feedback**: Real-time floating toast messages for actions, form errors, and session status.
- **Zero Heavy Frontend Dependencies**: 100% vanilla CSS and lightweight clientside JavaScript.

---

## Tech Stack

- **Backend**: Python, Django 6.1
- **Database**: SQLite
- **Frontend**: HTML5, Vanilla CSS3 (Glassmorphism & Gradients), Vanilla JavaScript
- **Security**: Django Auth, CSRF Defense, PBKDF2 Password Hashing, Protected Route Decorators

---

## Quick Start & Installation

### 1. Clone the repository
```bash
git clone https://github.com/rohithkarthikeyan-tech/WebApplication.git
cd WebApplication
```

### 2. Set up a virtual environment (recommended)
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Django
```bash
pip install django
```

### 4. Apply Database Migrations
```bash
python manage.py migrate
```

### 5. (Optional) Run Tests & Integrity Checks
```bash
python manage.py check
python manage.py test website
```

### 6. Launch the Development Server
```bash
python manage.py runserver
```

Visit the application at: `http://127.0.0.1:8000/`

---

## Route Overview

| Route | URL | Access Level | Description |
| :--- | :--- | :--- | :--- |
| **Home** | `/` | Public | Hero, features, live status monitor, stats |
| **About** | `/about/` | Public | Visuals, roadmap, tech matrix |
| **Contact** | `/contact/` | Public | Database-backed contact form |
| **Register** | `/register/` | Public | New user sign-up with password verification |
| **Login** | `/login/` | Public | Session authentication gateway |
| **Logout** | `/logout/` | Authenticated | Clears user session |
| **Dashboard** | `/dashboard/` | Authenticated (`@login_required`) | User portal with stats & actions |
| **Custom 404** | `/404/` | Public | 404 error page preview |

---

## License

MIT License. Designed & Developed with Django.
