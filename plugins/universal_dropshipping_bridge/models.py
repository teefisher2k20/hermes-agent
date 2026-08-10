"""
Pydantic Data Normalization & PostgreSQL JSONB Database Schemas
for the Universal Dropshipping Bridge.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class OrderItem(BaseModel):
    sku: str
    supplier_product_id: Optional[str] = None
    title: str
    quantity: int
    unit_price: float


class NormalizedOrder(BaseModel):
    order_id: str
    store_platform: str = Field(description="CustomSite, Shopify, WooCommerce")
    customer_email: str
    shipping_address: Dict[str, Any]
    items: List[OrderItem]
    total_amount: float
    currency: str = "USD"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    raw_payload: Optional[Dict[str, Any]] = None


class AlibabaInventoryItem(BaseModel):
    supplier_product_id: str
    sku: str
    title: str
    stock_count: int
    unit_cost: float
    moq: int
    lead_time_days: int
    supplier_rating: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)
