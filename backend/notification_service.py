"""
Notification Logging Service

This module provides functions for logging mock notifications to the notification_log table.
In the MVP, email notifications are mocked by logging them to the database instead of sending actual emails.
All notification log entries include order_id, notification_type, recipient_email, and relevant details.
"""

import json
from typing import Optional

from sqlmodel import Session

from models import NotificationLog, OrderHeader


def log_order_confirmation(
    order: OrderHeader,
    session: Session
) -> NotificationLog:
    """
    Log an order confirmation notification.
    
    This notification is sent when an order is successfully created.
    
    Args:
        order: The order that was created
        session: Database session
        
    Returns:
        The created NotificationLog record
    """
    details = json.dumps({
        "order_id": order.order_id,
        "dc_id": order.dc_id,
        "total_cost": str(order.total_cost),
        "order_date": order.order_date.isoformat(),
        "status": order.status
    })
    
    notification_log = NotificationLog(
        order_id=order.order_id,
        notification_type="order_confirmation",
        recipient_email=order.contact_email,
        details=details
    )
    
    session.add(notification_log)
    session.commit()
    session.refresh(notification_log)
    
    return notification_log


def log_invoice_notification(
    order: OrderHeader,
    session: Session
) -> NotificationLog:
    """
    Log an invoice notification.
    
    This notification is sent when an order is created and an invoice is generated.
    
    Args:
        order: The order for which the invoice was generated
        session: Database session
        
    Returns:
        The created NotificationLog record
    """
    details = json.dumps({
        "order_id": order.order_id,
        "dc_id": order.dc_id,
        "total_cost": str(order.total_cost),
        "order_date": order.order_date.isoformat(),
        "invoice_available": True
    })
    
    notification_log = NotificationLog(
        order_id=order.order_id,
        notification_type="invoice",
        recipient_email=order.contact_email,
        details=details
    )
    
    session.add(notification_log)
    session.commit()
    session.refresh(notification_log)
    
    return notification_log


def log_fulfillment_notification(
    order: OrderHeader,
    session: Session
) -> NotificationLog:
    """
    Log a fulfillment notification.
    
    This notification is sent when an order status changes to IN_FULFILLMENT.
    
    Args:
        order: The order that entered fulfillment
        session: Database session
        
    Returns:
        The created NotificationLog record
    """
    details = json.dumps({
        "order_id": order.order_id,
        "dc_id": order.dc_id,
        "total_cost": str(order.total_cost),
        "status": order.status,
        "order_date": order.order_date.isoformat()
    })
    
    notification_log = NotificationLog(
        order_id=order.order_id,
        notification_type="fulfillment",
        recipient_email=order.contact_email,
        details=details
    )
    
    session.add(notification_log)
    session.commit()
    session.refresh(notification_log)
    
    return notification_log


def log_shipping_notification(
    order: OrderHeader,
    session: Session
) -> NotificationLog:
    """
    Log a shipping notification.
    
    This notification is sent when an order status changes to SHIPPED.
    
    Args:
        order: The order that was shipped
        session: Database session
        
    Returns:
        The created NotificationLog record
    """
    details = json.dumps({
        "order_id": order.order_id,
        "dc_id": order.dc_id,
        "total_cost": str(order.total_cost),
        "status": order.status,
        "order_date": order.order_date.isoformat()
    })
    
    notification_log = NotificationLog(
        order_id=order.order_id,
        notification_type="shipping",
        recipient_email=order.contact_email,
        details=details
    )
    
    session.add(notification_log)
    session.commit()
    session.refresh(notification_log)
    
    return notification_log
