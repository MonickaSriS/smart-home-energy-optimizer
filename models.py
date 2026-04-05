from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
from datetime import datetime, time

class Appliance(BaseModel):
    id: str
    name: str
    power_rating: float  # kW
    is_on: bool = False
    is_controllable: bool = True
    must_run_duration: Optional[float] = None  # hours
    runtime_so_far: float = 0.0
    completed: bool = False
    
    # Constraints
    earliest_start: Optional[time] = None
    latest_end: Optional[time] = None
    depends_on: Optional[str] = None  # ID of prerequisite appliance
    
    # Comfort-related
    is_comfort_critical: bool = False
    target_temperature: Optional[float] = None
    current_temperature: Optional[float] = None

class BatteryState(BaseModel):
    capacity_kwh: float = 10.0
    current_charge_kwh: float = 5.0
    max_charge_rate_kw: float = 5.0
    max_discharge_rate_kw: float = 5.0
    charge_efficiency: float = 0.95
    discharge_efficiency: float = 0.95
    
    @property
    def soc_percent(self) -> float:
        return (self.current_charge_kwh / self.capacity_kwh) * 100

class SolarState(BaseModel):
    current_generation_kw: float = 0.0
    forecast_next_hour: List[float] = Field(default_factory=list)
    total_generated_today: float = 0.0

class GridState(BaseModel):
    current_price_per_kwh: float
    price_forecast: List[float] = Field(default_factory=list)
    total_imported: float = 0.0
    total_exported: float = 0.0

class Observation(BaseModel):
    timestamp: str
    time_step: int  # 0-95 (15-min intervals)
    hour_of_day: int
    
    appliances: List[Appliance]
    battery: BatteryState
    solar: SolarState
    grid: GridState
    
    # Comfort metrics
    indoor_temperature: float  # Current temp
    target_temperature_range: tuple[float, float] = (68.0, 72.0)
    
    # Feedback
    last_action_cost: float = 0.0
    last_action_feedback: str = ""
    
    # Summary metrics
    total_cost_so_far: float = 0.0
    total_energy_consumed: float = 0.0
    comfort_violations: int = 0

class ApplianceAction(BaseModel):
    appliance_id: str
    command: Literal["ON", "OFF", "MAINTAIN"]

class BatteryAction(BaseModel):
    command: Literal["CHARGE", "DISCHARGE", "IDLE"]
    power_kw: float = 0.0  # How much to charge/discharge

class Action(BaseModel):
    appliance_actions: List[ApplianceAction]
    battery_action: BatteryAction
    reasoning: Optional[str] = None  # For debugging

class Reward(BaseModel):
    total: float
    cost_component: float = 0.0
    comfort_component: float = 0.0
    efficiency_component: float = 0.0
    constraint_penalty: float = 0.0
    feedback: str = ""