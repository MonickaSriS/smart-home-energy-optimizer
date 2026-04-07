from typing import Tuple, List, Dict, Any, Optional
import copy
from models import (
    Observation, Action, Reward, Appliance, 
    BatteryState, SolarState, GridState
)
from appliances import get_easy_appliances, get_medium_appliances, get_hard_appliances
from pricing import PricingModel
from solar import SolarPanel


class SmartHomeEnergyEnv:
    """Smart Home Energy Management Environment"""
    
    def __init__(self, difficulty: str = "easy"):
        self.difficulty = difficulty
        self.time_step_minutes = 15
        self.steps_per_day = 96
        
        self.pricing = PricingModel(difficulty)
        self.solar = SolarPanel(
            peak_capacity_kw=5.0,
            enabled=(difficulty in ["medium", "hard"])
        )
        
        self.current_step = 0
        self.appliances: List[Appliance] = []
        self.battery: Optional[BatteryState] = None
        
        self.total_cost = 0.0
        self.total_energy = 0.0
        self.comfort_violations = 0
        self.indoor_temp = 70.0
    
    async def reset(self) -> Observation:
        """Initialize a new episode"""
        self.current_step = 0
        self.total_cost = 0.0
        self.total_energy = 0.0
        self.comfort_violations = 0
        self.indoor_temp = 70.0
        
        # Load appliances
        if self.difficulty == "easy":
            self.appliances = get_easy_appliances()
        elif self.difficulty == "medium":
            self.appliances = get_medium_appliances()
        else:
            self.appliances = get_hard_appliances()
        
        # Battery only in hard mode
        if self.difficulty == "hard":
            self.battery = BatteryState(
                capacity_kwh=10.0,
                current_charge_kwh=5.0,
            )
        else:
            self.battery = None
        
        return self._get_observation()
    
    async def step(self, action: Action) -> Tuple[Observation, Reward, bool, Dict[str, Any]]:
        """Execute one time step"""
        hour, minute = self._get_current_time()
        dt = self.time_step_minutes / 60.0
        
        step_cost = 0.0
        step_energy = 0.0
        feedback_parts = []
        
        current_price = self.pricing.get_price(hour, minute)
        
        # --- Appliance control ---
        for app_action in action.appliance_actions:
            appliance = self._get_appliance(app_action.appliance_id)
            if not appliance:
                continue
            
            if app_action.command == "ON":
                if not appliance.is_on:
                    appliance.is_on = True
                    feedback_parts.append(f"Started {appliance.name}")
            elif app_action.command == "OFF":
                if appliance.is_on:
                    appliance.is_on = False
                    feedback_parts.append(f"Stopped {appliance.name}")
            
            # Energy usage
            if appliance.is_on:
                energy = appliance.power_rating * dt
                step_energy += energy
                step_cost += energy * current_price
                
                # Handle completion
                if appliance.must_run_duration:
                    appliance.runtime_so_far += dt
                    if appliance.runtime_so_far >= appliance.must_run_duration:
                        appliance.completed = True
                        appliance.is_on = False
                        feedback_parts.append(f"✓ {appliance.name} completed")
        
        # --- Solar ---
        solar_gen = self.solar.get_generation(hour, minute) * dt
        self.solar.total_generated_today += solar_gen
        
        net_grid_energy = step_energy - solar_gen
        
        # --- Battery (only in hard mode) ---
        if self.battery and action.battery_action.command != "IDLE":
            battery_energy = min(
                abs(action.battery_action.power_kw) * dt,
                self.battery.max_charge_rate_kw * dt
            )
            
            if action.battery_action.command == "CHARGE":
                charge_amount = min(
                    battery_energy,
                    self.battery.capacity_kwh - self.battery.current_charge_kwh
                )
                self.battery.current_charge_kwh += charge_amount * self.battery.charge_efficiency
                step_cost += charge_amount * current_price
                feedback_parts.append(f"Battery charged {charge_amount:.2f} kWh")
                    
            elif action.battery_action.command == "DISCHARGE":
                discharge_amount = min(battery_energy, self.battery.current_charge_kwh)
                self.battery.current_charge_kwh -= discharge_amount
                net_grid_energy -= discharge_amount * self.battery.discharge_efficiency
                feedback_parts.append(f"Battery discharged {discharge_amount:.2f} kWh")
        
        # --- Comfort ---
        self._update_comfort(hour)
        
        # --- Totals ---
        self.total_cost += step_cost
        self.total_energy += step_energy
        
        # --- Reward ---
        reward = self._calculate_reward(step_cost, step_energy, solar_gen)
        
        # --- Step update ---
        self.current_step += 1
        done = self.current_step >= self.steps_per_day
        
        obs = self._get_observation()
        obs.last_action_cost = step_cost
        obs.last_action_feedback = " | ".join(feedback_parts) if feedback_parts else "No changes"
        
        info = {
            "hour": hour,
            "minute": minute,
            "price": current_price,
            "solar_gen": solar_gen,
        }
        
        return obs, reward, done, info
    
    async def state(self) -> Dict[str, Any]:
        """Return current state for evaluation"""
        hour, minute = self._get_current_time()
        
        return {
            "time_step": self.current_step,
            "hour": hour,
            "total_cost": self.total_cost,
            "total_energy_consumed": self.total_energy,
            "solar_energy_generated": self.solar.total_generated_today,
            "solar_energy_used": min(self.total_energy, self.solar.total_generated_today),
            "appliances": [
                {
                    "id": a.id,
                    "completed": a.completed,
                    "runtime": a.runtime_so_far,
                }
                for a in self.appliances
            ],
            "battery_soc": self.battery.soc_percent if self.battery else 0.0,
            "comfort_violations": self.comfort_violations,
            "constraints_met": sum(
                1 for a in self.appliances 
                if a.completed or not a.must_run_duration
            ),
            "total_constraints": len(
                [a for a in self.appliances if a.must_run_duration]
            ),
        }
    
    def _get_observation(self) -> Observation:
        """Build observation"""
        hour, minute = self._get_current_time()
        
        battery_state = (
            copy.deepcopy(self.battery)
            if self.battery
            else BatteryState(capacity_kwh=1.0, current_charge_kwh=0.0)
        )
        
        return Observation(
            timestamp=f"{hour:02d}:{minute:02d}",
            time_step=self.current_step,
            hour_of_day=hour,
            appliances=copy.deepcopy(self.appliances),
            battery=battery_state,
            solar=SolarState(
                current_generation_kw=self.solar.get_generation(hour, minute),
                forecast_next_hour=self.solar.get_forecast(hour, hours_ahead=4),
                total_generated_today=self.solar.total_generated_today,
            ),
            grid=GridState(
                current_price_per_kwh=self.pricing.get_price(hour, minute),
                price_forecast=self.pricing.get_forecast(hour, hours_ahead=8),
            ),
            indoor_temperature=self.indoor_temp,
            total_cost_so_far=self.total_cost,
            total_energy_consumed=self.total_energy,
            comfort_violations=self.comfort_violations,
        )
    
    def _get_current_time(self) -> Tuple[int, int]:
        total_minutes = self.current_step * self.time_step_minutes
        hour = (total_minutes // 60) % 24
        minute = total_minutes % 60
        return hour, minute
    
    def _get_appliance(self, appliance_id: str) -> Appliance:
        for a in self.appliances:
            if a.id == appliance_id:
                return a
        return None
    
    def _update_comfort(self, hour: int):
        hvac = self._get_appliance("hvac")
        
        if hvac and hvac.is_on:
            self.indoor_temp = 70.0
        else:
            outdoor_temp = 85.0 if 10 <= hour <= 18 else 65.0
            self.indoor_temp += (outdoor_temp - self.indoor_temp) * 0.1
        
        if self.indoor_temp < 68.0 or self.indoor_temp > 72.0:
            self.comfort_violations += 1
    
    def _calculate_reward(self, cost: float, energy: float, solar: float) -> Reward:
        cost_component = -cost
        solar_bonus = 0.01 * solar
        comfort_penalty = -0.05 if self.indoor_temp < 68 or self.indoor_temp > 72 else 0.0
        
        total = cost_component + solar_bonus + comfort_penalty
        
        return Reward(
            total=total,
            cost_component=cost_component,
            comfort_component=comfort_penalty,
            efficiency_component=solar_bonus,
            feedback=f"Cost: ${cost:.3f}, Solar: {solar:.2f}kWh"
        )
    
    # Type aliases for compatibility
EnergyAction = Action
EnergyObservation = Observation