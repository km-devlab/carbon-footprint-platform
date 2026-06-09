# Paste the data validation shapes here
# Pure computation functions run synchronously without blocking the thread pool, making them easy to unit test.

from functools import lru_cache
from app.constants import (
    EMISSION_FACTORS_TRANSPORT,
    EMISSION_FACTORS_ENERGY,
    EMISSION_FACTORS_DIET
)
from app.schemas import ActionInsight

# Cache up to 1024 unique user scenarios to drastically reduce compute overhead
@lru_cache(maxsize=1024)
def calculate_cached_footprint(
    transport_type: str, 
    distance_km: float, 
    electricity_kwh: float, 
    clean_energy_percentage: float, 
    diet_type: str
) -> dict:
    
    # 1. Transport Calculations
    transport_emissions = distance_km * EMISSION_FACTORS_TRANSPORT[transport_type]
    
    # 2. Energy Calculations (accounting for green energy offsets)
    effective_grid_kwh = electricity_kwh * (1 - (clean_energy_percentage / 100.0))
    energy_emissions = effective_grid_kwh * EMISSION_FACTORS_ENERGY["grid_electricity"]
    
    # 3. Diet Calculations (calculated over a standard 30-day month)
    diet_emissions = EMISSION_FACTORS_DIET[diet_type] * 30.0
    
    total = transport_emissions + energy_emissions + diet_emissions
    
    # Generate tailored insights dynamically based on the largest emission buckets
    insights = []
    if transport_type in ["petrol_vehicle", "diesel_vehicle"] and distance_km > 500:
        savings = distance_km * (EMISSION_FACTORS_TRANSPORT[transport_type] - EMISSION_FACTORS_TRANSPORT["public_bus"])
        insights.append(ActionInsight(
            action="Switching to alternative commutes or public transit can significantly lower your travel footprint.",
            potential_saving_kg=round(savings, 2),
            impact_level="High"
        ))
        
    if clean_energy_percentage < 50 and electricity_kwh > 200:
        savings = electricity_kwh * 0.5 * EMISSION_FACTORS_ENERGY["grid_electricity"]
        insights.append(ActionInsight(
            action="Consider sourcing at least 50% of your household energy from renewable solutions.",
            potential_saving_kg=round(savings, 2),
            impact_level="Medium"
        ))

    if diet_type == "meat_heavy":
        savings = (EMISSION_FACTORS_DIET["meat_heavy"] - EMISSION_FACTORS_DIET["vegetarian"]) * 30
        insights.append(ActionInsight(
            action="Adopting a plant-forward or vegetarian diet helps optimize global food footprint metrics.",
            potential_saving_kg=round(savings, 2),
            impact_level="High"
        ))

    return {
        "total_carbon_footprint_kg": round(total, 2),
        "breakdown": {
            "transport": round(transport_emissions, 2),
            "energy": round(energy_emissions, 2),
            "diet": round(diet_emissions, 2)
        },
        "actionable_insights": [insight.model_dump() for insight in insights]
    }