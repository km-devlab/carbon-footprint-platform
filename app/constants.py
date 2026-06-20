"""
Emission conversion factors based on IPCC / DEFRA guidance.

Units are expressed in kg CO2e per unit of consumption. Kept as static,
in-memory constants (rather than a database) since they change rarely and
this avoids unnecessary I/O on the calculation hot path.
"""

# Transport: kg CO2e per km
EMISSION_FACTORS_TRANSPORT = {
    "electric_vehicle": 0.05,
    "hybrid_vehicle": 0.12,
    "petrol_vehicle": 0.19,
    "diesel_vehicle": 0.18,
    "public_bus": 0.03,
    "train": 0.04,
}

# Energy: kg CO2e per kWh
EMISSION_FACTORS_ENERGY = {
    "grid_electricity": 0.45,
    "natural_gas": 0.18,
    "solar_renewable": 0.00,
}

# Diet: kg CO2e per day
EMISSION_FACTORS_DIET = {
    "meat_heavy": 7.26,
    "vegetarian": 3.81,
    "vegan": 2.89,
}