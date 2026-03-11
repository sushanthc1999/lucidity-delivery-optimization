"""
API request and response schemas (Pydantic models).

Separates the API contract from the endpoint logic (Single Responsibility).
"""

from typing import List
from pydantic import BaseModel, Field


# ── Request Schemas ──────────────────────────────────────────────
class LocationPayload(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class RestaurantPayload(BaseModel):
    restaurant_id: str
    name: str
    location: LocationPayload
    average_prep_time_minutes: float = Field(..., ge=0, description="Prep time in minutes")


class ConsumerPayload(BaseModel):
    user_id: str
    name: str
    location: LocationPayload


class OrderPayload(BaseModel):
    order_id: str
    restaurant: RestaurantPayload
    consumer: ConsumerPayload


class ExecutivePayload(BaseModel):
    user_id: str
    name: str
    current_location: LocationPayload
    speed_kmph: float = Field(default=20.0, gt=0)


class OptimizeRouteRequest(BaseModel):
    executive: ExecutivePayload
    orders: List[OrderPayload]


# ── Response Schemas ─────────────────────────────────────────────
class RouteStepResponse(BaseModel):
    step: int
    action: str  # 'pickup' or 'drop'
    order_id: str
    location: LocationPayload
    arrival_time_minutes: float
    wait_time_minutes: float


class OptimizeRouteResponse(BaseModel):
    status: str
    total_time_minutes: float
    route: List[RouteStepResponse]
