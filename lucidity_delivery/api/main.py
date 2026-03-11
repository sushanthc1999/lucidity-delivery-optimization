"""
FastAPI application for the Delivery Route Optimization API.

Provides a REST endpoint to calculate the optimal delivery route
for a batch of orders.
"""

import logging

from fastapi import FastAPI, HTTPException

from lucidity_delivery.engines.routing_strategy import BruteForceDeliveryStrategy
from lucidity_delivery.utils.distance import HaversineDistanceCalculator
from lucidity_delivery.api.schemas import (
    LocationPayload,
    OptimizeRouteRequest,
    OptimizeRouteResponse,
    RouteStepResponse,
)
from lucidity_delivery.api.mappers import to_domain_models
from lucidity_delivery.config import Config

# ── Logging ──────────────────────────────────────────────────────
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format=Config.LOG_FORMAT,
)
logger = logging.getLogger(__name__)

# ── FastAPI App ──────────────────────────────────────────────────
app = FastAPI(
    title="Lucidity Delivery Optimizer",
    description="Finds the optimal delivery route for a batch of N orders.",
    version="1.0.0",
)


# ── API Endpoint ─────────────────────────────────────────────────
@app.post("/api/v1/optimize-route", response_model=OptimizeRouteResponse)
def optimize_route(request: OptimizeRouteRequest):
    """
    Accepts a delivery executive and a list of orders.
    Returns the optimal route minimizing total delivery time.
    """
    try:
        executive, orders = to_domain_models(request)

        # Strategy Pattern: inject the distance calculator into the strategy
        distance_calculator = HaversineDistanceCalculator()
        strategy = BruteForceDeliveryStrategy(distance_calculator=distance_calculator)

        result = strategy.find_optimal_route(executive=executive, orders=orders)

        route_steps = [
            RouteStepResponse(
                step=idx + 1,
                action=node.location_type,
                order_id=node.order_id,
                location=LocationPayload(
                    latitude=node.location.latitude,
                    longitude=node.location.longitude,
                ),
                arrival_time_minutes=round(node.arrival_time_hrs * 60, 2),
                wait_time_minutes=round(node.wait_time_hrs * 60, 2),
            )
            for idx, node in enumerate(result.path)
        ]

        return OptimizeRouteResponse(
            status="success",
            total_time_minutes=round(result.total_time_hrs * 60, 2),
            route=route_steps,
        )

    except ValueError as e:
        logger.error("Validation error: %s", e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error during route optimization")
        raise HTTPException(status_code=500, detail="Internal server error")


# ── CLI Runner ───────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.SERVER_HOST, port=Config.SERVER_PORT)
