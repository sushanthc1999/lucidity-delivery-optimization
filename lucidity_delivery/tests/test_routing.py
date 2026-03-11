"""
Unit tests for the routing strategy (BruteForceDeliveryStrategy).
"""
import unittest

from lucidity_delivery.core.base_entities import Location
from lucidity_delivery.domain.models import (
    Consumer,
    DeliveryExecutive,
    Order,
    Restaurant,
)
from lucidity_delivery.engines.routing_strategy import BruteForceDeliveryStrategy
from lucidity_delivery.utils.distance import HaversineDistanceCalculator


class TestBruteForceDeliveryStrategy(unittest.TestCase):

    def setUp(self):
        self.calc = HaversineDistanceCalculator()
        self.strategy = BruteForceDeliveryStrategy(distance_calculator=self.calc)

    def _make_executive(self, lat: float, lon: float) -> DeliveryExecutive:
        return DeliveryExecutive(
            user_id="E1", name="Aman",
            current_location=Location(lat, lon), speed=20.0,
        )

    def _make_order(
        self, order_id: str,
        r_lat: float, r_lon: float, prep_mins: float,
        c_lat: float, c_lon: float,
    ) -> Order:
        restaurant = Restaurant(
            restaurant_id=f"R-{order_id}", name=f"Restaurant {order_id}",
            location=Location(r_lat, r_lon),
            average_prep_time_hrs=prep_mins / 60.0,
        )
        consumer = Consumer(
            user_id=f"C-{order_id}", name=f"Consumer {order_id}",
            location=Location(c_lat, c_lon),
        )
        return Order(order_id=order_id, restaurant=restaurant, consumer=consumer)

    # ── Test: No orders ──────────────────────────────────────────
    def test_no_orders(self):
        executive = self._make_executive(12.9716, 77.5946)
        result = self.strategy.find_optimal_route(executive, [])
        self.assertEqual(result.total_time_hrs, 0.0)
        self.assertEqual(len(result.path), 0)

    # ── Test: Single order ───────────────────────────────────────
    def test_single_order_path_structure(self):
        """Single order must produce exactly [pickup, drop]."""
        executive = self._make_executive(12.9716, 77.5946)
        order = self._make_order("O1", 12.9352, 77.6245, 30, 12.9279, 77.6271)

        result = self.strategy.find_optimal_route(executive, [order])

        self.assertEqual(len(result.path), 2)
        self.assertEqual(result.path[0].location_type, "pickup")
        self.assertEqual(result.path[0].order_id, "O1")
        self.assertEqual(result.path[1].location_type, "drop")
        self.assertEqual(result.path[1].order_id, "O1")
        self.assertGreater(result.total_time_hrs, 0.0)

    # ── Test: Two orders — pickup before drop constraint ─────────
    def test_two_orders_pickup_before_drop(self):
        """Every order's pickup must appear before its drop in the path."""
        executive = self._make_executive(12.9716, 77.5946)
        o1 = self._make_order("O1", 12.9352, 77.6245, 20, 12.9279, 77.6271)
        o2 = self._make_order("O2", 12.9450, 77.6100, 35, 12.9150, 77.6400)

        result = self.strategy.find_optimal_route(executive, [o1, o2])

        self.assertEqual(len(result.path), 4)  # 2 pickups + 2 drops

        # For each order, verify pickup index < drop index
        for oid in ["O1", "O2"]:
            pickup_idx = next(
                i for i, n in enumerate(result.path)
                if n.order_id == oid and n.location_type == "pickup"
            )
            drop_idx = next(
                i for i, n in enumerate(result.path)
                if n.order_id == oid and n.location_type == "drop"
            )
            self.assertLess(pickup_idx, drop_idx, f"Pickup must precede drop for {oid}")

    # ── Test: Wait time when executive arrives early ─────────────
    def test_wait_time_at_restaurant(self):
        """If prep time is very long, the executive should wait."""
        # Executive starts AT the restaurant location (0 travel time)
        executive = self._make_executive(12.9352, 77.6245)
        order = self._make_order(
            "O1",
            12.9352, 77.6245,  # restaurant at same location
            120,               # 2 hours prep time
            12.9279, 77.6271,  # consumer nearby
        )

        result = self.strategy.find_optimal_route(executive, [order])

        # Executive arrives instantly, waits 2 hours, then travels to consumer
        pickup_node = result.path[0]
        self.assertAlmostEqual(pickup_node.wait_time_hrs, 2.0, places=2)
        self.assertGreater(result.total_time_hrs, 2.0)

    # ── Test: Zero prep time (food is ready immediately) ─────────
    def test_zero_prep_time(self):
        """If prep time is 0, there should be no waiting."""
        executive = self._make_executive(12.9716, 77.5946)
        order = self._make_order("O1", 12.9352, 77.6245, 0, 12.9279, 77.6271)

        result = self.strategy.find_optimal_route(executive, [order])

        pickup_node = result.path[0]
        self.assertEqual(pickup_node.wait_time_hrs, 0.0)

    # ── Test: Optimality — closer restaurant should be picked first ──
    def test_optimal_picks_closer_restaurant_first(self):
        """
        Given one very close and one far restaurant,
        the optimal route should not start by going to the far one
        (assuming similar prep times and consumer locations).
        """
        executive = self._make_executive(12.9716, 77.5946)
        # O1: restaurant very close to executive
        o1 = self._make_order("O1", 12.9720, 77.5950, 10, 12.9750, 77.5960)
        # O2: restaurant far away
        o2 = self._make_order("O2", 13.0200, 77.6500, 10, 13.0250, 77.6520)

        result = self.strategy.find_optimal_route(executive, [o1, o2])

        # The first step should be picking up O1 (the closer one)
        self.assertEqual(result.path[0].order_id, "O1")
        self.assertEqual(result.path[0].location_type, "pickup")


if __name__ == "__main__":
    unittest.main()
