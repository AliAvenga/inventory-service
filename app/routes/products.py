"""The catalogue the storefront shows: products, prices and stock."""
from fastapi import APIRouter

from app.store import inventory

router = APIRouter(prefix="/api/inventory", tags=["products"])


@router.get("/products")
def list_products() -> dict:
    return {"products": list(inventory.products.values())}


@router.get("/products/{product_id}")
def get_product(product_id: str) -> dict:
    return inventory.product(product_id)
