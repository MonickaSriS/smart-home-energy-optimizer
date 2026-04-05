import math
from typing import List

class SolarPanel:
    def __init__(self, peak_capacity_kw: float = 5.0, enabled: bool = False):
        self.peak_capacity = peak_capacity_kw
        self.enabled = enabled
        self.total_generated_today = 0.0
    
    def get_generation(self, hour: int, minute: int = 0) -> float:
        """
        Simulate solar generation with realistic curve
        Peak at solar noon (12 PM), zero at night
        """
        if not self.enabled or hour < 6 or hour >= 20:
            return 0.0
        
        # Time in decimal hours from sunrise (6 AM)
        time_decimal = hour + minute / 60.0
        
        # Bell curve centered at noon (12.0)
        # Peak at 12 PM, drops to near-zero at 6 AM and 8 PM
        normalized_time = (time_decimal - 12.0) / 6.0
        generation = self.peak_capacity * math.exp(-0.5 * (normalized_time ** 2) * 2)
        
        # Add some randomness for clouds (±15%)
        import random
        random.seed(hour * 60 + minute)
        cloud_factor = random.uniform(0.85, 1.0)
        
        return round(generation * cloud_factor, 2)
    
    def get_forecast(self, current_hour: int, hours_ahead: int = 24) -> List[float]:
        """Get solar generation forecast"""
        forecast = []
        for h in range(hours_ahead):
            future_hour = (current_hour + h) % 24
            forecast.append(self.get_generation(future_hour))
        return forecast