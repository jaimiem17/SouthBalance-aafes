from __future__ import annotations

import base64
import hashlib
import secrets
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from database import get_session, init_db
from models import (
    UserAccount,
    AAFESDistributionCenter,
    ProductItem,
    ProductColor,
    CustomOption,
    InventoryStock,
    OrderHeader,
    OrderItem,
    AuditLog,
    NotificationLog,
)
import schemas
from schemas import (
    UserCreate,
    UserRead,
    DistributionCenterCreate,
    ProductCreate,
    ProductColorCreate,
    CustomOptionCreate,
    InventoryStockCreate,
    InventoryAdjust,
    OrderCreate,
    OrderStatusUpdate,
    OrderItemCreate,
    LoginRequest,
    LoginResponse,
    UserInfo,
    AuditLogRead,
    NotificationLogRead,
)
from auth import authenticate_user, create_jwt_token
from authorization import require_role, get_current_user


PASSWORD_HASH_ITERATIONS = 600_000


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_HASH_ITERATIONS,
    )
    encoded_salt = base64.b64encode(salt).decode("ascii")
    encoded_digest = base64.b64encode(digest).decode("ascii")
    return f"pbkdf2_sha256${PASSWORD_HASH_ITERATIONS}${encoded_salt}${encoded_digest}"


