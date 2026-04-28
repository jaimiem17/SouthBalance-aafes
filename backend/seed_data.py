"""
Data Seeding Script for AAFES Order Management MVP

This script populates the database with test data for the MVP demo.
The script is idempotent - it can be run multiple times without errors.

Usage:
    python seed_data.py

Requirements: All (data setup for testing)
"""

from __future__ import annotations

import base64
import hashlib
import secrets
from decimal import Decimal
from uuid import uuid4

from sqlmodel import Session, select

from database import engine, init_db
from models import (
    UserAccount,
    AAFESDistributionCenter,
    ProductItem,
    ProductColor,
    CustomOption,
    InventoryStock,
)


PASSWORD_HASH_ITERATIONS = 600_000


def hash_password(password: str) -> str:
    """
    Hash a password using PBKDF2-SHA256.
    
    Args:
        password: Plain text password
    
    Returns:
        Password hash in format: pbkdf2_sha256$iterations$salt$digest
    """
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


def seed_users(session: Session) -> dict[str, str]:
    """
    Create 4 test users with different roles.
    
    Returns:
        Dictionary mapping username to account_id
    """
    users_data = [
        {
            "username": "alice_sales",
            "password": "password123",
            "role": "Salesperson",
        },
        {
            "username": "bob_inventory",
            "password": "password123",
            "role": "Inventory_Manager",
        },
        {
            "username": "charlie_admin",
            "password": "password123",
            "role": "Admin",
        },
        {
            "username": "diana_fulfillment",
            "password": "password123",
            "role": "Fulfillment_Team",
        },
    ]
    
    user_ids = {}
    
    for user_data in users_data:
        # Check if user already exists
        existing_user = session.exec(
            select(UserAccount).where(UserAccount.username == user_data["username"])
        ).first()
        
        if existing_user:
            print(f"✓ User '{user_data['username']}' already exists")
            user_ids[user_data["username"]] = existing_user.account_id
            continue
        
        # Create new user
        user = UserAccount(
            account_id=str(uuid4()),
            username=user_data["username"],
            password_hash=hash_password(user_data["password"]),
            role=user_data["role"],
            is_active=True,
        )
        session.add(user)
        user_ids[user_data["username"]] = user.account_id
        print(f"✓ Created user '{user_data['username']}' with role '{user_data['role']}'")
    
    session.commit()
    return user_ids


def seed_distribution_centers(session: Session) -> dict[str, str]:
    """
    Create 3 distribution centers.
    
    Returns:
        Dictionary mapping facility name to dc_id
    """
    dcs_data = [
        {
            "facility_name": "AAFES East",
            "address1": "1234 Military Way",
            "address2": None,
            "city": "Norfolk",
            "state": "VA",
            "postal_code": "23511",
            "region": "East",
        },
        {
            "facility_name": "AAFES West",
            "address1": "5678 Base Blvd",
            "address2": None,
            "city": "San Diego",
            "state": "CA",
            "postal_code": "92101",
            "region": "West",
        },
        {
            "facility_name": "AAFES Central",
            "address1": "9012 Fort Street",
            "address2": None,
            "city": "Fort Worth",
            "state": "TX",
            "postal_code": "76102",
            "region": "Central",
        },
    ]
    
    dc_ids = {}
    
    for dc_data in dcs_data:
        # Check if DC already exists
        existing_dc = session.exec(
            select(AAFESDistributionCenter).where(
                AAFESDistributionCenter.facility_name == dc_data["facility_name"]
            )
        ).first()
        
        if existing_dc:
            print(f"✓ Distribution center '{dc_data['facility_name']}' already exists")
            dc_ids[dc_data["facility_name"]] = existing_dc.dc_id
            continue
        
        # Create new DC
        dc = AAFESDistributionCenter(
            dc_id=str(uuid4()),
            facility_name=dc_data["facility_name"],
            address1=dc_data["address1"],
            address2=dc_data["address2"],
            city=dc_data["city"],
            state=dc_data["state"],
            postal_code=dc_data["postal_code"],
            region=dc_data["region"],
        )
        session.add(dc)
        dc_ids[dc_data["facility_name"]] = dc.dc_id
        print(f"✓ Created distribution center '{dc_data['facility_name']}' in {dc_data['city']}, {dc_data['state']}")
    
    session.commit()
    return dc_ids


