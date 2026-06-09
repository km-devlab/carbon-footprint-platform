import pytest
from app.services import calculate_cached_footprint

def test_standard_baseline_emissions():
    """Verify that a normal user footprint computes accurately against factors."""
    result = calculate_cached_footprint(
        transport_type="petrol_vehicle",
        distance_km=1000,
        electricity_kwh=300,
        clean_energy_percentage=0,
        diet_type="vegan"
    )
    # Expected: (1000 * 0.19) + (300 * 0.45) + (2.89 * 30) = 190 + 135 + 86.7 = 411.7
    assert result["total_carbon_footprint_kg"] == 411.7
    assert "transport" in result["breakdown"]

def test_zero_boundary_conditions():
    """Ensure zero bounds return expected baseline values without math crash."""
    result = calculate_cached_footprint(
        transport_type="electric_vehicle",
        distance_km=0,
        electricity_kwh=0,
        clean_energy_percentage=100,
        diet_type="vegan"
    )
    assert result["total_carbon_footprint_kg"] == 86.7  # Just diet remaining

def test_high_boundary_limits():
    """Ensure extreme input caps do not throw calculations out of scope."""
    result = calculate_cached_footprint(
        transport_type="diesel_vehicle",
        distance_km=5000,
        electricity_kwh=2000,
        clean_energy_percentage=50,
        diet_type="meat_heavy"
    )
    assert result["total_carbon_footprint_kg"] > 0