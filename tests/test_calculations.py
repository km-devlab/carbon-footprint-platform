"""Unit tests for pure calculation logic in app.services."""

from app.services import calculate_cached_footprint


def test_standard_baseline_emissions():
    """A normal user footprint computes accurately against known emission factors."""
    result = calculate_cached_footprint(
        transport_type="petrol_vehicle",
        distance_km=1000,
        electricity_kwh=300,
        clean_energy_percentage=0,
        diet_type="vegan",
    )
    # Expected: (1000 * 0.19) + (300 * 0.45) + (2.89 * 30) = 190 + 135 + 86.7 = 411.7
    assert result["total_carbon_footprint_kg"] == 411.7
    assert "transport" in result["breakdown"]


def test_zero_boundary_conditions():
    """Zero-valued inputs return the expected baseline without raising."""
    result = calculate_cached_footprint(
        transport_type="electric_vehicle",
        distance_km=0,
        electricity_kwh=0,
        clean_energy_percentage=100,
        diet_type="vegan",
    )
    assert result["total_carbon_footprint_kg"] == 86.7  # Diet emissions only
    assert result["breakdown"]["transport"] == 0
    assert result["breakdown"]["energy"] == 0


def test_high_boundary_limits():
    """Extreme (but schema-valid) inputs do not throw and produce a positive total."""
    result = calculate_cached_footprint(
        transport_type="diesel_vehicle",
        distance_km=5000,
        electricity_kwh=2000,
        clean_energy_percentage=50,
        diet_type="meat_heavy",
    )
    assert result["total_carbon_footprint_kg"] > 0


def test_full_clean_energy_eliminates_grid_emissions():
    """100% clean energy should zero out the grid-electricity emission component."""
    result = calculate_cached_footprint(
        transport_type="train",
        distance_km=100,
        electricity_kwh=500,
        clean_energy_percentage=100,
        diet_type="vegetarian",
    )
    assert result["breakdown"]["energy"] == 0


def test_breakdown_sums_to_total():
    """The breakdown components should always sum to the reported total."""
    result = calculate_cached_footprint(
        transport_type="hybrid_vehicle",
        distance_km=750,
        electricity_kwh=410,
        clean_energy_percentage=25,
        diet_type="meat_heavy",
    )
    breakdown_sum = round(sum(result["breakdown"].values()), 2)
    assert breakdown_sum == result["total_carbon_footprint_kg"]


def test_high_petrol_mileage_generates_transport_insight():
    """Long petrol/diesel commutes should trigger a transport-switching insight."""
    result = calculate_cached_footprint(
        transport_type="petrol_vehicle",
        distance_km=600,
        electricity_kwh=100,
        clean_energy_percentage=100,
        diet_type="vegan",
    )
    actions = [i["impact_level"] for i in result["actionable_insights"]]
    assert "High" in actions
    assert len(result["actionable_insights"]) == 1


def test_low_clean_energy_generates_energy_insight():
    """High grid reliance with low clean-energy share should trigger an energy insight."""
    result = calculate_cached_footprint(
        transport_type="electric_vehicle",
        distance_km=10,
        electricity_kwh=300,
        clean_energy_percentage=10,
        diet_type="vegan",
    )
    insight_actions = [i["action"] for i in result["actionable_insights"]]
    assert any("renewable" in action.lower() for action in insight_actions)


def test_meat_heavy_diet_generates_diet_insight():
    """A meat-heavy diet should always trigger a diet-related insight."""
    result = calculate_cached_footprint(
        transport_type="train",
        distance_km=10,
        electricity_kwh=10,
        clean_energy_percentage=100,
        diet_type="meat_heavy",
    )
    insight_actions = [i["action"] for i in result["actionable_insights"]]
    assert any("plant-forward" in action.lower() for action in insight_actions)


def test_low_impact_profile_generates_no_insights():
    """A low-impact, already-green profile should not be nagged with suggestions."""
    result = calculate_cached_footprint(
        transport_type="electric_vehicle",
        distance_km=50,
        electricity_kwh=50,
        clean_energy_percentage=100,
        diet_type="vegan",
    )
    assert result["actionable_insights"] == []