def seed_products(session: Session) -> dict[str, str]:
    """
    Create 2 products.
    
    Returns:
        Dictionary mapping product name to product_id
    """
    products_data = [
        {
            "product_name": "Yoga Mat",
            "base_cost": Decimal("25.00"),
            "is_active": True,
        },
        {
            "product_name": "Water Bottle",
            "base_cost": Decimal("15.00"),
            "is_active": True,
        },
    ]
    
    product_ids = {}
    
    for product_data in products_data:
        # Check if product already exists
        existing_product = session.exec(
            select(ProductItem).where(
                ProductItem.product_name == product_data["product_name"]
            )
        ).first()
        
        if existing_product:
            print(f"✓ Product '{product_data['product_name']}' already exists")
            product_ids[product_data["product_name"]] = existing_product.product_id
            continue
        
        # Create new product
        product = ProductItem(
            product_id=str(uuid4()),
            product_name=product_data["product_name"],
            base_cost=product_data["base_cost"],
            is_active=product_data["is_active"],
        )
        session.add(product)
        product_ids[product_data["product_name"]] = product.product_id
        print(f"✓ Created product '{product_data['product_name']}' with base cost ${product_data['base_cost']}")
    
    session.commit()
    return product_ids


def seed_colors(session: Session) -> dict[str, str]:
    """
    Create 2 colors.
    
    Returns:
        Dictionary mapping color name to color_id
    """
    colors_data = [
        {"color_name": "Blue"},
        {"color_name": "Green"},
    ]
    
    color_ids = {}
    
    for color_data in colors_data:
        # Check if color already exists
        existing_color = session.exec(
            select(ProductColor).where(
                ProductColor.color_name == color_data["color_name"]
            )
        ).first()
        
        if existing_color:
            print(f"✓ Color '{color_data['color_name']}' already exists")
            color_ids[color_data["color_name"]] = existing_color.color_id
            continue
        
        # Create new color
        color = ProductColor(
            color_id=str(uuid4()),
            color_name=color_data["color_name"],
        )
        session.add(color)
        color_ids[color_data["color_name"]] = color.color_id
        print(f"✓ Created color '{color_data['color_name']}'")
    
    session.commit()
    return color_ids


def seed_custom_options(session: Session) -> dict[str, str]:
    """
    Create 5 custom options (1 patriotic, 4 branch-specific).
    
    Returns:
        Dictionary mapping custom option name to custom_id
    """
    custom_options_data = [
        {
            "name": "patriotic",
            "custom_type": "patriotic",
            "branch_name": None,
            "added_charge": Decimal("2.00"),
        },
        {
            "name": "Army",
            "custom_type": "branch",
            "branch_name": "Army",
            "added_charge": Decimal("5.00"),
        },
        {
            "name": "Navy",
            "custom_type": "branch",
            "branch_name": "Navy",
            "added_charge": Decimal("5.00"),
        },
        {
            "name": "Air Force",
            "custom_type": "branch",
            "branch_name": "Air Force",
            "added_charge": Decimal("5.00"),
        },
        {
            "name": "Marines",
            "custom_type": "branch",
            "branch_name": "Marines",
            "added_charge": Decimal("5.00"),
        },
    ]
    
    custom_ids = {}
    
    for custom_data in custom_options_data:
        # Check if custom option already exists
        # For patriotic: check custom_type = "patriotic"
        # For branch: check custom_type = "branch" AND branch_name matches
        if custom_data["custom_type"] == "patriotic":
            existing_custom = session.exec(
                select(CustomOption).where(
                    CustomOption.custom_type == "patriotic"
                )
            ).first()
        else:
            existing_custom = session.exec(
                select(CustomOption).where(
                    (CustomOption.custom_type == "branch") &
                    (CustomOption.branch_name == custom_data["branch_name"])
                )
            ).first()
        
        if existing_custom:
            print(f"✓ Custom option '{custom_data['name']}' already exists")
            custom_ids[custom_data["name"]] = existing_custom.custom_id
            continue
        
        # Create new custom option
        custom = CustomOption(
            custom_id=str(uuid4()),
            custom_type=custom_data["custom_type"],
            branch_name=custom_data["branch_name"],
            added_charge=custom_data["added_charge"],
        )
        session.add(custom)
        custom_ids[custom_data["name"]] = custom.custom_id
        print(f"✓ Created custom option '{custom_data['name']}' with charge ${custom_data['added_charge']}")
    
    session.commit()
    return custom_ids


