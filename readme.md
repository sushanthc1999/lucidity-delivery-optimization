# Delivery Route Optimization

A production-quality delivery route optimization engine that finds the shortest total time to deliver a batch of N orders using **DFS Backtracking with Branch Pruning**.

## Problem Statement

A delivery executive receives a batch of N orders simultaneously. Each order involves:
- Picking up food from a **Restaurant** (which has an average meal preparation time)
- Delivering it to a **Consumer**

The system computes the optimal sequence of pickups and deliveries that **minimizes total elapsed time**, accounting for travel time (Haversine formula at 20 km/hr) and restaurant wait times.

## Assumptions

1. All restaurants are informed simultaneously and start meal preparation at `t=0`.
2. Travel speed is constant at 20 km/hr (configurable via `config.py`).
3. No real-time location updates — this is a one-shot route optimization.
4. An order's food **must be picked up before it can be delivered** (precedence constraint).

## Project Structure

```
lucidity_delivery/
├── config.py                 # Centralized configuration (speed, port, logging)
├── core/
│   ├── base_entities.py      # Location (frozen dataclass), User (ABC)
│   └── interfaces.py         # DistanceCalculator, DeliveryStrategy (ABC)
├── domain/
│   └── models.py             # Consumer, DeliveryExecutive, Restaurant, Order, RouteResult
├── utils/
│   ├── distance.py           # HaversineDistanceCalculator
│   └── time_calc.py          # TimeCalculator
├── engines/
│   └── routing_strategy.py   # BruteForceDeliveryStrategy (DFS Backtracking)
├── api/
│   ├── main.py               # FastAPI endpoint
│   ├── schemas.py            # Request/Response Pydantic models
│   └── mappers.py            # API payload → Domain model conversion
└── tests/
    ├── test_distance.py      # Haversine accuracy & validation tests
    └── test_routing.py       # Routing logic & constraint tests
```

## Setup

```bash
# Clone the repo
git clone https://github.com/<your-username>/lucidity-delivery-optimization.git
cd lucidity-delivery-optimization

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Run Tests

```bash
python3 -m unittest discover -s lucidity_delivery/tests -v
```

**Expected output (12 tests):**
```
test_antipodal_points .......................... ok
test_koramangala_to_hsr ........................ ok
test_london_to_paris ........................... ok
test_same_location_returns_zero ................ ok
test_invalid_latitude .......................... ok
test_invalid_longitude ......................... ok
test_no_orders ................................. ok
test_optimal_picks_closer_restaurant_first ..... ok
test_single_order_path_structure ............... ok
test_two_orders_pickup_before_drop ............. ok
test_wait_time_at_restaurant ................... ok
test_zero_prep_time ............................ ok

Ran 12 tests in 0.001s — OK
```

## Run API Server

```bash
python3 -m lucidity_delivery.api.main
```
- **Server**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs

## API Usage

### `POST /api/v1/optimize-route`

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/optimize-route \
  -H "Content-Type: application/json" \
  -d '{
    "executive": {
      "user_id": "E1",
      "name": "Aman",
      "current_location": {"latitude": 12.9352, "longitude": 77.6245},
      "speed_kmph": 20.0
    },
    "orders": [
      {
        "order_id": "O1",
        "restaurant": {
          "restaurant_id": "R1", "name": "Meghana Foods",
          "location": {"latitude": 12.9279, "longitude": 77.6271},
          "average_prep_time_minutes": 30
        },
        "consumer": {
          "user_id": "C1", "name": "Ravi",
          "location": {"latitude": 12.9116, "longitude": 77.6389}
        }
      },
      {
        "order_id": "O2",
        "restaurant": {
          "restaurant_id": "R2", "name": "Truffles",
          "location": {"latitude": 12.9400, "longitude": 77.6150},
          "average_prep_time_minutes": 45
        },
        "consumer": {
          "user_id": "C2", "name": "Priya",
          "location": {"latitude": 12.9200, "longitude": 77.6500}
        }
      }
    ]
  }'
```

**Response:**
```json
{
  "status": "success",
  "total_time_minutes": 61.8,
  "route": [
    {"step": 1, "action": "pickup",  "order_id": "O1", "arrival_time_minutes": 5.2,  "wait_time_minutes": 24.8},
    {"step": 2, "action": "pickup",  "order_id": "O2", "arrival_time_minutes": 35.1, "wait_time_minutes": 9.9},
    {"step": 3, "action": "drop",    "order_id": "O1", "arrival_time_minutes": 52.3, "wait_time_minutes": 0},
    {"step": 4, "action": "drop",    "order_id": "O2", "arrival_time_minutes": 61.8, "wait_time_minutes": 0}
  ]
}
```

## Design Patterns & SOLID Principles

| Principle / Pattern | Implementation |
|---|---|
| **Strategy Pattern** | `DeliveryStrategy` ABC → `BruteForceDeliveryStrategy` (swappable for heuristic approaches) |
| **Dependency Inversion** | Routing engine depends on `DistanceCalculator` ABC, not concrete `Haversine` |
| **Liskov Substitution** | `Consumer` and `DeliveryExecutive` both extend `User` ABC |
| **Single Responsibility** | Each module has one job: distance math, time math, routing, API, mapping |
| **Interface Segregation** | `DistanceCalculator` exposes only `calculate_distance()` |
| **Open/Closed** | New strategies/calculators can be added without modifying existing code |
| **Immutable State** | Frozen dataclasses + new list copies per recursion branch prevent mutation bugs |

## Algorithm

**Approach:** Constrained DFS Backtracking with Branch Pruning

- Explores all valid permutations where each order's pickup precedes its delivery
- Handles restaurant wait times (if executive arrives before food is ready)
- Prunes branches that already exceed the current best time
- **Complexity:** O((2N)! / 2^N) — optimal for small batch sizes (N = 2–5)

## Extensibility

| Future Requirement | Change Required |
|---|---|
| Google Maps distance API | Add `GoogleMapsDistanceCalculator` implementing `DistanceCalculator` |
| Large N (20+ orders) | Add `HeuristicDeliveryStrategy` implementing `DeliveryStrategy` |
| Optimize average delivery time | New strategy using cumulative time tracking |
| New user types | Extend `User` ABC |
