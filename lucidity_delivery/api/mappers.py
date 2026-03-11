"""
Mappers: Convert API payloads (schemas) → Domain models.

This module acts as the Anti-Corruption Layer between the API boundary
and the internal domain, ensuring that schema changes do not leak
into the business logic.
"""

from typing import List

from lucidity_delivery.core.base_entities import Location
from lucidity_delivery.domain.models import (
    Consumer,
    DeliveryExecutive,
    Order,
    Restaurant,
)
from lucidity_delivery.api.schemas import (
    ExecutivePayload,
    LocationPayload,
    OptimizeRouteRequest,
    OrderPayload,
)


def to_location(payload: LocationPayload) -> Location:
    """Converts a LocationPayload to a domain Location."""
    return Location(payload.latitude, payload.longitude)


def to_executive(payload: ExecutivePayload) -> DeliveryExecutive:
    """Converts an ExecutivePayload to a domain DeliveryExecutive."""
    return DeliveryExecutive(
        user_id=payload.user_id,
        name=payload.name,
        current_location=to_location(payload.current_location),
        speed=payload.speed_kmph,
    )


def to_order(payload: OrderPayload) -> Order:
    """Converts an OrderPayload to a domain Order."""
    restaurant = Restaurant(
        restaurant_id=payload.restaurant.restaurant_id,
        name=payload.restaurant.name,
        location=to_location(payload.restaurant.location),
        average_prep_time_hrs=payload.restaurant.average_prep_time_minutes / 60.0,
    )
    consumer = Consumer(
        user_id=payload.consumer.user_id,
        name=payload.consumer.name,
        location=to_location(payload.consumer.location),
    )
    return Order(order_id=payload.order_id, restaurant=restaurant, consumer=consumer)


def to_domain_models(
    request: OptimizeRouteRequest,
) -> tuple[DeliveryExecutive, List[Order]]:
    """Orchestrates conversion of the full request into domain objects."""
    executive = to_executive(request.executive)
    orders = [to_order(o) for o in request.orders]
    return executive, orders
