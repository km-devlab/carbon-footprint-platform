"""
Request/response data contracts for the Carbon Footprint API.

All inbound data is strongly typed with explicit bounds so malformed or
out-of-range input is rejected by Pydantic before it ever reaches business
logic in `services.py`.
"""

import math
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class FootprintCalculationRequest(BaseModel):
    """Monthly lifestyle inputs used to estimate a household's carbon footprint."""

    # Transport attributes
    transport_type: Literal[
        "electric_vehicle",
        "hybrid_vehicle",
        "petrol_vehicle",
        "diesel_vehicle",
        "public_bus",
        "train",
    ]
    distance_km: float = Field(..., ge=0, le=100_000, description="Distance traveled in kilometers per month")

    # Energy attributes
    electricity_kwh: float = Field(..., ge=0, le=50_000, description="Monthly electricity usage in kWh")
    clean_energy_percentage: float = Field(..., ge=0, le=100, description="Percentage of energy from renewable sources")

    # Diet attributes
    diet_type: Literal["meat_heavy", "vegetarian", "vegan"]

    @field_validator("distance_km", "electricity_kwh", "clean_energy_percentage")
    @classmethod
    def reject_non_finite(cls, value: float) -> float:
        """Reject NaN/Infinity, which would otherwise pass numeric range checks."""
        if math.isnan(value) or math.isinf(value):
            raise ValueError("Value must be a finite number.")
        return value


class ActionInsight(BaseModel):
    """A single personalized, actionable suggestion for reducing emissions."""

    action: str
    potential_saving_kg: float
    impact_level: Literal["High", "Medium", "Low"]


class FootprintCalculationResponse(BaseModel):
    """Computed carbon footprint breakdown returned by the calculate endpoint."""

    total_carbon_footprint_kg: float
    breakdown: dict[str, float]
    actionable_insights: list[ActionInsight]