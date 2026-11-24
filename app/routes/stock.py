"""Stock levels, for the storefront's availability badges."""
from fastapi import APIRouter

from app.store import LOW_STOCK_THRESHOLD, inventory

router = APIRouter(prefix="/api/inventory", tags=["stock"])


@router.get("/stock/{product_id}")
def stock_level(product_id: str) -> dict:
    product = inventory.product(product_id)
    level = "out" if product["stock"] == 0 else "low" if product["stock"] <= LOW_STOCK_THRESHOLD else "in"
    return {"product_id": product_id, "stock": product["stock"], "level": level}
