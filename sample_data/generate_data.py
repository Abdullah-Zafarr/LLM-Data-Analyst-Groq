import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Parameters
n_rows = 200
regions = ['North', 'South', 'East', 'West', 'Central']
categories = ['Electronics', 'Accessories', 'Home', 'Office']
products = {
    'Electronics': ['Widget A', 'Widget B', 'Gadget Y', 'Gadget X', 'Smartphone Z', 'Laptop Pro'],
    'Accessories': ['Cable Pack', 'Phone Case', 'Wireless Charger', 'Bluetooth Earbuds'],
    'Home': ['Smart Bulb', 'Smart Plug', 'Desk Lamp', 'Air Purifier'],
    'Office': ['Desk Mat', 'Ergo Mouse', 'Mechanical Keyboard', 'Monitor Stand']
}
salespeople = ['Alice', 'Bob', 'Charlie', 'Diana', 'Evan', 'Fiona', 'George', 'Hannah']
payment_methods = ['Credit Card', 'PayPal', 'Wire Transfer', 'Cash']

start_date = datetime(2023, 1, 1)

data = []
for i in range(n_rows):
    order_id = f"ORD-{1000 + i}"
    # Generate dates heavily skewed towards 2023 and early 2024
    days_to_add = np.random.randint(0, 500)
    date = (start_date + timedelta(days=int(days_to_add))).strftime('%Y-%m-%d')
    
    region = random.choice(regions)
    category = random.choice(categories)
    product = random.choice(products[category])
    salesperson = random.choice(salespeople)
    
    # Introduce anomalies
    if random.random() < 0.05:
        # Returns / Refunds -> negative units & revenue
        units = -np.random.randint(1, 10)
        revenue = units * np.random.uniform(15, 200)
    else:
        # Normal sales
        units = np.random.randint(1, 100)
        revenue = units * np.random.uniform(10, 250)
        # 10% chance of extreme outlier (whale customer)
        if random.random() < 0.1:
            revenue *= np.random.uniform(5, 10)
            
    # Add a discount
    discount = 0.0
    if random.random() < 0.3:
        discount = round(np.random.uniform(0.05, 0.3), 2)
        
    payment = random.choice(payment_methods)
    
    # Introduce some missing values to test data cleaning
    if random.random() < 0.04:
        salesperson = np.nan
    if random.random() < 0.03:
        region = np.nan
        
    data.append([
        order_id, date, region, product, category, salesperson, 
        units, round(revenue, 2), discount, payment
    ])

df = pd.DataFrame(data, columns=[
    'OrderID', 'Date', 'Region', 'Product', 'Category', 'Salesperson',
    'Units', 'Revenue', 'Discount', 'Payment_Method'
])

# Sort by date
df = df.sort_values('Date').reset_index(drop=True)

# Add duplicate rows to test duplicate handling
df = pd.concat([df, df.iloc[[10, 25, 42]]], ignore_index=True)

# Write to CSV
df.to_csv('c:/Users/Hp/Downloads/Tool-Calling project/sample_data/sales_data.csv', index=False)
print("Successfully generated enhanced sales_data.csv with 203 rows.")
