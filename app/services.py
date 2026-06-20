"""
Pure, side-effect-free carbon footprint calculations.

Functions here run synchronously and do not perform I/O, which keeps them
fast, trivially testable, and safe to cache by input value.
"""

from functools import lru_cache

from app.constants import (
    EMISSION_FACTORS_DIET,
    EMISSION_FACTORS_ENERGY,
    EMISSION_FACTORS_TRANSPORT,
)
from app.schemas import ActionInsight

DAYS_PER_MONTH = 30.0


@lru_cache(maxsize=1024)
def calculate_cached_footprint(
    transport_type: str,
    distance_km: float,
    electricity_kwh: float,
    clean_energy_percentage: float,
    diet_type: str,
) -> dict:
    """
    Compute a monthly carbon footprint breakdown in kg CO2e.

    Inputs are expected to have already been validated by
    `FootprintCalculationRequest` (Pydantic), which restricts
    `transport_type`/`diet_type` to known enum values and bounds the numeric
    fields. Results for identical inputs are cached since the computation is
    pure and deterministic, avoiding redundant work for repeat requests.

    Raises:
        KeyError: if called directly with a transport/diet type outside the
            known emission factor tables (cannot happen via the API, since
            the request schema restricts these to valid enum values).
    """
    transport_emissions = distance_km * EMISSION_FACTORS_TRANSPORT[transport_type]

    effective_grid_kwh = electricity_kwh * (1 - (clean_energy_percentage / 100.0))
    energy_emissions = effective_grid_kwh * EMISSION_FACTORS_ENERGY["grid_electricity"]

    diet_emissions = EMISSION_FACTORS_DIET[diet_type] * DAYS_PER_MONTH

    # Round each component first, then derive the total from the rounded
    # parts. This guarantees the displayed breakdown always sums exactly to
    # the displayed total (rounding the unrounded sum independently can
    # drift by a cent-equivalent due to floating-point/half-even rounding).
    breakdown = {
        "transport": round(transport_emissions, 2),
        "energy": round(energy_emissions, 2),
        "diet": round(diet_emissions, 2),
    }
    total = round(sum(breakdown.values()), 2)

    insights = _build_insights(
        transport_type=transport_type,
        distance_km=distance_km,
        electricity_kwh=electricity_kwh,
        clean_energy_percentage=clean_energy_percentage,
        diet_type=diet_type,
    )

    return {
        "total_carbon_footprint_kg": total,
        "breakdown": breakdown,
        "actionable_insights": [insight.model_dump() for insight in insights],
    }


def _build_insights(
    *,
    transport_type: str,
    distance_km: float,
    electricity_kwh: float,
    clean_energy_percentage: float,
    diet_type: str,
) -> list[ActionInsight]:
    """Generate tailored reduction suggestions based on the largest emission buckets."""
    insights: list[ActionInsight] = []

    if transport_type in ("petrol_vehicle", "diesel_vehicle") and distance_km > 500:
        savings = distance_km * (
            EMISSION_FACTORS_TRANSPORT[transport_type] - EMISSION_FACTORS_TRANSPORT["public_bus"]
        )
        insights.append(
            ActionInsight(
                action="Switching to public transit or carpooling can significantly lower your travel footprint.",
                potential_saving_kg=round(savings, 2),
                impact_level="High",
            )
        )

    if clean_energy_percentage < 50 and electricity_kwh > 200:
        savings = electricity_kwh * 0.5 * EMISSION_FACTORS_ENERGY["grid_electricity"]
        insights.append(
            ActionInsight(
                action="Sourcing at least 50% of your household energy from renewables can cut this further.",
                potential_saving_kg=round(savings, 2),
                impact_level="Medium",
            )
        )

    if diet_type == "meat_heavy":
        savings = (EMISSION_FACTORS_DIET["meat_heavy"] - EMISSION_FACTORS_DIET["vegetarian"]) * DAYS_PER_MONTH
        insights.append(
            ActionInsight(
                action="Shifting toward a more plant-forward diet meaningfully reduces food-related emissions.",
                potential_saving_kg=round(savings, 2),
                impact_level="High",
            )
        )

    return insights