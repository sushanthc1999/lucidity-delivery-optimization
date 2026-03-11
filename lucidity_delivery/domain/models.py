"""
Domain models for the delivery optimization system.

Contains concrete entities: Consumer, DeliveryExecutive, Restaurant, Order.
Also contains RouteNode and RouteResult for representing algorithm output.
"""

from dataclasses import dataclass, field
from typing import List

from lucidity_delivery.core.base_entities import Location, User
from lucidity_delivery.config import Config


class Consumer(User):
    """
    A consumer who has placed an order.
    Inherits from User (Liskov Substitution Principle).
    """
    def __init__(self, user_id: str, name: str, location: Location):
        super().__init__(user_id, name)
        self._location = location

    @property
    def location(self) -> Location:
        return self._location

    def get_location(self) -> Location:
        return self._location


class DeliveryExecutive(User):
    """
    A delivery executive (e.g. Aman) who picks up and delivers orders.
    Inherits from User (Liskov Substitution Principle).
    """
    def __init__(
        self, 
        user_id: str, 
        name: str, 
        current_location: Location,
        speed: float = Config.DEFAULT_SPEED_KMPH
    ):
        super().__init__(user_id, name)
        if speed <= 0:
            raise ValueError(f"Speed must be positive, got {speed}")
        self._current_location = current_location
        self._speed = speed

    @property
    def current_location(self) -> Location:
        return self._current_location

    @property
    def speed(self) -> float:
        return self._speed

    def get_location(self) -> Location:
        return self._current_location


@dataclass(frozen=True)
class Restaurant:
    """
    Represents a restaurant that fulfills orders.
    Frozen for immutability.
    """
    restaurant_id: str
    name: str
    location: Location
    average_prep_time_hrs: float  # in hours

    def __post_init__(self):
        if self.average_prep_time_hrs < 0:
            raise ValueError(
                f"Prep time cannot be negative, got {self.average_prep_time_hrs}"
            )


@dataclass(frozen=True)
class Order:
    """
    Links a Consumer to a Restaurant.
    Frozen for immutability — an order's details should not change mid-route.
    """
    order_id: str
    restaurant: Restaurant
    consumer: Consumer


@dataclass(frozen=True)
class RouteNode:
    """
    Represents a single step in the delivery route.
    location_type is either 'pickup' or 'drop'.
    """
    location_type: str  # 'pickup' or 'drop'
    order_id: str
    location: Location
    arrival_time_hrs: float
    wait_time_hrs: float = 0.0

    def __post_init__(self):
        if self.location_type not in ("pickup", "drop"):
            raise ValueError(
                f"location_type must be 'pickup' or 'drop', got '{self.location_type}'"
            )


@dataclass
class RouteResult:
    """
    The final output of the routing algorithm.
    Contains the total time, the ordered path, and details for each step.
    """
    total_time_hrs: float
    path: List[RouteNode] = field(default_factory=list)

    @property
    def total_time_minutes(self) -> float:
        return self.total_time_hrs * 60

    def __repr__(self) -> str:
        steps = " → ".join(
            f"{node.location_type.upper()}({node.order_id})" for node in self.path
        )
        return (
            f"RouteResult(total_time={self.total_time_minutes:.1f} mins, "
            f"path=[{steps}])"
        )
