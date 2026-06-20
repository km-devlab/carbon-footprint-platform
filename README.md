# 🌿 EcoPulse | Carbon Footprint Awareness Platform

EcoPulse is a web application and API that helps people understand, track, and reduce their monthly carbon footprint from transport, energy, and diet — turning raw emissions math into clear, actionable guidance.

🌐 **Live Application:** https://carbon-footprint-platform-4l2n.onrender.com
📑 **Interactive API Docs:** https://carbon-footprint-platform-4l2n.onrender.com/docs

---

## Key Features

### 🛡️ Security
- Strict Pydantic validation on every field — bounded ranges, fixed enums for transport/diet type, and explicit rejection of `NaN`/`Infinity` values before any calculation runs.
- A global exception handler ensures unexpected errors return a generic message instead of leaking internal stack traces.
- Baseline hardening headers (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`) on every response.
- CORS is restricted by default (configurable via the `ALLOWED_ORIGINS` environment variable) rather than open to all origins, since the UI and API share a single deployed origin.
- Stateless request handling — no user data is persisted or logged beyond standard request logs.

### ⚡ Efficiency
- Calculation logic is pure, synchronous arithmetic with no database or network calls on the hot path — effectively O(1) per request.
- `functools.lru_cache` memoizes results for repeated identical inputs.

### ♿ Accessibility
- Semantic landmarks (`header`, `main`, `footer`) with a keyboard-accessible skip link.
- Live regions (`aria-live="polite"`) announce updated results and insights to screen readers as sliders change.
- Slider inputs expose `aria-valuetext` with units (e.g. "400 kilometers per month") instead of bare numbers.
- Respects `prefers-reduced-motion` to disable decorative animation for users who request it.
- A `<noscript>` fallback informs users if JavaScript is unavailable, since the calculator requires it.

### 🧪 Testing
- `tests/test_calculations.py` — unit tests on the core calculation engine (boundaries, zero/extreme inputs, insight generation).
- `tests/test_api.py` — integration tests on the HTTP layer using FastAPI's `TestClient` (validation errors, status codes, response shape, security headers).

---

## Architecture & Tech Stack

- **Backend:** Python 3.12, FastAPI, Uvicorn
- **Frontend:** Server-rendered Jinja2 template, Tailwind CSS (CDN) for styling, Alpine.js for reactive state and API calls
- **Testing:** Pytest + FastAPI TestClient

```text
carbon-footprint-platform/
│
├── app/
│   ├── __init__.py
│   ├── constants.py       # Emission factor lookup tables
│   ├── main.py             # FastAPI app, routes, middleware, error handlers
│   ├── schemas.py          # Pydantic request/response models
│   ├── services.py         # Pure calculation logic + insight generation
│   ├── static/              # CSS and image assets
│   └── templates/
│       └── index.html       # Calculator UI
│
├── tests/
│   ├── test_calculations.py # Unit tests for services.py
│   └── test_api.py          # Integration tests for main.py
│
├── Procfile                # Render/Heroku-style start command
├── requirements.txt        # Pinned runtime + test dependencies
└── runtime.txt              # Python version pin
```

---

## Running locally

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

Visit `http://localhost:8000` for the UI, or `http://localhost:8000/docs` for interactive API docs.

### Running tests

```bash
pytest tests/ -v
```

---

## API

### `POST /api/v1/calculate`

Request body:

```json
{
  "transport_type": "petrol_vehicle",
  "distance_km": 1000,
  "electricity_kwh": 300,
  "clean_energy_percentage": 0,
  "diet_type": "vegan"
}
```

`transport_type` must be one of: `electric_vehicle`, `hybrid_vehicle`, `petrol_vehicle`, `diesel_vehicle`, `public_bus`, `train`.
`diet_type` must be one of: `meat_heavy`, `vegetarian`, `vegan`.

Response:

```json
{
  "total_carbon_footprint_kg": 411.7,
  "breakdown": { "transport": 190.0, "energy": 135.0, "diet": 86.7 },
  "actionable_insights": [
    {
      "action": "Shifting toward a more plant-forward diet meaningfully reduces food-related emissions.",
      "potential_saving_kg": 103.5,
      "impact_level": "High"
    }
  ]
}
```

### `GET /health`

Lightweight liveness check used for deployment monitoring. Returns `{"status": "ok"}`.

---

## Emission factors

Based on standard IPCC/DEFRA-style kg CO₂e conversion factors, defined in `app/constants.py`. These are illustrative averages for awareness purposes and are not a substitute for a certified carbon audit.