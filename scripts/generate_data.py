"""
=============================================================================
Supermarket Sales Dataset Generator
=============================================================================
This script generates a realistic 500-transaction dataset for the
"Supermarket Sales Analysis" project.

Attributes included:
- Invoice ID: Unique identifier for each transaction (e.g., INV-1001)
- Branch: Supermarket branch location (Branch A, Branch B, Branch C)
- City: City where the branch is located (Yangon, Naypyitaw, Mandalay)
- Customer Type: 'Member' (loyalty card holders) vs 'Normal' (regular shoppers)
- Gender: 'Female' or 'Male'
- Category: Product category / department
- Product: Specific item sold
- Unit Price: Price per single unit in USD ($)
- Quantity: Number of units purchased (1 to 10)
- Payment Method: 'Cash', 'Credit card', or 'E-wallet'
- Rating: Customer satisfaction score (1.0 to 10.0)
- Date: Transaction date

To make data cleaning realistic and educational, a few intentional edge cases
(e.g., occasional missing values, inconsistent casing) are included for our
cleaning pipeline to detect and handle.
"""

import os
import random
import pandas as pd
from datetime import datetime, timedelta

def generate_supermarket_dataset(num_records: int = 500, output_path: str = "data/supermarket_sales.csv"):
    # Ensure reproducible results
    random.seed(42)

    # Define realistic product catalogs grouped by category with realistic price ranges
    catalog = {
        "Electronic accessories": [
            ("Wireless Earbuds", 35.0, 65.0),
            ("USB-C Fast Charger", 15.0, 28.0),
            ("Bluetooth Speaker", 40.0, 85.0),
            ("Power Bank 20000mAh", 25.0, 50.0),
            ("Gaming Mouse", 30.0, 75.0)
        ],
        "Fashion accessories": [
            ("Polarized Sunglasses", 20.0, 55.0),
            ("Leather Belt", 18.0, 42.0),
            ("Casual Backpack", 35.0, 80.0),
            ("Silk Scarf", 15.0, 38.0),
            ("Wristwatch", 45.0, 99.0)
        ],
        "Food and beverages": [
            ("Organic Green Tea", 8.0, 22.0),
            ("Artisan Dark Chocolate", 5.0, 16.0),
            ("Extra Virgin Olive Oil", 12.0, 32.0),
            ("Gourmet Ground Coffee", 10.0, 26.0),
            ("Almond Milk 1L Pack", 6.0, 18.0)
        ],
        "Health and beauty": [
            ("Hydrating Face Serum", 22.0, 60.0),
            ("Herbal Shampoo", 10.0, 25.0),
            ("Mineral Sunscreen SPF 50", 16.0, 35.0),
            ("Aromatherapy Essential Oil", 14.0, 30.0),
            ("Bamboo Toothbrush Set", 8.0, 19.0)
        ],
        "Home and lifestyle": [
            ("Scented Soy Candle", 12.0, 28.0),
            ("Ceramic Coffee Mug Set", 18.0, 36.0),
            ("Microfiber Bed Sheet", 28.0, 65.0),
            ("Indoor Plant Pot", 14.0, 34.0),
            ("Stainless Steel Water Bottle", 15.0, 32.0)
        ],
        "Sports and travel": [
            ("Non-Slip Yoga Mat", 20.0, 48.0),
            ("Resistance Bands Kit", 12.0, 30.0),
            ("Travel Neck Pillow", 14.0, 28.0),
            ("Quick-Dry Gym Towel", 9.0, 22.0),
            ("Collapsible Duffle Bag", 25.0, 58.0)
        ]
    }

    # Branch mapping to cities
    branch_city_map = {
        "Branch A": "Yangon",
        "Branch B": "Mandalay",
        "Branch C": "Naypyitaw"
    }

    customer_types = ["Member", "Normal"]
    genders = ["Female", "Male"]
    payment_methods = ["Cash", "Credit card", "E-wallet"]
    start_date = datetime(2026, 1, 1)

    categories = list(catalog.keys())
    branches = list(branch_city_map.keys())

    records = []

    for i in range(1, num_records + 1):
        invoice_id = f"INV-{1000 + i}"
        branch = random.choice(branches)
        city = branch_city_map[branch]
        customer_type = random.choices(customer_types, weights=[0.55, 0.45])[0]
        gender = random.choice(genders)

        # Select category and corresponding product
        category = random.choice(categories)
        product_info = random.choice(catalog[category])
        product_name = product_info[0]
        min_price, max_price = product_info[1], product_info[2]

        # Unit price with 2 decimals
        unit_price = round(random.uniform(min_price, max_price), 2)
        # Quantity between 1 and 10 items
        quantity = random.randint(1, 10)

        # Payment method
        payment = random.choices(payment_methods, weights=[0.35, 0.35, 0.30])[0]

        # Rating score from 1.0 to 10.0 (skewed towards realistic customer feedback: 5.5 - 9.5)
        rating = round(random.triangular(4.0, 10.0, 7.8), 1)

        # Transaction date spread over 90 days
        tx_date = (start_date + timedelta(days=random.randint(0, 89))).strftime("%Y-%m-%d")

        records.append({
            "Invoice ID": invoice_id,
            "Branch": branch,
            "City": city,
            "Customer Type": customer_type,
            "Gender": gender,
            "Category": category,
            "Product": product_name,
            "Unit Price": unit_price,
            "Quantity": quantity,
            "Payment Method": payment,
            "Rating": rating,
            "Date": tx_date
        })

    # Convert to DataFrame
    df = pd.DataFrame(records)

    # Introduce a few realistic data anomalies to demonstrate data cleaning capabilities:
    # 1. A couple of missing values in 'Rating' or 'Customer Type'
    df.loc[12, "Rating"] = None
    df.loc[45, "Customer Type"] = None
    # 2. Inconsistent casing in a branch name
    df.loc[88, "Branch"] = "branch a"

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Successfully generated {len(df)} transactions in '{output_path}'")
    return df

if __name__ == "__main__":
    generate_supermarket_dataset()
