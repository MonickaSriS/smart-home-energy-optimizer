from datetime import datetime, time
from typing import List

class PricingModel:
    def __init__(self, difficulty: str = "easy"):
        self.difficulty = difficulty
        
    def get_price(self, hour: int, minute: int = 0) -> float:
        """Get electricity price in $/kWh based on time"""
        if self.difficulty == "easy":
            return self._easy_pricing(hour)
        elif self.difficulty == "medium":
            return self._medium_pricing(hour)
        else:
            return self._hard_pricing(hour, minute)
    
    def _easy_pricing(self, hour: int) -> float:
        """Simple time-of-use: peak vs off-peak"""
        if 7 <= hour < 22:  # 7 AM - 10 PM
            return 0.30
        return 0.12
    
    def _medium_pricing(self, hour: int) -> float:
        """Four-tier pricing"""
        if 0 <= hour < 6:  # Super off-peak
            return 0.10
        elif 6 <= hour < 14:  # Morning off-peak
            return 0.15
        elif 14 <= hour < 18:  # Afternoon mid-peak
            return 0.25
        elif 18 <= hour < 22:  # Evening peak
            return 0.35
        else:  # Night off-peak
            return 0.15
    
    def _hard_pricing(self, hour: int, minute: int) -> float:
        """Dynamic pricing with 15-min intervals"""
        import random
        random.seed(hour * 60 + minute)  # Deterministic but varying
        
        base = self._medium_pricing(hour)
        # Add noise: ±20%
        variation = random.uniform(-0.2, 0.2)
        return round(base * (1 + variation), 3)
    
    def get_forecast(self, current_hour: int, hours_ahead: int = 24) -> List[float]:
        """Get price forecast"""
        forecast = []
        for h in range(hours_ahead):
            future_hour = (current_hour + h) % 24
            forecast.append(self.get_price(future_hour))
        return forecast