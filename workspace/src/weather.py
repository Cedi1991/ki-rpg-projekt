```python
import math
import time
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple
import random

@dataclass
class WeatherState:
    """Represents the current weather state."""
    temperature: float = 20.0
    humidity: float = 50.0
    wind_speed: float = 5.0
    condition: str = "clear"
    time_of_day: float = 12.0  # 0-24 hours

@dataclass
class DayCycle:
    """Manages the deterministic day/night cycle."""
    current_time: float = 12.0
    time_scale: float = 1.0
    is_night: bool = False
    
    def update(self, delta_time: float) -> None:
        """Update the time of day."""
        self.current_time += delta_time * self.time_scale
        if self.current_time >= 24.0:
            self.current_time -= 24.0
        self.is_night = self.current_time < 6.0 or self.current_time >= 20.0

    def get_day_progress(self) -> float:
        """Get progress through the day (0.0 to 1.0)."""
        return self.current_time / 24.0

    def get_sun_position(self) -> Tuple[float, float]:
        """Get sun position (x, y) for 3D engine."""
        angle = (self.current_time / 24.0) * 2 * math.pi - math.pi / 2
        x = math.cos(angle)
        y = math.sin(angle)
        return x, y

class WeatherSystem:
    """
    Weather and day cycle system.
    Provides deterministic mana regeneration based on time of day.
    """
    
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.day_cycle = DayCycle()
        self.weather_state = WeatherState()
        self._last_update_time = time.time()
        
    def update(self, delta_time: float) -> None:
        """Update weather and day cycle."""
        self.day_cycle.update(delta_time)
        self._update_weather(delta_time)
        self._last_update_time = time.time()
        
    def _update_weather(self, delta_time: float) -> None:
        """Deterministically update weather based on time of day."""
        t = self.day_cycle.current_time
        
        # Temperature follows a sine curve peaking at 14:00
        temp_offset = math.sin((t - 14.0) / 24.0 * 2 * math.pi)
        self.weather_state.temperature = 20.0 + 10.0 * temp_offset
        
        # Humidity inversely correlated with temperature
        self.weather_state.humidity = 50.0 - 20.0 * temp_offset
        
        # Wind speed varies with time
        self.weather_state.wind_speed = 5.0 + 3.0 * math.sin(t / 4.0)
        
        # Condition based on humidity and time
        if self.weather_state.humidity > 70.0:
            self.weather_state.condition = "rain"
        elif self.weather_state.humidity < 30.0:
            self.weather_state.condition = "clear"
        else:
            self.weather_state.condition = "cloudy"
            
    def get_mana_regeneration_rate(self) -> float:
        """
        Get deterministic mana regeneration rate based on time of day.
        Higher at night, lower during day.
        """
        t = self.day_cycle.current_time
        # Night (20:00-6:00) has higher regen
        if self.day_cycle.is_night:
            # Peak at midnight
            night_progress = (t - 20.0) / 10.0 if t >= 20.0 else (t + 4.0) / 10.0
            regen = 1.5 + 0.5 * math.sin(night_progress * math.pi)
        else:
            # Day (6:00-20:00) has lower regen
            day_progress = (t - 6.0) / 14.0
            regen = 0.5 + 0.3 * math.sin(day_progress * math.pi)
            
        # Weather modifier
        if self.weather_state.condition == "rain":
            regen *= 1.2
        elif self.weather_state.condition == "clear":
            regen *= 0.9
            
        return max(0.1, regen)
        
    def get_weather_for_3d(self) -> Dict[str, Any]:
        """Get weather data for 3D engine rendering."""
        return {
            "temperature": self.weather_state.temperature,
            "humidity": self.weather_state.humidity,
            "wind_speed": self.weather_state.wind_speed,
            "condition": self.weather_state.condition,
            "sun_position": self.day_cycle.get_sun_position(),
            "time_of_day": self.day_cycle.current_time,
            "is_night": self.day_cycle.is_night
        }
        
    def get_lighting_parameters(self) -> Dict[str, float]:
        """Get lighting parameters for 3D engine."""
        sun_x, sun_y = self.day_cycle.get_sun_position()
        return