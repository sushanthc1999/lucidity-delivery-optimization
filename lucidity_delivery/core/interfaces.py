"""
Interfaces (Abstract Base Classes) for the delivery optimization system.

These enforce contracts via abc.ABC rather than relying on duck typing.
Demonstrates Dependency Inversion — high-level modules depend on these
abstractions, not on concrete implementations.
"""

from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING

from lucidity_delivery.core.base_entities import Location

#doubt
if TYPE_CHECKING:
    from lucidity_delivery.domain.models import Order, DeliveryExecutive, RouteResult

#doubt
class DistanceCalculator(ABC):
    """
    Interface for calculating distance between two geographic locations.
    
    Concrete implementations:
        - HaversineDistanceCalculator (current)
        - GoogleMapsDistanceCalculator (future extension)
    """
    @abstractmethod
    def calculate_distance(self, loc1: Location, loc2: Location) -> float:
        """
        Returns the distance in kilometers between two locations.
        """
        ...


class DeliveryStrategy(ABC):
    """
    Interface for the route optimization algorithm.
    
    Implements the Strategy Pattern — allows swapping algorithms
    without modifying the calling code.
    
    Concrete implementations:
        - BruteForceDeliveryStrategy (current, optimal for small N)
        - HeuristicDeliveryStrategy (future, for large N)
    """
    @abstractmethod
    def find_optimal_route(
        self, 
        executive: "DeliveryExecutive", 
        orders: List["Order"]
    ) -> "RouteResult":
        """
        Finds the optimal delivery route minimizing total elapsed time.
        
        Args:
            executive: The delivery executive with starting location and speed.
            orders: List of orders to be picked up and delivered.
            
        Returns:
            RouteResult containing the optimal path, total time, and route steps.
        """
        ...
