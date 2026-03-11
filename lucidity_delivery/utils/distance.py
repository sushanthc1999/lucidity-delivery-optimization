"""
Haversine distance calculator.

Implements the DistanceCalculator interface using the standard
Haversine formula for great-circle distance on a sphere.
"""

import math

from lucidity_delivery.core.base_entities import Location
from lucidity_delivery.core.interfaces import DistanceCalculator


class HaversineDistanceCalculator(DistanceCalculator):
    """
    Calculates the great-circle distance between two points using
    the Haversine formula with Earth's mean radius.
    """
    _EARTH_RADIUS_KM = 6371.0

    def calculate_distance(self, loc1: Location, loc2: Location) -> float:
        """
        Returns distance in kilometers between two Location objects.
        
        Formula:
            a = sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlon/2)
            c = 2 * atan2(√a, √(1−a))
            d = R * c
        """
        lat1 = math.radians(loc1.latitude)
        lon1 = math.radians(loc1.longitude)
        lat2 = math.radians(loc2.latitude)
        lon2 = math.radians(loc2.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return self._EARTH_RADIUS_KM * c
