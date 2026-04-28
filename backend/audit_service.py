"""
Audit Logging Service

This module provides functions for logging sensitive operations to the audit_log table.
All audit log entries include event_type, timestamp, and relevant context (user, order, inventory).
"""

import json
from datetime import datetime
from typing import Optional

from sqlmodel import Session

from models import AuditLog, UserAccount, OrderHeader, InventoryStock


def log_login(
    user: UserAccount,
    ip_address: str,
    success: bool,
    session: Session
) -> AuditLog:
    """
    Log a login attempt (successful or failed).
    
    Args:
        user: The user account attempting to log in
        ip_address: The IP address of the login attempt
        success: Whether the login was successful
        session: Database session
        
    Returns:
        The created AuditLog record
    """
    event_type = "login" if success else "login_failed"
    
    details = json.dumps({
        "username": user.username,
        "role": user.role,
        "success": success
    })
    
    audit_log = AuditLog(
        event_type=event_type,
        account_id=user.account_id,
        ip_address=ip_address,
        details=details
    )
    
    session.add(audit_log)
    session.commit()
    session.refresh(audit_log)
    
    return audit_log


def log_order_creation(
    order: OrderHeader,
    user: UserAccount,
    session: Session
) -> AuditLog:
    """
    Log the creation of a new order.
    
    Args:
        order: The order that was created
        user: The user who created the order
        session: Database session
        
    Returns:
        The created AuditLog record
    """
    details = json.dumps({
        "dc_id": order.dc_id,
        "contact_email": order.contact_email,
        "total_cost": str(order.total_cost),
        "status": order.status
    })
    
    audit_log = AuditLog(
        event_type="order_created",
        account_id=user.account_id,
        order_id=order.order_id,
        details=details
    )
    
    session.add(audit_log)
    session.commit()
    session.refresh(audit_log)
    
    return audit_log


def log_status_change(
    order: OrderHeader,
    old_status: str,
    new_status: str,
    user: UserAccount,
    session: Session
) -> AuditLog:
    """
    Log an order status change.
    
    Args:
        order: The order whose status was changed
        old_status: The previous status value
        new_status: The new status value
        user: The user who changed the status
        session: Database session
        
    Returns:
        The created AuditLog record
    """
    details = json.dumps({
        "order_id": order.order_id,
        "dc_id": order.dc_id,
        "contact_email": order.contact_email
    })
    
    audit_log = AuditLog(
        event_type="status_updated",
        account_id=user.account_id,
        order_id=order.order_id,
        old_value=old_status,
        new_value=new_status,
        details=details
    )
    
    session.add(audit_log)
    session.commit()
    session.refresh(audit_log)
    
    return audit_log


def log_inventory_adjustment(
    stock: InventoryStock,
    quantity_change: int,
    user: UserAccount,
    session: Session
) -> AuditLog:
    """
    Log an inventory quantity adjustment.
    
    Args:
        stock: The inventory stock that was adjusted
        quantity_change: The amount of change (positive for additions, negative for removals)
        user: The user who made the adjustment
        session: Database session
        
    Returns:
        The created AuditLog record
    """
    details = json.dumps({
        "product_id": stock.product_id,
        "color_id": stock.color_id,
        "quantity_change": quantity_change,
        "new_quantity": stock.quantity_available
    })
    
    audit_log = AuditLog(
        event_type="inventory_adjusted",
        account_id=user.account_id,
        stock_id=stock.stock_id,
        old_value=str(stock.quantity_available - quantity_change),
        new_value=str(stock.quantity_available),
        details=details
    )
    
    session.add(audit_log)
    session.commit()
    session.refresh(audit_log)
    
    return audit_log
