"""
Invoice Service for AAFES Order Management MVP

This module provides invoice generation functionality for orders.
Generates HTML invoices using Jinja2 templates.

Validates: Requirements 7.1, 7.2, 7.3, 7.4
"""

from sqlmodel import Session, select
from jinja2 import Template
from models import (
    OrderHeader,
    OrderItem,
    AAFESDistributionCenter,
    InventoryStock,
    ProductItem,
    ProductColor,
    CustomOption,
)


def generate_invoice_html(order_id: str, session: Session) -> str:
    """
    Generate HTML invoice for an order.
    
    Validates: Requirements 7.1, 7.2, 7.3, 7.4
    
    Args:
        order_id: The order ID to generate invoice for
        session: Database session
        
    Returns:
        HTML string containing the formatted invoice
        
    Raises:
        ValueError: If order not found or missing required data
    """
    # Query order with all related data
    order = session.get(OrderHeader, order_id)
    if not order:
        raise ValueError(f"Order not found: {order_id}")
    
    # Get distribution center details
    dc = session.get(AAFESDistributionCenter, order.dc_id)
    if not dc:
        raise ValueError(f"Distribution center not found for order: {order_id}")
    
    # Get order items with all related details
    order_items = session.exec(
        select(OrderItem).where(OrderItem.order_id == order_id)
    ).all()
    
    if not order_items:
        raise ValueError(f"No order items found for order: {order_id}")
    
    # Build line items with product, color, and customization details
    line_items = []
    for item in order_items:
        # Get inventory stock
        stock = session.get(InventoryStock, item.stock_id)
        if not stock:
            continue
        
        # Get product details
        product = session.get(ProductItem, stock.product_id)
        if not product:
            continue
        
        # Get color details
        color = session.get(ProductColor, stock.color_id)
        if not color:
            continue
        
        # Get customization details (if any)
        customization = None
        if item.custom_id:
            custom_option = session.get(CustomOption, item.custom_id)
            if custom_option:
                if custom_option.custom_type == "patriotic":
                    customization = "Patriotic"
                elif custom_option.custom_type == "branch" and custom_option.branch_name:
                    customization = f"{custom_option.branch_name} Branch"
                else:
                    customization = custom_option.custom_type.capitalize()
        
        line_items.append({
            "product_name": product.product_name,
            "color_name": color.color_name,
            "quantity": item.quantity_ordered,
            "customization": customization if customization else "None",
            "cost": f"${item.calculated_item_cost:.2f}",
        })
    
    # Jinja2 template for HTML invoice
    invoice_template = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Invoice - Order {{ order_id }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .invoice-container {
            background-color: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #0066cc;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }
        .invoice-header {
            margin-bottom: 30px;
        }
        .invoice-info {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        .info-section {
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 4px;
        }
        .info-label {
            font-weight: bold;
            color: #666;
            font-size: 12px;
            text-transform: uppercase;
            margin-bottom: 5px;
        }
        .info-value {
            color: #333;
            font-size: 14px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }
        thead {
            background-color: #0066cc;
            color: white;
        }
        th {
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
        }
        tbody tr:hover {
            background-color: #f9f9f9;
        }
        .total-section {
            text-align: right;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 2px solid #333;
        }
        .total-label {
            font-size: 18px;
            font-weight: bold;
            color: #333;
        }
        .total-amount {
            font-size: 24px;
            font-weight: bold;
            color: #0066cc;
            margin-left: 20px;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            text-align: center;
            color: #666;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="invoice-container">
        <div class="invoice-header">
            <h1>INVOICE</h1>
        </div>
        
        <div class="invoice-info">
            <div class="info-section">
                <div class="info-label">Order ID</div>
                <div class="info-value">{{ order_id }}</div>
            </div>
            <div class="info-section">
                <div class="info-label">Order Date</div>
                <div class="info-value">{{ order_date }}</div>
            </div>
            <div class="info-section">
                <div class="info-label">Distribution Center</div>
                <div class="info-value">
                    {{ dc_facility_name }}<br>
                    {{ dc_address1 }}<br>
                    {% if dc_address2 %}{{ dc_address2 }}<br>{% endif %}
                    {{ dc_city }}, {{ dc_state }} {{ dc_postal_code }}<br>
                    Region: {{ dc_region }}
                </div>
            </div>
            <div class="info-section">
                <div class="info-label">Contact Email</div>
                <div class="info-value">{{ contact_email }}</div>
            </div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Product</th>
                    <th>Color</th>
                    <th>Quantity</th>
                    <th>Customization</th>
                    <th style="text-align: right;">Cost</th>
                </tr>
            </thead>
            <tbody>
                {% for item in line_items %}
                <tr>
                    <td>{{ item.product_name }}</td>
                    <td>{{ item.color_name }}</td>
                    <td>{{ item.quantity }}</td>
                    <td>{{ item.customization }}</td>
                    <td style="text-align: right;">{{ item.cost }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <div class="total-section">
            <span class="total-label">Total:</span>
            <span class="total-amount">${{ total_cost }}</span>
        </div>
        
        <div class="footer">
            <p>Thank you for your order!</p>
            <p>AAFES Order Management System</p>
        </div>
    </div>
</body>
</html>
    """)
    
    # Render the template with order data
    html = invoice_template.render(
        order_id=order.order_id,
        order_date=order.order_date.strftime("%B %d, %Y at %I:%M %p"),
        dc_facility_name=dc.facility_name,
        dc_address1=dc.address1,
        dc_address2=dc.address2,
        dc_city=dc.city,
        dc_state=dc.state,
        dc_postal_code=dc.postal_code,
        dc_region=dc.region,
        contact_email=order.contact_email,
        line_items=line_items,
        total_cost=f"{order.total_cost:.2f}",
    )
    
    return html
