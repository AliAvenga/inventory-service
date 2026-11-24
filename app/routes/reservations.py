"""Reserving stock for an order at checkout, and releasing it when an order is cancelled."""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.store import inventory

router = APIRouter(prefix="/api/inventory", tags=["reservations"])


class ReservationRequest(BaseModel):
    product_id: str
    quantity: int = Field(gt=0, le=20)
    order_ref: str = Field(min_length=1, max_length=40)


@router.post("/reservations", status_code=201)
def reserve(request: ReservationRequest) -> dict:
    """409 `insufficient_stock` when there is not enough; publishes `inventory.stock.low` when stock runs low."""
    return inventory.reserve(request.product_id, request.quantity, request.order_ref)


@router.delete("/reservations/{reservation_id}")
def release(reservation_id: str) -> dict:
    return inventory.release(reservation_id)
