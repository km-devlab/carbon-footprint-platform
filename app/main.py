from fastapi import FastAPI, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

from app.schemas import FootprintCalculationRequest, FootprintCalculationResponse
from app.services import calculate_cached_footprint

# Initialize application
app = FastAPI(
    title="Carbon Footprint Awareness Engine",
    description="A stateless, high-efficiency API designed to accurately calculate carbon impact.",
    version="1.0.0"
)

# Establish robust CORS policies
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=False,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type", "Authorization"],
)

# Resolve path to templates directory dynamically relative to project files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


# --- WEB UI LANDING ROUTE ---
@app.get("/", response_class=HTMLResponse, summary="Serve Immersive User Web Dashboard")
async def serve_home_dashboard(request: Request):
    """
    Renders the motion-designed HTML layout directly to the user's browser,
    providing complete accessibility layers and smooth responsive forms.
    """
    return templates.TemplateResponse(request=request, name="index.html")


# --- CORE CALCULATOR API ENDPOINT ---
@app.post(
    "/api/v1/calculate",
    response_model=FootprintCalculationResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate monthly carbon footprint equivalents"
)
async def process_carbon_footprint(payload: FootprintCalculationRequest):
    """
    Accepts lifestyle consumption inputs, handles strict data sanitization,
    and returns localized carbon breakdown metrics along with mitigation protocols.
    """
    result = calculate_cached_footprint(
    transport_type=payload.transport_type,
    distance_km=payload.distance_km,
    electricity_kwh=payload.electricity_kwh,
    clean_energy_percentage=payload.clean_energy_percentage,
    diet_type=payload.diet_type
)
    return result

