"""Inventory service of the demo shop: catalogue, stock levels and reservations."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.routes import products, reservations, stock
from app.store import InventoryError, inventory

app = FastAPI(title="Inventory service", version="0.1.0")
for module in (products, stock, reservations):
    app.include_router(module.router)


@app.exception_handler(InventoryError)
def inventory_error(_: Request, error: InventoryError) -> JSONResponse:
    return JSONResponse(status_code=error.status, content={"error": error.code, "message": error.message})


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "inventory-service"}


@app.get("/api/inventory/events")
def events(topic: str | None = None) -> dict:
    """Events the service published (newest first), for example `inventory.stock.low`."""
    return {"events": [event for event in inventory.events if topic is None or event["topic"] == topic]}


@app.post("/api/inventory/test/reset", status_code=204)
def reset() -> None:
    """Back to the seeded catalogue, so every test starts from the same stock."""
    inventory.reset()
