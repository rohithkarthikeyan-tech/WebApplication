# Aether - Modern Responsive Django Platform with AI Assistant & Polyglot Persistence

[![Django Version](https://img.shields.io/badge/Django-6.1-green.svg)](https://www.djangoproject.com/)
[![Database](https://img.shields.io/badge/SQL-SQLite-blue.svg)](https://www.sqlite.org/)
[![NoSQL](https://img.shields.io/badge/NoSQL-MongoDB-brightgreen.svg)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

A full-stack, enterprise-grade web application engineered with **Django 6**, **dark glassmorphic aesthetics**, an **AI Assistant** available on every page, **SQL-backed FAQs and Support Tickets**, **MongoDB-backed Chat Logs and Feedback**, **Request Logging**, **Subsystem Health Monitoring**, and **8 Diagnostic Error Codes**.

---

## 🌐 Live Deployment Link

- **Live URL**: [https://webapplication-dsvi.onrender.com/](https://webapplication-dsvi.onrender.com/) *(or your deployed Render service endpoint)*
- **GitHub Repository**: [https://github.com/rohithkarthikeyan-tech/WebApplication](https://github.com/rohithkarthikeyan-tech/WebApplication)

---

## 🚀 Key Feature Deliverables

### 1. Responsive Multi-Page Platform with Global Chat Widget
- Over 7 responsive pages (Home, About, FAQs, Error Codes, Health Check, Support Tickets, Contact, Dashboard, Login, Register).
- A floating **AI Assistant chat widget** permanently embedded on **every page** via `base.html`.
- Adaptive mobile navigation drawer with sticky glassmorphism header and animated ambient cyan/purple gradients.

### 2. SQL Database-Backed FAQs (10+ Questions)
- Stored in the relational SQL database via Django's `FAQ` model (`website_faq`).
- Interactive `/faqs/` page featuring real-time client-side search filtering and topic category pills (General, Authentication, Security, Error Codes, Architecture, AI Assistant).

### 3. Diagnostic Error Code Matrix (8 Codes)
- Full documentation, technical causes, resolution guidelines, and live HTTP simulation for:
  - `400 Bad Request`
  - `401 Unauthorized`
  - `403 Forbidden`
  - `404 Not Found`
  - `429 Too Many Requests`
  - `500 Internal Server Error`
  - `503 Service Unavailable`
  - `480 Aether Quantum Sync Failure` *(Site-Specific Custom Error)*
- Interactive `/errors/` directory and simulator endpoints at `/error-preview/<int:code>/`.

### 4. Custom 404 and 500 Pages with "Ask the Assistant"
- Tailored glassmorphic error templates (`website/404.html` and `website/500.html`).
- Both error pages feature a prominent **"Ask the Assistant"** option that launches the AI chat widget with pre-populated error context and automated diagnostic assistance.

### 5. Multi-Capability AI Assistant
- **FAQ Knowledge Base**: Searches SQL database FAQs to answer user queries.
- **Error Code Explainer**: Understands all 8 error codes (including custom 480) and provides immediate recovery guidance.
- **Support Ticket Escalation**: If the assistant cannot answer an inquiry, it automatically prompts the user and creates a formal support ticket in SQL.

### 6. Polyglot Persistence Architecture
- **SQL (SQLite / PostgreSQL)**: Transactional and relational data:
  - User Accounts & Sessions
  - FAQs (`website_faq`)
  - Error Codes (`website_errorcode`)
  - Support Tickets (`website_supportticket`)
  - Contact Messages (`website_contactmessage`)
- **MongoDB (NoSQL)**: Event-driven telemetry:
  - Chat conversation transcripts (`chat_logs`)
  - User thumbs-up/thumbs-down feedback ratings and comments (`feedback`)
  - HTTP request metrics (`request_logs`)
  *(Includes an automated in-memory ring-buffer fallback ensuring zero crashes if MongoDB is offline).*

### 7. Request Logging & Subsystem Health Check
- Custom `RequestLoggingMiddleware` measuring request durations, status codes, methods, paths, and client IPs.
- `/health/` monitoring dashboard and JSON API (`/health/?format=json`) inspecting SQL latency, MongoDB connectivity, and third-party API availability.
- **Third-Party API with Time Limit & Fallback**: Calls external cloud telemetry with a strict **2.0-second timeout**. If the external API times out or is unreachable, the system seamlessly engages a curated offline fallback without failing.

### 8. Environment Security (Zero Secrets in Repository)
- All secrets, API keys (`GEMINI_API_KEY`, `OPENAI_API_KEY`), database URIs (`MONGO_URI`), and flags (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`) are loaded via `python-dotenv`.
- A clean `.env.example` template is provided; `.env` is strictly git-ignored.

---

## 💡 Proposed Improvement

### Asynchronous Celery/Redis Task Queue & Hybrid Vector Semantic Search (RAG)

**Current Architecture:**
The application currently performs database queries, external API calls, and MongoDB log persistence synchronously in the request-response cycle (with strict timeout guards).

**Proposed Enhancement:**
1. **Background Job Orchestration (Celery + Redis)**:
   - Offload third-party telemetry queries, outbound support email dispatches, and MongoDB analytics writes to asynchronous background worker queues.
   - Drastically reduces server response times under high concurrency and prevents external network spikes from affecting client page loads.
2. **Dense Vector Embeddings for the AI Assistant**:
   - Augment the current SQL keyword-scoring engine with vector embeddings (using `pgvector` or `FAISS`).
   - Enables semantic similarity search across long multi-paragraph documents, handles paraphrased queries, and allows users to upload screenshots of error logs for automated diagnostic parsing.

---

## 🛠️ Quick Start & Installation

### 1. Clone the repository
```bash
git clone https://github.com/rohithkarthikeyan-tech/WebApplication.git
cd WebApplication
```

### 2. Configure Environment Variables
```bash
# Copy sample configuration
copy .env.example .env
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations & Seed Data
```bash
python manage.py migrate
```
*(Automatically creates SQL tables and seeds at least 10 FAQs and 8 Error Codes).*

### 5. Execute Test Suite (All 15 Tests Passing)
```bash
python manage.py test website
```

### 6. Run the Development Server
```bash
python manage.py runserver
```

Open your browser at: `http://127.0.0.1:8000/`

---

## 📍 Route Directory

| Route | URL | Description |
| :--- | :--- | :--- |
| **Home** | `/` | Hero, third-party telemetry, feature cards, live stats |
| **About** | `/about/` | Story, architecture visuals, technology matrix |
| **FAQs** | `/faqs/` | 10+ SQL-backed FAQs with search filter & categories |
| **Error Codes** | `/errors/` | 8 Error codes with simulator triggers & AI assistance |
| **Simulate Error** | `/error-preview/<int:code>/` | Live simulator for 400, 401, 403, 404, 429, 500, 503, 480 |
| **Health Monitor** | `/health/` | Real-time SQL DB, MongoDB, and external API telemetry |
| **Raw Health JSON** | `/health/?format=json` | Machine-readable subsystem health JSON payload |
| **Support Tickets**| `/tickets/` | SQL support ticket helpdesk and creation form |
| **Contact** | `/contact/` | Contact message submission saved to SQLite |
| **Register** | `/register/` | Account registration with confirmation |
| **Login** | `/login/` | Django session authentication |
| **Dashboard** | `/dashboard/` | Protected user portal (*requires login*) |
| **Preview 404** | `/404/` | Custom 404 page with "Ask the Assistant" |
| **Preview 500** | `/500/` | Custom 500 page with "Ask the Assistant" |
| **Chat API** | `/api/chat/` | AI Assistant message dispatch & MongoDB log |
| **Feedback API** | `/api/feedback/` | AI thumbs up/down feedback saved to MongoDB |

---

## 📄 License

MIT License. Designed and developed with Django 6.
