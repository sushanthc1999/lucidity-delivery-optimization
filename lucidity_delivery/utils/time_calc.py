"""
Time calculation utility.

Encapsulates travel time computation so the routing engine
does not need to handle raw arithmetic directly.
"""


class TimeCalculator:
    """
    Responsible for converting distance and speed into travel time.
    Single Responsibility Principle — only does time math.
    """

    @staticmethod
    def calculate_travel_time(distance_km: float, speed_kmph: float) -> float:
        """
        Returns travel time in hours.
        
        Args:
            distance_km: Distance to travel in kilometers.
            speed_kmph: Travel speed in km/hr.
            
        Returns:
            Time in hours.
            
        Raises:
            ValueError: If speed is zero or negative.
        """
        if speed_kmph <= 0:
            raise ValueError(f"Speed must be positive, got {speed_kmph}")
        return distance_km / speed_kmph
