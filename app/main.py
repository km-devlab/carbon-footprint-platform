import logging
import os

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.schemas import FootprintCalculationRequest, FootprintCalculationResponse
from app.services import calculate_cached_footprint

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("carbon_footprint_api")

app = FastAPI(
    title="Carbon Footprint Awareness Engine",
    description="A stateless API that calculates a household's monthly carbon footprint "
    "and returns personalized, actionable reduction insights.",
    version="1.0.0",
)

# The UI and API are served from the same Render deployment (single origin),
# so cross-origin access is not required. Restricting origins removes an
# unnecessary attack surface compared to a wildcard policy.
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Attach baseline hardening headers to every response."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Return a clean, client-safe error shape for invalid input instead of a raw stack trace."""
    logger.warning("Validation failed for %s: %s", request.url.path, exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Invalid input. Please check the submitted values and try again."},
    )


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all so internal errors never leak implementation details to the client."""
    logger.error("Unhandled error on %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )


@app.get("/", response_class=HTMLResponse, summary="Serve the web dashboard")
async def serve_home_dashboard(request: Request) -> HTMLResponse:
    """Render the calculator's HTML dashboard."""
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/health", summary="Liveness check", tags=["meta"])
async def health_check() -> dict:
    """Lightweight endpoint for uptime monitoring and deployment health checks."""
    return {"status": "ok"}


@app.post(
    "/api/v1/calculate",
    response_model=FootprintCalculationResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate monthly carbon footprint",
)
async def process_carbon_footprint(payload: FootprintCalculationRequest) -> dict:
    """
    Accept monthly lifestyle inputs (transport, energy, diet), validate them
    against strict bounds, and return a carbon footprint breakdown along with
    personalized reduction insights.
    """
    return calculate_cached_footprint(
        transport_type=payload.transport_type,
        distance_km=payload.distance_km,
        electricity_kwh=payload.electricity_kwh,
        clean_energy_percentage=payload.clean_energy_percentage,
        diet_type=payload.diet_type,
    )