def seed_inventory(
    session: Session,
    product_ids: dict[str, str],
    color_ids: dict[str, str],
) -> None:
    """
    Create 4 inventory records (2 products × 2 colors).
    """
    inventory_data = [
        {
            "product_name": "Yoga Mat",
            "color_name": "Blue",
            "quantity_available": 100,
        },
        {
            "product_name": "Yoga Mat",
            "color_name": "Green",
            "quantity_available": 100,
        },
        {
            "product_name": "Water Bottle",
            "color_name": "Blue",
            "quantity_available": 200,
        },
        {
            "product_name": "Water Bottle",
            "color_name": "Green",
            "quantity_available": 200,
        },
    ]
    
    for inv_data in inventory_data:
        product_id = product_ids[inv_data["product_name"]]
        color_id = color_ids[inv_data["color_name"]]
        
        # Check if inventory record already exists
        existing_inventory = session.exec(
            select(InventoryStock).where(
                (InventoryStock.product_id == product_id) &
                (InventoryStock.color_id == color_id)
            )
        ).first()
        
        if existing_inventory:
            print(f"✓ Inventory for '{inv_data['product_name']} {inv_data['color_name']}' already exists (quantity: {existing_inventory.quantity_available})")
            continue
        
        # Create new inventory record
        inventory = InventoryStock(
            stock_id=str(uuid4()),
            product_id=product_id,
            color_id=color_id,
            quantity_available=inv_data["quantity_available"],
        )
        session.add(inventory)
        print(f"✓ Created inventory for '{inv_data['product_name']} {inv_data['color_name']}' with quantity {inv_data['quantity_available']}")
    
    session.commit()


def main():
    """
    Main function to seed all test data.
    """
    print("=" * 60)
    print("AAFES Order Management MVP - Data Seeding Script")
    print("=" * 60)
    print()
    
    # Initialize database (create tables if they don't exist)
    print("Initializing database...")
    init_db()
    print("✓ Database initialized")
    print()
    
    # Create database session
    with Session(engine) as session:
        # Seed users
        print("Seeding users...")
        user_ids = seed_users(session)
        print()
        
        # Seed distribution centers
        print("Seeding distribution centers...")
        dc_ids = seed_distribution_centers(session)
        print()
        
        # Seed products
        print("Seeding products...")
        product_ids = seed_products(session)
        print()
        
        # Seed colors
        print("Seeding colors...")
        color_ids = seed_colors(session)
        print()
        
        # Seed custom options
        print("Seeding custom options...")
        custom_ids = seed_custom_options(session)
        print()
        
        # Seed inventory
        print("Seeding inventory...")
        seed_inventory(session, product_ids, color_ids)
        print()
    
    print("=" * 60)
    print("Data seeding completed successfully!")
    print("=" * 60)
    print()
    print("Test Users:")
    print("  - alice_sales (Salesperson) - password: password123")
    print("  - bob_inventory (Inventory_Manager) - password: password123")
    print("  - charlie_admin (Admin) - password: password123")
    print("  - diana_fulfillment (Fulfillment_Team) - password: password123")
    print()
    print("Distribution Centers:")
    print("  - AAFES East (Norfolk, VA)")
    print("  - AAFES West (San Diego, CA)")
    print("  - AAFES Central (Fort Worth, TX)")
    print()
    print("Products:")
    print("  - Yoga Mat ($25.00)")
    print("  - Water Bottle ($15.00)")
    print()
    print("Colors:")
    print("  - Blue")
    print("  - Green")
    print()
    print("Custom Options:")
    print("  - patriotic ($2.00)")
    print("  - Army ($5.00)")
    print("  - Navy ($5.00)")
    print("  - Air Force ($5.00)")
    print("  - Marines ($5.00)")
    print()
    print("Inventory:")
    print("  - Yoga Mat Blue: 100")
    print("  - Yoga Mat Green: 100")
    print("  - Water Bottle Blue: 200")
    print("  - Water Bottle Green: 200")
    print()


if __name__ == "__main__":
    main()
