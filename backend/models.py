from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import uuid4

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, Boolean, Integer, DECIMAL, TIMESTAMP, ForeignKey, Index
from sqlalchemy.sql import func


def uuid_str() -> str:
    return str(uuid4())


class UserAccount(SQLModel, table=True):
    __tablename__ = "user_account"

    account_id: str = Field(
        default_factory=uuid_str,
        sa_column=Column(String(36), primary_key=True),
    )
    username: str = Field(sa_column=Column(String(100), unique=True, nullable=False))
    password_hash: str = Field(sa_column=Column(String(255), nullable=False))
    role: str = Field(sa_column=Column(String(50), nullable=False))
    is_active: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default="1"))
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp()),
    )

    orders: List["OrderHeader"] = Relationship(back_populates="account")


class AAFESDistributionCenter(SQLModel, table=True):
    __tablename__ = "aafes_distribution_center"

    dc_id: str = Field(default_factory=uuid_str, sa_column=Column(String(36), primary_key=True))
    facility_name: str = Field(sa_column=Column(String(200), nullable=False))
    address1: str = Field(sa_column=Column(String(200), nullable=False))
    address2: Optional[str] = Field(default=None, sa_column=Column(String(200), nullable=True))
    city: str = Field(sa_column=Column(String(100), nullable=False))
    state: str = Field(sa_column=Column(String(100), nullable=False))
    postal_code: str = Field(sa_column=Column(String(30), nullable=False))
    region: str = Field(sa_column=Column(String(100), nullable=False))

    orders: List["OrderHeader"] = Relationship(back_populates="distribution_center")


class ProductItem(SQLModel, table=True):
    __tablename__ = "product_item"

    product_id: str = Field(default_factory=uuid_str, sa_column=Column(String(36), primary_key=True))
    product_name: str = Field(sa_column=Column(String(200), nullable=False))
    base_cost: Decimal = Field(sa_column=Column(DECIMAL(10, 2), nullable=False))
    is_active: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default="1"))

    inventory_rows: List["InventoryStock"] = Relationship(back_populates="product")


class ProductColor(SQLModel, table=True):
    __tablename__ = "product_color"

    color_id: str = Field(default_factory=uuid_str, sa_column=Column(String(36), primary_key=True))
    color_name: str = Field(sa_column=Column(String(100), unique=True, nullable=False))

    inventory_rows: List["InventoryStock"] = Relationship(back_populates="color")


class CustomOption(SQLModel, table=True):
    __tablename__ = "custom_option"

    custom_id: str = Field(default_factory=uuid_str, sa_column=Column(String(36), primary_key=True))
    custom_type: str = Field(sa_column=Column(String(50), nullable=False))  # patriotic / branch
    branch_name: Optional[str] = Field(default=None, sa_column=Column(String(150), nullable=True))
    added_charge: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(DECIMAL(10, 2), nullable=False, server_default="0.00"),
    )

    order_items: List["OrderItem"] = Relationship(back_populates="custom_option")


class InventoryStock(SQLModel, table=True):
    __tablename__ = "inventory_stock"

    stock_id: str = Field(default_factory=uuid_str, sa_column=Column(String(36), primary_key=True))
    product_id: str = Field(sa_column=Column(String(36), ForeignKey("product_item.product_id"), nullable=False))
    color_id: str = Field(sa_column=Column(String(36), ForeignKey("product_color.color_id"), nullable=False))

    quantity_available: int = Field(default=0, sa_column=Column(Integer, nullable=False, server_default="0"))
    last_updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp()),
    )

    product: ProductItem = Relationship(back_populates="inventory_rows")
    color: ProductColor = Relationship(back_populates="inventory_rows")
    order_items: List["OrderItem"] = Relationship(back_populates="stock")


class OrderHeader(SQLModel, table=True):
    __tablename__ = "order_header"

    order_id: str = Field(default_factory=uuid_str, sa_column=Column(String(36), primary_key=True))
    account_id: str = Field(sa_column=Column(String(36), ForeignKey("user_account.account_id"), nullable=False))
    dc_id: str = Field(sa_column=Column(String(36), ForeignKey("aafes_distribution_center.dc_id"), nullable=False))

    order_date: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp()),
    )
    status: str = Field(sa_column=Column(String(50), nullable=False))
    contact_email: str = Field(sa_column=Column(String(200), nullable=False))
    total_cost: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(DECIMAL(12, 2), nullable=False, server_default="0.00"),
    )

    account: UserAccount = Relationship(back_populates="orders")
    distribution_center: AAFESDistributionCenter = Relationship(back_populates="orders")
    items: List["OrderItem"] = Relationship(back_populates="order")


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_item"

    detail_id: str = Field(default_factory=uuid_str, sa_column=Column(String(36), primary_key=True))
    order_id: str = Field(sa_column=Column(String(36), ForeignKey("order_header.order_id"), nullable=False))
    stock_id: str = Field(sa_column=Column(String(36), ForeignKey("inventory_stock.stock_id"), nullable=False))
    custom_id: Optional[str] = Field(default=None, sa_column=Column(String(36), ForeignKey("custom_option.custom_id"), nullable=True))

    quantity_ordered: int = Field(sa_column=Column(Integer, nullable=False))
    calculated_item_cost: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(DECIMAL(12, 2), nullable=False, server_default="0.00"),
    )

    order: OrderHeader = Relationship(back_populates="items")
    stock: InventoryStock = Relationship(back_populates="order_items")
    custom_option: Optional[CustomOption] = Relationship(back_populates="order_items")


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_log"
    __table_args__ = (
        Index("idx_audit_account_id", "account_id"),
        Index("idx_audit_order_id", "order_id"),
        Index("idx_audit_timestamp", "timestamp"),
    )

    log_id: str = Field(default_factory=uuid_str, sa_column=Column(String(36), primary_key=True))
    event_type: str = Field(sa_column=Column(String(100), nullable=False))
    account_id: Optional[str] = Field(default=None, sa_column=Column(String(36), ForeignKey("user_account.account_id"), nullable=True))
    order_id: Optional[str] = Field(default=None, sa_column=Column(String(36), ForeignKey("order_header.order_id"), nullable=True))
    stock_id: Optional[str] = Field(default=None, sa_column=Column(String(36), ForeignKey("inventory_stock.stock_id"), nullable=True))
    old_value: Optional[str] = Field(default=None, sa_column=Column(String(500), nullable=True))
    new_value: Optional[str] = Field(default=None, sa_column=Column(String(500), nullable=True))
    ip_address: Optional[str] = Field(default=None, sa_column=Column(String(50), nullable=True))
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp()),
    )
    details: Optional[str] = Field(default=None, sa_column=Column(String(1000), nullable=True))


class NotificationLog(SQLModel, table=True):
    __tablename__ = "notification_log"
    __table_args__ = (
        Index("idx_notification_order_id", "order_id"),
        Index("idx_notification_timestamp", "timestamp"),
    )

    notification_id: str = Field(default_factory=uuid_str, sa_column=Column(String(36), primary_key=True))
    order_id: str = Field(sa_column=Column(String(36), ForeignKey("order_header.order_id"), nullable=False))
    notification_type: str = Field(sa_column=Column(String(100), nullable=False))
    recipient_email: str = Field(sa_column=Column(String(200), nullable=False))
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp()),
    )
    details: Optional[str] = Field(default=None, sa_column=Column(String(1000), nullable=True))
