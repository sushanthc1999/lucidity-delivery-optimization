"""
Unit tests for the Haversine distance calculator.
"""
import unittest

from lucidity_delivery.core.base_entities import Location
from lucidity_delivery.utils.distance import HaversineDistanceCalculator


class TestHaversineDistanceCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = HaversineDistanceCalculator()

    def test_london_to_paris(self):
        """Known distance: London to Paris ≈ 343 km."""
        london = Location(latitude=51.5074, longitude=-0.1278)
        paris = Location(latitude=48.8566, longitude=2.3522)
        distance = self.calc.calculate_distance(london, paris)
        self.assertAlmostEqual(distance, 343.5, delta=5.0)

    def test_same_location_returns_zero(self):
        """Distance from a point to itself should be 0."""
        loc = Location(latitude=12.9716, longitude=77.5946)
        distance = self.calc.calculate_distance(loc, loc)
        self.assertAlmostEqual(distance, 0.0, places=5)

    def test_koramangala_to_hsr(self):
        """Short distance within Bangalore (< 5 km)."""
        koramangala = Location(latitude=12.9352, longitude=77.6245)
        hsr = Location(latitude=12.9116, longitude=77.6389)
        distance = self.calc.calculate_distance(koramangala, hsr)
        self.assertTrue(0 < distance < 5.0)

    def test_antipodal_points(self):
        """Opposite ends of the Earth ≈ 20015 km (half circumference)."""
        north_pole = Location(latitude=90.0, longitude=0.0)
        south_pole = Location(latitude=-90.0, longitude=0.0)
        distance = self.calc.calculate_distance(north_pole, south_pole)
        self.assertAlmostEqual(distance, 20015.0, delta=100.0)


class TestLocationValidation(unittest.TestCase):

    def test_invalid_latitude(self):
        with self.assertRaises(ValueError):
            Location(latitude=100.0, longitude=0.0)

    def test_invalid_longitude(self):
        with self.assertRaises(ValueError):
            Location(latitude=0.0, longitude=200.0)


if __name__ == "__main__":
    unittest.main()
