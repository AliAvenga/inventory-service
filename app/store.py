"""In-memory catalogue and stock for the demo. Reset with POST /api/inventory/test/reset."""
from __future__ import annotations

import threading
import uuid
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

LOW_STOCK_THRESHOLD = 5

_SEED: dict[str, dict[str, Any]] = {
    "P-100": {"id": "P-100", "name": "Espresso beans 1kg", "price": "24.90", "stock": 12},
    "P-200": {"id": "P-200", "name": "Ceramic mug", "price": "9.50", "stock": 30},
    "P-300": {"id": "P-300", "name": "Hand grinder", "price": "59.00", "stock": 4},
    "P-400": {"id": "P-400", "name": "Milk frother", "price": "34.00", "stock": 0},
}


class InventoryError(Exception):
    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status, self.code, self.message = status, code, message


class Inventory:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.reset()

    def reset(self) -> None:
        with self._lock:
            self.products = deepcopy(_SEED)
            self.reservations: dict[str, dict[str, Any]] = {}
            self.events: list[dict[str, Any]] = []

    def product(self, product_id: str) -> dict[str, Any]:
        found = self.products.get(product_id)
        if found is None:
            raise InventoryError(404, "product_not_found", f"Product {product_id} does not exist.")
        return found

    def publish(self, topic: str, payload: dict[str, Any]) -> None:
        self.events.insert(0, {"topic": topic, "payload": payload, "published_at": datetime.now(UTC).isoformat()})

    def reserve(self, product_id: str, quantity: int, order_ref: str) -> dict[str, Any]:
        with self._lock:
            product = self.product(product_id)
            if product["stock"] < quantity:
                raise InventoryError(409, "insufficient_stock",
                                     f"Only {product['stock']} of {product['name']} left.")
            product["stock"] -= quantity
            reservation = {"id": f"R-{uuid.uuid4().hex[:8].upper()}", "product_id": product_id,
                           "quantity": quantity, "order_ref": order_ref, "status": "reserved"}
            self.reservations[reservation["id"]] = reservation
            if product["stock"] <= LOW_STOCK_THRESHOLD:
                self.publish("inventory.stock.low", {"product_id": product_id, "stock": product["stock"]})
            return reservation

    def release(self, reservation_id: str) -> dict[str, Any]:
        with self._lock:
            reservation = self.reservations.get(reservation_id)
            if reservation is None:
                raise InventoryError(404, "reservation_not_found", f"Reservation {reservation_id} does not exist.")
            if reservation["status"] == "reserved":
                self.products[reservation["product_id"]]["stock"] += reservation["quantity"]
                reservation["status"] = "released"
            return reservation


inventory = Inventory()
