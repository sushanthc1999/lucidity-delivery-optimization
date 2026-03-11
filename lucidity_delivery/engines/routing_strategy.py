"""
Brute Force Delivery Strategy using DFS Backtracking.

Explores all valid permutations of pickups and deliveries to find
the route with the minimum total elapsed time.

Constraint: For each order, the restaurant (pickup) must be visited
BEFORE the consumer (drop).

Time Complexity: O((2N)! / 2^N) — feasible for small N (2-5).
"""

import logging
from typing import List, Optional

from lucidity_delivery.core.base_entities import Location
from lucidity_delivery.core.interfaces import DistanceCalculator, DeliveryStrategy
from lucidity_delivery.domain.models import (
    DeliveryExecutive,
    Order,
    RouteNode,
    RouteResult,
)
from lucidity_delivery.utils.time_calc import TimeCalculator

logger = logging.getLogger(__name__)


class BruteForceDeliveryStrategy(DeliveryStrategy):
    """
    Implements the Strategy Pattern for route optimization.
    
    Uses DFS Backtracking to guarantee the mathematically optimal route
    for small batch sizes. Includes branch pruning to skip paths that
    are already worse than the current best.
    """

    def __init__(self, distance_calculator: DistanceCalculator):
        """
        Dependency Injection: receives an abstract DistanceCalculator,
        not a concrete HaversineDistanceCalculator.
        """
        self._distance_calculator = distance_calculator
        self._time_calculator = TimeCalculator()

    def find_optimal_route(
        self, executive: DeliveryExecutive, orders: List[Order]
    ) -> RouteResult:
        """
        Entry point for the algorithm.
        
        Args:
            executive: Delivery executive with starting location and speed.
            orders: All orders in the batch to be fulfilled.
            
        Returns:
            RouteResult with minimum total time and the optimal path.
        """
        if not orders:
            logger.info("No orders to deliver.")
            return RouteResult(total_time_hrs=0.0, path=[])

        logger.info(
            "Starting route optimization for %d orders from %s",
            len(orders), executive
        )

        # This list holds a single-element mutable reference for the DFS closure
        best_result: List[Optional[RouteResult]] = [None]

        self._dfs(
            current_location=executive.current_location,
            current_time=0.0,
            speed=executive.speed,
            unpicked_orders=list(orders),
            undelivered_orders=[],
            current_path=[],
            best_result=best_result,
        )

        result = best_result[0] if best_result[0] else RouteResult(total_time_hrs=0.0)
        logger.info("Optimal route found: %s", result)
        return result

    def _dfs(
        self,
        current_location: Location,
        current_time: float,
        speed: float,
        unpicked_orders: List[Order],
        undelivered_orders: List[Order],
        current_path: List[RouteNode],
        best_result: List[Optional[RouteResult]],
    ) -> None:
        """
        Recursive DFS with backtracking and pruning.
        
        Branches:
            A) Pick up any unpicked order (go to its restaurant).
            B) Drop off any order already in hand (go to its consumer).
        """
        # ── Pruning ──────────────────────────────────────────────
        # If we already have a completed route that's faster, abandon this branch
        if best_result[0] is not None and current_time >= best_result[0].total_time_hrs:
            return

        # ── Base Case ────────────────────────────────────────────
        # All orders picked up AND delivered
        if not unpicked_orders and not undelivered_orders:
            if best_result[0] is None or current_time < best_result[0].total_time_hrs:
                best_result[0] = RouteResult(
                    total_time_hrs=current_time,
                    path=list(current_path),  # snapshot the path
                )
            return

        # ── Branch A: Pick up an order ───────────────────────────
        for i, order in enumerate(unpicked_orders):
            restaurant_loc = order.restaurant.location

            # Travel to the restaurant
            distance = self._distance_calculator.calculate_distance(
                current_location, restaurant_loc
            )
            travel_time = self._time_calculator.calculate_travel_time(distance, speed)
            arrival_time = current_time + travel_time

            # Wait if meal isn't ready yet (prep started at t=0)
            wait_time = max(0.0, order.restaurant.average_prep_time_hrs - arrival_time)
            departure_time = arrival_time + wait_time

            # Build the route step
            pickup_node = RouteNode(
                location_type="pickup",
                order_id=order.order_id,
                location=restaurant_loc,
                arrival_time_hrs=arrival_time,
                wait_time_hrs=wait_time,
            )

            # Create new lists to maintain immutability across recursive branches
            new_unpicked = unpicked_orders[:i] + unpicked_orders[i + 1:]
            new_undelivered = undelivered_orders + [order]

            self._dfs(
                current_location=restaurant_loc,
                current_time=departure_time,
                speed=speed,
                unpicked_orders=new_unpicked,
                undelivered_orders=new_undelivered,
                current_path=current_path + [pickup_node],
                best_result=best_result,
            )

        # ── Branch B: Drop off an order already picked up ────────
        for i, order in enumerate(undelivered_orders):
            consumer_loc = order.consumer.location

            # Travel to the consumer
            distance = self._distance_calculator.calculate_distance(
                current_location, consumer_loc
            )
            travel_time = self._time_calculator.calculate_travel_time(distance, speed)
            arrival_time = current_time + travel_time

            # Build the route step
            drop_node = RouteNode(
                location_type="drop",
                order_id=order.order_id,
                location=consumer_loc,
                arrival_time_hrs=arrival_time,
                wait_time_hrs=0.0,
            )

            new_undelivered = undelivered_orders[:i] + undelivered_orders[i + 1:]

            self._dfs(
                current_location=consumer_loc,
                current_time=arrival_time,
                speed=speed,
                unpicked_orders=unpicked_orders,
                undelivered_orders=new_undelivered,
                current_path=current_path + [drop_node],
                best_result=best_result,
            )
