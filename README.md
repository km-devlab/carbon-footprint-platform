# 🌿 EcoPulse | Carbon Footprint Awareness Platform

EcoPulse is an immersive, accessible, motion-designed web application and high-efficiency API engineered to help individuals understand, track, and organically reduce their environmental footprint. Built with a Solarpunk aesthetic, the platform translates raw carbon calculations into tangible ecological metrics.

🌐 **Live Application:** [https://your-app.onrender.com/](https://your-app.onrender.com/)  
📑 **Interactive API Documentation:** [https://your-app.onrender.com/docs](https://your-app.onrender.com/docs)

---

## 🚀 Key Evaluation Features

### 🛡️ 1. Security & Data Hardening
- **Input Sanitization:** Leverages strict Pydantic core validation models to completely prevent type-casting vulnerabilities, invalid payloads, `NaN`, or infinite values before processing logic.
- **Stateless Framework:** Purely stateless architectural operations protect user confidentiality, eliminating local cross-session data leaks or persistent data exploitation vectors.

### ⚡ 2. Efficiency & Performance
- **Deterministic Math Engine:** Calculation pipelines operate at constant-time complexity $O(1)$, executing without costly database calls or heavy resource loops.
- **LRU Memoization Caching:** Implements Python's native `@lru_cache` mechanics to index recurring community inputs, eliminating repeated compute structures.
- **Asynchronous Front-End Debouncing:** Features a 250ms debounced user interface preventing event-flooding and shielding the backend from unintended micro-DDoS traffic.

### ♿ 3. Accessibility (WCAG 2.1 AA Compliant)
- Fully accessible keyboard navigation workflow layout utilizing native structural forms.
- High color-contrast visual guidelines maintaining strict compliance over solid solarpunk earth tones.
- Screen-reader ready landmarks including explicit input labels (`for` / `id` bindings) and live updating announcement cards (`aria-live="assertive"`).

---

## 🛠️ Architecture & Tech Stack

- **Backend:** Python 3.12, FastAPI (ASGI web engine), Uvicorn (Lightning-fast server context)
- **Frontend Layer:** Semantic HTML5, Tailwind CSS (Visual Styling), Alpine.js (Reactive states and dynamic fetches)
- **Testing Engine:** Pytest

```text
carbon-footprint-platform/
│
├── app/
│   ├── constants.py       # Validated emission calculation factors
│   ├── main.py            # API routing, static mounting, & server definitions
│   ├── schemas.py         # Pydantic schema contracts
│   ├── services.py        # Core mathematics engine with LRU memory caching
│   ├── static/            # Static assets and UI branding favicons
│   └── templates/         # WCAG-compliant Solarpunk user template interface
│
├── Procfile               # Production cloud execution procedures
├── requirements.txt       # Frozen environment configuration dependencies
└── runtime.txt            # Python compilation environment definition