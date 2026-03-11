"""
Base entities for the delivery optimization system.

Contains foundational data classes and the User abstract base class
that Consumer and DeliveryExecutive inherit from.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    """
    Represents a geographic coordinate.
    Frozen to ensure immutability — locations should never be mutated in-place.
    """
    latitude: float
    longitude: float

    def __post_init__(self):
        if not (-90 <= self.latitude <= 90):
            raise ValueError(f"Latitude must be between -90 and 90, got {self.latitude}")
        if not (-180 <= self.longitude <= 180):
            raise ValueError(f"Longitude must be between -180 and 180, got {self.longitude}")


class User(ABC):
    """
    Abstract base class for all human actors in the system.
    Demonstrates Liskov Substitution — any subclass can replace User.
    """
    def __init__(self, user_id: str, name: str):
        self._user_id = user_id
        self._name = name

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    def get_location(self) -> Location:
        """Returns the primary location associated with this user."""
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._user_id}, name={self._name})"
