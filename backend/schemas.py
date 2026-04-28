from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import field_validator
from sqlmodel import SQLModel, Field


# ---------- User Schemas ----------

class UserCreate(SQLModel):
    username: str = Field(max_length=100)
    password: str = Field(min_length=8, max_length=128)
    role: str = Field(max_length=50)


class UserRead(SQLModel):
    account_id: str
    username: str
    role: str
    is_active: bool
    created_at: datetime


# ---------- Distribution Center Schemas ----------

class DistributionCenterCreate(SQLModel):
    facility_name: str = Field(max_length=200)
    address1: str = Field(max_length=200)
    address2: Optional[str] = Field(default=None, max_length=200)
    city: str = Field(max_length=100)
    state: str = Field(max_length=100)
    postal_code: str = Field(max_length=30)
    region: str = Field(max_length=100)


class DistributionCenterRead(SQLModel):
    dc_id: str
    facility_name: str
    address1: str
    address2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    region: str


# ---------- Product Schemas ----------

class ProductCreate(SQLModel):
    product_name: str = Field(max_length=200)
    base_cost: Decimal = Field(ge=Decimal("0.00"), max_digits=10, decimal_places=2)
    is_active: bool = True


class ProductRead(SQLModel):
    product_id: str
    product_name: str
    base_cost: Decimal
    is_active: bool


class ProductColorCreate(SQLModel):
    color_name: str = Field(max_length=100)


class ProductColorRead(SQLModel):
    color_id: str
    color_name: str


# ---------- Custom Option Schemas ----------

class CustomOptionCreate(SQLModel):
    custom_type: str = Field(max_length=50)
    branch_name: Optional[str] = Field(default=None, max_length=150)
    added_charge: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0.00"),
        max_digits=10,
        decimal_places=2,
    )


class CustomOptionRead(SQLModel):
    custom_id: str
    custom_type: str
    branch_name: Optional[str] = None
    added_charge: Decimal


# ---------- Inventory Schemas ----------

class InventoryStockCreate(SQLModel):
    product_id: str
    color_id: str
    quantity_available: int = 0


class InventoryStockUpdate(SQLModel):
    quantity_available: int


class InventoryAdjust(SQLModel):
    quantity_change: int


class InventoryStockRead(SQLModel):
    stock_id: str
    product_id: str
    color_id: str
    quantity_available: int
    last_updated_at: datetime


# ---------- Order Schemas ----------

class OrderCreate(SQLModel):
    account_id: str
    dc_id: str
    contact_email: str = Field(max_length=200)
    status: str = Field(default="Pending", max_length=50)

    @field_validator("contact_email")
    @classmethod
    def validate_contact_email(cls, value: str) -> str:
        email = value.strip()
        if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
            raise ValueError("contact_email must be a valid email address")
        return email


class OrderRead(SQLModel):
    order_id: str
    account_id: str
    dc_id: str
    order_date: datetime
    status: str
    contact_email: str
    total_cost: Decimal


class OrderStatusUpdate(SQLModel):
    status: str = Field(max_length=50)


class OrderItemCreate(SQLModel):
    order_id: str
    stock_id: str
    custom_id: Optional[str] = None
    quantity_ordered: int = Field(gt=0)
    calculated_item_cost: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0.00"),
        max_digits=12,
        decimal_places=2,
    )


class OrderItemRead(SQLModel):
    detail_id: str
    order_id: str
    stock_id: str
    custom_id: Optional[str] = None
    quantity_ordered: int
    calculated_item_cost: Decimal


# ---------- Authentication Schemas ----------

class LoginRequest(SQLModel):
    username: str = Field(max_length=100)
    password: str = Field(min_length=8, max_length=128)


class UserInfo(SQLModel):
    account_id: str
    username: str
    role: str


class LoginResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 28800  # 8 hours in seconds
    user: UserInfo


# ---------- Audit Log Schemas ----------

class AuditLogCreate(SQLModel):
    event_type: str = Field(max_length=100)
    account_id: Optional[str] = None
    order_id: Optional[str] = None
    stock_id: Optional[str] = None
    old_value: Optional[str] = Field(default=None, max_length=500)
    new_value: Optional[str] = Field(default=None, max_length=500)
    ip_address: Optional[str] = Field(default=None, max_length=50)
    details: Optional[str] = Field(default=None, max_length=1000)


class AuditLogRead(SQLModel):
    log_id: str
    event_type: str
    account_id: Optional[str] = None
    order_id: Optional[str] = None
    stock_id: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime
    details: Optional[str] = None


# ---------- Notification Log Schemas ----------

class NotificationLogCreate(SQLModel):
    order_id: str
    notification_type: str = Field(max_length=100)
    recipient_email: str = Field(max_length=200)
    details: Optional[str] = Field(default=None, max_length=1000)


class NotificationLogRead(SQLModel):
    notification_id: str
    order_id: str
    notification_type: str
    recipient_email: str
    timestamp: datetime
    details: Optional[str] = None


# ---------- Order Creation Request Schema ----------

class OrderItemCreateRequest(SQLModel):
    stock_id: str
    quantity_ordered: int = Field(gt=0)
    custom_id: Optional[str] = None


class OrderCreateRequest(SQLModel):
    dc_id: str
    contact_email: str = Field(max_length=200)
    items: list[OrderItemCreateRequest]

    @field_validator("contact_email")
    @classmethod
    def validate_contact_email(cls, value: str) -> str:
        email = value.strip()
        if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
            raise ValueError("contact_email must be a valid email address")
        return email
