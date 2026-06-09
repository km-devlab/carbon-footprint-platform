# Paste the data validation shapes here
# Data entering the API is strongly typed and strict boundary validations are applied to eliminate malicious 
# input or anomalies.

from pydantic import BaseModel, Field, field_validator
from typing import Literal

class FootprintCalculationRequest(BaseModel):
    # Transport attributes
    transport_type: Literal["electric_vehicle", "hybrid_vehicle", "petrol_vehicle", "diesel_vehicle", "public_bus", "train"]
    distance_km: float = Field(..., ge=0, le=100000, description="Distance traveled in kilometers per month")
    
    # Energy attributes
    electricity_kwh: float = Field(..., ge=0, le=50000, description="Monthly electricity usage in kWh")
    clean_energy_percentage: float = Field(..., ge=0, le=100, description="Percentage of energy from renewable sources")
    
    # Diet attributes
    diet_type: Literal["meat_heavy", "vegetarian", "vegan"]

    @field_validator('distance_km', 'electricity_kwh')
    @classmethod
    def prevent_negative_nan(cls, value: float) -> float:
        import math
        if math.isnan(value) or math.isinf(value):
            raise ValueError("Value must be a valid finite number.")
        return value

class ActionInsight(BaseModel):
    action: str
    potential_saving_kg: float
    impact_level: Literal["High", "Medium", "Low"]

class FootprintCalculationResponse(BaseModel):
    total_carbon_footprint_kg: float
    breakdown: dict[str, float]
    actionable_insights: list[ActionInsight]