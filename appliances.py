from models import Appliance
from datetime import time
from typing import List

def get_easy_appliances() -> List[Appliance]:
    """3 appliances for easy task"""
    return [
        Appliance(
            id="dishwasher",
            name="Dishwasher",
            power_rating=0.75,  # 1.5 kWh over 2 hours = 0.75 kW
            must_run_duration=2.0,
            earliest_start=time(18, 0),  # 6 PM
            latest_end=time(6, 0),  # 6 AM next day
        ),
        Appliance(
            id="washing_machine",
            name="Washing Machine",
            power_rating=1.33,  # 2 kWh over 1.5 hours
            must_run_duration=1.5,
            earliest_start=time(5, 0),
            latest_end=time(23, 0),
        ),
        Appliance(
            id="ev_charger",
            name="EV Charger",
            power_rating=1.17,  # 7 kWh over 6 hours
            must_run_duration=6.0,
            latest_end=time(7, 0),
        ),
    ]

def get_medium_appliances() -> List[Appliance]:
    """10 appliances for medium task"""
    appliances = get_easy_appliances()
    
    appliances.extend([
        Appliance(
            id="dryer",
            name="Clothes Dryer",
            power_rating=3.0,
            must_run_duration=1.0,
            depends_on="washing_machine",
        ),
        Appliance(
            id="pool_pump",
            name="Pool Pump",
            power_rating=1.2,
            must_run_duration=4.0,
        ),
        Appliance(
            id="water_heater",
            name="Water Heater",
            power_rating=1.75,  # 3.5 kWh over 2 hours
            must_run_duration=2.0,
            is_comfort_critical=True,
            target_temperature=120.0,
        ),
        Appliance(
            id="hvac",
            name="HVAC System",
            power_rating=2.5,
            is_comfort_critical=True,
            target_temperature=70.0,
        ),
        Appliance(
            id="water_softener",
            name="Water Softener",
            power_rating=0.5,
            must_run_duration=1.0,
            earliest_start=time(22, 0),
            latest_end=time(6, 0),
        ),
        Appliance(
            id="irrigation",
            name="Irrigation System",
            power_rating=0.8,
            must_run_duration=1.0,
            earliest_start=time(5, 0),
            latest_end=time(8, 0),
        ),
        Appliance(
            id="dehumidifier",
            name="Dehumidifier",
            power_rating=0.7,
            is_controllable=True,
        ),
    ])
    
    return appliances

def get_hard_appliances() -> List[Appliance]:
    """20 appliances for hard task"""
    appliances = get_medium_appliances()
    
    appliances.extend([
        Appliance(
            id="home_office",
            name="Home Office",
            power_rating=1.5,
            earliest_start=time(9, 0),
            latest_end=time(17, 0),
            is_controllable=False,  # Must run during work hours
        ),
        Appliance(
            id="entertainment",
            name="Entertainment System",
            power_rating=0.8,
            is_controllable=False,
        ),
        Appliance(
            id="kitchen",
            name="Kitchen Appliances",
            power_rating=2.0,
            is_controllable=False,
        ),
        Appliance(
            id="garage_door",
            name="Garage Door",
            power_rating=0.1,
            is_controllable=False,
        ),
        Appliance(
            id="security",
            name="Security System",
            power_rating=0.3,
            is_controllable=False,
        ),
        Appliance(
            id="landscape_lighting",
            name="Landscape Lighting",
            power_rating=0.5,
            earliest_start=time(18, 0),
            latest_end=time(23, 0),
        ),
        Appliance(
            id="hot_tub",
            name="Hot Tub",
            power_rating=4.0,
            is_comfort_critical=True,
            target_temperature=102.0,
        ),
        Appliance(
            id="wine_fridge",
            name="Wine Fridge",
            power_rating=0.4,
            is_controllable=False,
        ),
        Appliance(
            id="refrigerator",
            name="Smart Refrigerator",
            power_rating=1.2,
            is_controllable=False,
        ),
        Appliance(
            id="thermostat_zone1",
            name="Thermostat Zone 1",
            power_rating=1.5,
            is_comfort_critical=True,
        ),
    ])
    
    return appliances