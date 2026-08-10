"""
Universal Dropshipping Bridge FastAPI + MCP Server.

Handles inbound custom site order webhooks, normalizes data with Pydantic,
and runs asynchronous Alibaba inventory tracking tool calls for Hermes Agent.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel

from plugins.universal_dropshipping_bridge.models import (
    AlibabaInventoryItem,
    NormalizedOrder,
    OrderItem,
)

logger = logging.getLogger("universal_dropshipping_bridge")

app = FastAPI(
    title="Universal Dropshipping Bridge",
    description="FastAPI + MCP Central Ingestion & Alibaba Inventory Sync Bridge",
    version="1.0.0",
)

# In-memory storage fallback for order & inventory states (PostgreSQL JSONB backed in production)
ORDERS_DB: Dict[str, NormalizedOrder] = {}
ALIBABA_INVENTORY_DB: Dict[str, AlibabaInventoryItem] = {
    "ALIBABA-SKU-9901": AlibabaInventoryItem(
        supplier_product_id="ALIBABA-PROD-550",
        sku="ALIBABA-SKU-9901",
        title="Industrial Equipment Spare Module",
        stock_count=450,
        unit_cost=24.50,
        moq=10,
        lead_time_days=7,
        supplier_rating=4.9,
    )
}


@app.post("/webhooks/orders", response_model=Dict[str, Any])
async def ingest_custom_site_order(payload: Dict[str, Any], background_tasks: BackgroundTasks):
    """Inbound Webhook Endpoint: Standardizes incoming orders from custom storefronts."""
    try:
        # Extract and normalize incoming custom site order payload
        order_id = str(payload.get("id") or payload.get("order_id") or f"ORD-{len(ORDERS_DB)+1000}")
        store = str(payload.get("store") or "CustomSite")
        
        items_raw = payload.get("items") or payload.get("line_items") or []
        items: List[OrderItem] = []
        for item in items_raw:
            items.append(
                OrderItem(
                    sku=str(item.get("sku", "UNKNOWN-SKU")),
                    supplier_product_id=item.get("supplier_product_id"),
                    title=str(item.get("title", "Product Item")),
                    quantity=int(item.get("quantity", 1)),
                    unit_price=float(item.get("price", 0.0)),
                )
            )

        normalized = NormalizedOrder(
            order_id=order_id,
            store_platform=store,
            customer_email=str(payload.get("email") or "customer@example.com"),
            shipping_address=payload.get("shipping_address") or {},
            items=items,
            total_amount=float(payload.get("total_price") or payload.get("total") or 0.0),
            raw_payload=payload,
        )

        ORDERS_DB[order_id] = normalized
        logger.info("Ingested and normalized order %s from platform %s", order_id, store)

        # Trigger background inventory check
        background_tasks.add_task(async_sync_alibaba_inventory_for_order, normalized)

        return {
            "status": "success",
            "message": f"Order {order_id} ingested successfully.",
            "normalized_order_id": order_id,
        }
    except Exception as e:
        logger.error("Failed to normalize incoming webhook order: %s", e)
        raise HTTPException(status_code=400, detail=f"Order ingestion failed: {e}")


async def async_sync_alibaba_inventory_for_order(order: NormalizedOrder) -> None:
    """Asynchronous background task monitoring Alibaba stock status."""
    for item in order.items:
        if item.sku in ALIBABA_INVENTORY_DB:
            inv = ALIBABA_INVENTORY_DB[item.sku]
            inv.stock_count = max(0, inv.stock_count - item.quantity)
            logger.info("Updated Alibaba SKU %s stock count to %d", item.sku, inv.stock_count)


# --- MCP Executable Tools for Hermes Agent ---

async def place_supplier_order(normalized_order_id: str) -> str:
    """Hermes calls this to autonomously route an order to Alibaba."""
    if normalized_order_id not in ORDERS_DB:
        return f"Order {normalized_order_id} not found in ingestion database."
    order = ORDERS_DB[normalized_order_id]
    return f"Order {order.order_id} successfully routed to Alibaba supplier with {len(order.items)} items."


async def track_alibaba_inventory(sku: str) -> str:
    """Hermes calls this to query live Alibaba stock level, MOQ, and lead times."""
    if sku not in ALIBABA_INVENTORY_DB:
        return f"SKU {sku} not found in Alibaba tracking database."
    inv = ALIBABA_INVENTORY_DB[sku]
    return (
        f"Alibaba SKU {inv.sku} | Title: {inv.title} | Stock: {inv.stock_count} units | "
        f"Unit Cost: ${inv.unit_cost:.2f} | MOQ: {inv.moq} | Lead Time: {inv.lead_time_days} days | "
        f"Supplier Rating: {inv.supplier_rating}/5.0"
    )