app = FastAPI(
    title="South Balance AAFES MVP API",
    description="Starter FastAPI backend for South Balance order and inventory management",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods including OPTIONS
    allow_headers=["*"],  # Allow all headers
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/")
def root():
    return {
        "message": "South Balance API is running",
        "docs": "/docs",
        "entities": [
            "users",
            "distribution-centers",
            "products",
            "colors",
            "custom-options",
            "inventory",
            "orders",
            "order-items",
        ],
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


#   Authentication  

@app.post("/api/auth/login", response_model=LoginResponse)
def login(
    credentials: LoginRequest,
    request: Request,
    session: Session = Depends(get_session),
):
    """
    Authenticate user and return JWT token.
    
    Validates: Requirements 1.1, 1.2, 11.1, 11.2
    
    - Authenticates user with username and password
    - Returns JWT token with 8-hour expiration on success
    - Logs successful login to audit_log with account_id, timestamp, and IP address
    - Logs failed login to audit_log with username, timestamp, and IP address
    - Returns 401 Unauthorized for invalid credentials
    """
    # Get client IP address
    ip_address = request.client.host if request.client else None
    
    # Attempt to authenticate user
    user = authenticate_user(credentials.username, credentials.password, session)
    
    if not user:
        # Log failed login attempt
        failed_login_log = AuditLog(
            event_type="login_failed",
            account_id=None,  # No account_id for failed login
            ip_address=ip_address,
            details=f"Failed login attempt for username: {credentials.username}",
        )
        session.add(failed_login_log)
        session.commit()
        
        # Return 401 Unauthorized
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate JWT token
    access_token = create_jwt_token(user)
    
    # Log successful login
    successful_login_log = AuditLog(
        event_type="login",
        account_id=user.account_id,
        ip_address=ip_address,
        details=f"Successful login for user: {user.username}",
    )
    session.add(successful_login_log)
    session.commit()
    
    # Return token and user info
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=28800,  # 8 hours in seconds
        user=UserInfo(
            account_id=user.account_id,
            username=user.username,
            role=user.role,
        ),
    )


@app.post("/api/auth/logout")
def logout():
    """
    Logout endpoint (client-side token removal).
    
    Validates: Requirements 1.1
    
    - JWT tokens are stateless, so logout is primarily client-side
    - Client should remove token from localStorage
    - Returns success message
    """
    return {"message": "Logged out successfully"}


#   Users  

@app.post("/api/users", response_model=dict)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    existing = session.exec(
        select(UserAccount).where(UserAccount.username == user.username)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    db_user = UserAccount(
        account_id=str(uuid4()),
        username=user.username,
        password_hash=hash_password(user.password),
        role=user.role,
        is_active=True,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return {"message": "User created", "account_id": db_user.account_id}


@app.get("/api/users", response_model=list[UserRead])
def get_users(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    session: Session = Depends(get_session),
):
    return session.exec(select(UserAccount).offset(offset).limit(limit)).all()


#   Distribution Centers  

@app.post("/api/distribution-centers", response_model=dict)
def create_distribution_center(
    dc: DistributionCenterCreate, session: Session = Depends(get_session)
):
    db_dc = AAFESDistributionCenter(
        dc_id=str(uuid4()),
        facility_name=dc.facility_name,
        address1=dc.address1,
        address2=dc.address2,
        city=dc.city,
        state=dc.state,
        postal_code=dc.postal_code,
        region=dc.region,
    )
    session.add(db_dc)
    session.commit()
    session.refresh(db_dc)

    return {"message": "Distribution center created", "dc_id": db_dc.dc_id}


@app.get("/api/distribution-centers")
def get_distribution_centers(session: Session = Depends(get_session)):
    return session.exec(select(AAFESDistributionCenter)).all()


#   Products  

@app.post("/api/products", response_model=dict)
def create_product(product: ProductCreate, session: Session = Depends(get_session)):
    db_product = ProductItem(
        product_id=str(uuid4()),
        product_name=product.product_name,
        base_cost=product.base_cost,
        is_active=product.is_active,
    )
    session.add(db_product)
    session.commit()
    session.refresh(db_product)

    return {"message": "Product created", "product_id": db_product.product_id}


@app.get("/api/products")
def get_products(session: Session = Depends(get_session)):
    return session.exec(select(ProductItem)).all()


#   Colors  

@app.post("/api/colors", response_model=dict)
def create_color(color: ProductColorCreate, session: Session = Depends(get_session)):
    existing = session.exec(
        select(ProductColor).where(ProductColor.color_name == color.color_name)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Color already exists")

    db_color = ProductColor(
        color_id=str(uuid4()),
        color_name=color.color_name,
    )
    session.add(db_color)
    session.commit()
    session.refresh(db_color)

    return {"message": "Color created", "color_id": db_color.color_id}


@app.get("/api/colors")
def get_colors(session: Session = Depends(get_session)):
    return session.exec(select(ProductColor)).all()


#   Custom Options  

@app.post("/api/custom-options", response_model=dict)
def create_custom_option(
    custom_option: CustomOptionCreate, session: Session = Depends(get_session)
):
    db_custom = CustomOption(
        custom_id=str(uuid4()),
        custom_type=custom_option.custom_type,
        branch_name=custom_option.branch_name,
        added_charge=custom_option.added_charge,
    )
    session.add(db_custom)
    session.commit()
    session.refresh(db_custom)

    return {"message": "Custom option created", "custom_id": db_custom.custom_id}


@app.get("/api/custom-options")
def get_custom_options(session: Session = Depends(get_session)):
    return session.exec(select(CustomOption)).all()


#  Inventory

@app.post("/api/inventory", response_model=dict)
def create_inventory_stock(
    stock: InventoryStockCreate, session: Session = Depends(get_session)
):
    product = session.get(ProductItem, stock.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    color = session.get(ProductColor, stock.color_id)
    if not color:
        raise HTTPException(status_code=404, detail="Color not found")

    db_stock = InventoryStock(
        stock_id=str(uuid4()),
        product_id=stock.product_id,
        color_id=stock.color_id,
        quantity_available=stock.quantity_available,
    )
    session.add(db_stock)
    session.commit()
    session.refresh(db_stock)

    return {"message": "Inventory row created", "stock_id": db_stock.stock_id}


@app.get("/api/inventory")
def get_inventory(session: Session = Depends(get_session)):
    return session.exec(select(InventoryStock)).all()


@app.patch("/api/inventory/{stock_id}/adjust", response_model=dict)
def adjust_inventory(
    stock_id: str,
    adjustment: InventoryAdjust,
    session: Session = Depends(get_session),
    user: UserAccount = Depends(require_role(["Inventory_Manager", "Admin"])),
):
    """
    Adjust inventory quantity with audit logging.
    
    Validates: Requirements 12.1, 12.2, 12.3, 11.5
    
    - Validates adjustment would not result in negative inventory
    - If valid: updates inventory quantity, logs to audit_log with quantity_change
    - If invalid: returns 400 Bad Request
    - Returns 200 OK with updated inventory
    """
    from audit_service import log_inventory_adjustment
    
    stock = session.get(InventoryStock, stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Inventory stock not found")

    new_qty = stock.quantity_available + adjustment.quantity_change
    if new_qty < 0:
        raise HTTPException(status_code=400, detail="Inventory cannot go negative")

    stock.quantity_available = new_qty
    session.add(stock)
    session.commit()
    session.refresh(stock)
    
    # Log inventory adjustment to audit_log
    log_inventory_adjustment(stock, adjustment.quantity_change, user, session)

    return {
        "message": "Inventory updated",
        "stock_id": stock.stock_id,
        "quantity_available": stock.quantity_available,
    }


#   Orders  

@app.post("/api/orders/create", response_model=dict, status_code=201)
def create_order_with_validation(
    order_request: schemas.OrderCreateRequest,
    request: Request,
    session: Session = Depends(get_session),
    user: UserAccount = Depends(require_role(["Salesperson", "Admin"])),
):
    """
    Create order with real-time inventory validation and atomic transactions.
    
    Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 6.2, 6.3, 6.4, 6.5, 8.1, 8.2, 11.3
    
    - Validates distribution center exists
    - For each item: validates stock exists, checks quantity_available >= quantity_ordered
    - Calculates item cost: (base_cost × quantity) + (added_charge × quantity) if custom_id provided
    - If all items valid: BEGIN TRANSACTION, decrement inventory, create order_header, create order_item records, COMMIT
    - If any item invalid: ROLLBACK and return 400 with out_of_stock_items list
    - After successful order creation: log to audit_log, log order_confirmation and invoice notifications
    - Returns 201 Created with order_id and total_cost
    """
    from audit_service import log_order_creation
    from notification_service import log_order_confirmation, log_invoice_notification
    
    # Validate distribution center exists
    dc = session.get(AAFESDistributionCenter, order_request.dc_id)
    if not dc:
        raise HTTPException(status_code=404, detail="Distribution center not found")
    
    # Validate all items and check inventory availability
    out_of_stock_items = []
    validated_items = []
    
    for item_request in order_request.items:
        # Validate stock exists
        stock = session.get(InventoryStock, item_request.stock_id)
        if not stock:
            raise HTTPException(
                status_code=404,
                detail=f"Inventory stock not found: {item_request.stock_id}"
            )
        
        # Check quantity available
        if stock.quantity_available < item_request.quantity_ordered:
            # Get product and color names for error message
            product = session.get(ProductItem, stock.product_id)
            color = session.get(ProductColor, stock.color_id)
            
            out_of_stock_items.append({
                "stock_id": item_request.stock_id,
                "product_name": product.product_name if product else "Unknown",
                "color_name": color.color_name if color else "Unknown",
                "requested": item_request.quantity_ordered,
                "available": stock.quantity_available,
            })
            continue
        
        # Get product for base cost
        product = session.get(ProductItem, stock.product_id)
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product not found for stock: {item_request.stock_id}"
            )
        
        # Calculate item cost: (base_cost × quantity) + (added_charge × quantity)
        base_cost = product.base_cost
        quantity = item_request.quantity_ordered
        added_charge = Decimal("0.00")
        
        if item_request.custom_id:
            custom_option = session.get(CustomOption, item_request.custom_id)
            if not custom_option:
                raise HTTPException(
                    status_code=404,
                    detail=f"Custom option not found: {item_request.custom_id}"
                )
            added_charge = custom_option.added_charge
        
        calculated_item_cost = (base_cost * quantity) + (added_charge * quantity)
        
        validated_items.append({
            "stock": stock,
            "stock_id": item_request.stock_id,
            "quantity_ordered": item_request.quantity_ordered,
            "custom_id": item_request.custom_id,
            "calculated_item_cost": calculated_item_cost,
        })
    
    # If any items are out of stock, return 400 with details
    if out_of_stock_items:
        raise HTTPException(
            status_code=400,
            detail="Insufficient inventory",
            headers={"X-Out-Of-Stock-Items": str(out_of_stock_items)},
        )
    
    # All items are valid - begin transaction
    try:
        # Calculate total cost
        total_cost = sum(item["calculated_item_cost"] for item in validated_items)
        
        # Create order header
        db_order = OrderHeader(
            order_id=str(uuid4()),
            account_id=user.account_id,
            dc_id=order_request.dc_id,
            contact_email=order_request.contact_email,
            status="IN_FULFILLMENT",
            total_cost=total_cost,
        )
        session.add(db_order)
        
        # Decrement inventory and create order items
        for item in validated_items:
            # Decrement inventory
            stock = item["stock"]
            stock.quantity_available -= item["quantity_ordered"]
            session.add(stock)
            
            # Create order item
            db_order_item = OrderItem(
                detail_id=str(uuid4()),
                order_id=db_order.order_id,
                stock_id=item["stock_id"],
                custom_id=item["custom_id"],
                quantity_ordered=item["quantity_ordered"],
                calculated_item_cost=item["calculated_item_cost"],
            )
            session.add(db_order_item)
        
        # Commit transaction
        session.commit()
        session.refresh(db_order)
        
        # Log to audit_log
        log_order_creation(db_order, user, session)
        
        # Log notifications
        log_order_confirmation(db_order, session)
        log_invoice_notification(db_order, session)
        
        return {
            "message": "Order created",
            "order_id": db_order.order_id,
            "total_cost": str(db_order.total_cost),
        }
    
    except Exception as e:
        # Rollback transaction on any error
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Transaction failed: {str(e)}"
        )


@app.get("/api/orders")
def get_orders(
    session: Session = Depends(get_session),
    user: UserAccount = Depends(get_current_user),
):
    """
    Retrieve orders with role-based filtering.
    
    Validates: Requirements 10.1, 10.2, 10.3, 10.4
    
    - Salesperson: Returns only orders created by that salesperson (account_id = current_user.account_id)
    - Inventory_Manager: Returns all orders
    - Admin: Returns all orders
    - Fulfillment_Team: Returns orders with status IN_FULFILLMENT or SHIPPED
    """
    # Build base query
    query = select(OrderHeader)
    
    # Apply role-based filtering
    if user.role == "Salesperson":
        # Salesperson sees only their own orders
        query = query.where(OrderHeader.account_id == user.account_id)
    elif user.role == "Inventory_Manager" or user.role == "Admin":
        # Inventory_Manager and Admin see all orders (no filter)
        pass
    elif user.role == "Fulfillment_Team":
        # Fulfillment_Team sees only IN_FULFILLMENT or SHIPPED orders
        query = query.where(
            (OrderHeader.status == "IN_FULFILLMENT") | (OrderHeader.status == "SHIPPED")
        )
    
    # Execute query and return results
    orders = session.exec(query).all()
    return orders


@app.get("/api/orders/{order_id}")
def get_order(order_id: str, session: Session = Depends(get_session)):
    order = session.get(OrderHeader, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    items = session.exec(
        select(OrderItem).where(OrderItem.order_id == order_id)
    ).all()

    return {"order": order, "items": items}


@app.patch("/api/orders/{order_id}/status", response_model=dict)
def update_order_status(
    order_id: str,
    payload: OrderStatusUpdate,
    request: Request,
    session: Session = Depends(get_session),
    user: UserAccount = Depends(require_role(["Fulfillment_Team", "Admin"])),
):
    """
    Update order status with validation and logging.
    
    Validates: Requirements 9.2, 9.3, 9.4, 8.3, 8.4, 11.4
    
    - Validates status transition: IN_FULFILLMENT → SHIPPED (valid), any → CANCELLED (valid), others (invalid)
    - If invalid transition, returns 400 Bad Request with error message
    - If valid transition: updates order status, logs to audit_log with old_value and new_value
    - If new status is IN_FULFILLMENT: logs fulfillment notification
    - If new status is SHIPPED: logs shipping notification
    - Returns 200 OK with updated order
    """
    from audit_service import log_status_change
    from notification_service import log_fulfillment_notification, log_shipping_notification
    
    # Get the order
    order = session.get(OrderHeader, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Store old status for validation and logging
    old_status = order.status
    new_status = payload.status
    
    # Validate status transition
    # Valid transitions:
    # - IN_FULFILLMENT → SHIPPED
    # - any status → CANCELLED
    # Invalid: all other transitions
    
    valid_transition = False
    
    # Check if transitioning to CANCELLED (always valid)
    if new_status == "CANCELLED":
        valid_transition = True
    # Check if transitioning from IN_FULFILLMENT to SHIPPED
    elif old_status == "IN_FULFILLMENT" and new_status == "SHIPPED":
        valid_transition = True
    # Check if status is not changing (idempotent update)
    elif old_status == new_status:
        valid_transition = True
    
    # If transition is invalid, return 400 Bad Request
    if not valid_transition:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition: {old_status} cannot transition to {new_status}"
        )
    
    # Update order status
    order.status = new_status
    session.add(order)
    session.commit()
    session.refresh(order)
    
    # Log status change to audit_log
    log_status_change(order, old_status, new_status, user, session)
    
    # Log notifications based on new status
    if new_status == "IN_FULFILLMENT":
        log_fulfillment_notification(order, session)
    elif new_status == "SHIPPED":
        log_shipping_notification(order, session)
    
    return {"message": "Order status updated", "order_id": order.order_id, "status": order.status}


#   Order Items  

@app.post("/api/order-items", response_model=dict)
def create_order_item(item: OrderItemCreate, session: Session = Depends(get_session)):
    order = session.get(OrderHeader, item.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    stock = session.get(InventoryStock, item.stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Inventory stock not found")

    if item.quantity_ordered <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

    if stock.quantity_available < item.quantity_ordered:
        raise HTTPException(status_code=400, detail="Insufficient inventory")

    if item.custom_id:
        custom = session.get(CustomOption, item.custom_id)
        if not custom:
            raise HTTPException(status_code=404, detail="Custom option not found")

    stock.quantity_available -= item.quantity_ordered

    item_cost = item.calculated_item_cost

    db_item = OrderItem(
        detail_id=str(uuid4()),
        order_id=item.order_id,
        stock_id=item.stock_id,
        custom_id=item.custom_id,
        quantity_ordered=item.quantity_ordered,
        calculated_item_cost=item_cost,
    )

    order.total_cost = (order.total_cost or Decimal("0.00")) + item_cost

    session.add(stock)
    session.add(db_item)
    session.add(order)
    session.commit()
    session.refresh(db_item)

    return {"message": "Order item created", "detail_id": db_item.detail_id}


#   Audit Logs  

@app.get("/api/audit-logs", response_model=list[AuditLogRead])
def get_audit_logs(
    event_type: str | None = Query(default=None),
    account_id: str | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
    user: UserAccount = Depends(require_role(["Admin"])),
):
    """
    Retrieve audit logs (Admin only).
    
    Validates: Requirements 2.5, 11.1
    
    - Protected by Admin role only
    - Supports filtering by event_type, account_id, and date range
    - Returns paginated list of audit logs
    """
    # Build query
    query = select(AuditLog)
    
    # Apply filters
    if event_type:
        query = query.where(AuditLog.event_type == event_type)
    
    if account_id:
        query = query.where(AuditLog.account_id == account_id)
    
    if start_date:
        query = query.where(AuditLog.timestamp >= start_date)
    
    if end_date:
        query = query.where(AuditLog.timestamp <= end_date)
    
    # Order by timestamp descending (most recent first)
    query = query.order_by(AuditLog.timestamp.desc())
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    # Execute query
    audit_logs = session.exec(query).all()
    
    return audit_logs


#   Notification Logs  

@app.get("/api/notifications", response_model=list[NotificationLogRead])
def get_notification_logs(
    order_id: str | None = Query(default=None),
    notification_type: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
    user: UserAccount = Depends(require_role(["Admin"])),
):
    """
    Retrieve notification logs (Admin only).
    
    Validates: Requirements 8.5
    
    - Protected by Admin role only
    - Supports filtering by order_id and notification_type
    - Returns paginated list of notification logs
    """
    # Build query
    query = select(NotificationLog)
    
    # Apply filters
    if order_id:
        query = query.where(NotificationLog.order_id == order_id)
    
    if notification_type:
        query = query.where(NotificationLog.notification_type == notification_type)
    
    # Order by timestamp descending (most recent first)
    query = query.order_by(NotificationLog.timestamp.desc())
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    # Execute query
    notification_logs = session.exec(query).all()
    
    return notification_logs


#   Invoice  

@app.get("/api/orders/{order_id}/invoice")
def get_order_invoice(
    order_id: str,
    session: Session = Depends(get_session),
    user: UserAccount = Depends(get_current_user),
):
    """
    Generate and return HTML invoice for an order.
    
    Validates: Requirements 7.1
    
    - Extracts current user from JWT token
    - Applies role-based filtering (same as GET /api/orders):
      - Salesperson: Can only access invoices for their own orders
      - Inventory_Manager: Can access all order invoices
      - Admin: Can access all order invoices
      - Fulfillment_Team: Can only access invoices for IN_FULFILLMENT or SHIPPED orders
    - Calls generate_invoice_html(order_id, session)
    - Returns HTML response with Content-Type: text/html
    """
    from fastapi.responses import HTMLResponse
    from invoice_service import generate_invoice_html
    
    # Get the order
    order = session.get(OrderHeader, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Apply role-based filtering (same as GET /api/orders)
    if user.role == "Salesperson":
        # Salesperson can only access their own orders
        if order.account_id != user.account_id:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
    elif user.role == "Inventory_Manager" or user.role == "Admin":
        # Inventory_Manager and Admin can access all orders (no filter)
        pass
    elif user.role == "Fulfillment_Team":
        # Fulfillment_Team can only access IN_FULFILLMENT or SHIPPED orders
        if order.status not in ["IN_FULFILLMENT", "SHIPPED"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Generate HTML invoice
    try:
        html_invoice = generate_invoice_html(order_id, session)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Return HTML response with Content-Type: text/html
    return HTMLResponse(content=html_invoice, status_code=200)
