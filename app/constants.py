# Paste the emission factors code block here
# To avoid database overhead and guarantee standard predictability, global emission factor constants are defined 
# clearly using scientific units ($kg\text{ }CO_2e$).

"""
Emission conversion factors based on IPCC / DEFRA guidelines.
Units are represented cleanly in kg CO2e per unit of consumption.
"""

# Transport: kg CO2e per KM
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