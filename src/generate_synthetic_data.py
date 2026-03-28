import numpy as np
import pandas as pd
import random
from faker import Faker
from datetime import datetime
import os

# -----------------------------------------------------------
#  CONFIGURATION
# -----------------------------------------------------------

NUM_CUSTOMERS = 3000
NUM_MERCHANTS = 500
NUM_TRANSACTIONS = 150000
FRAUD_RATE = 0.015  # ~1.5%

COUNTRIES = {
    "Dominican Republic": {"currency": "DOP", "fx_to_usd": 0.016},
    "United States": {"currency": "USD", "fx_to_usd": 1.00},
    "Mexico": {"currency": "MXN", "fx_to_usd": 0.058},
    "Colombia": {"currency": "COP", "fx_to_usd": 0.00026},
    "Brazil": {"currency": "BRL", "fx_to_usd": 0.20},
}

LATAM_NAMES = ["Carlos", "María", "Luis", "Ana", "José", "Juan", "Camila", "Pedro", "Julia", "Sofía"]
AMERICAN_NAMES = ["Emily", "Jacob", "Olivia", "Michael", "Ava", "Ethan", "Sophia", "Logan"]

MERCHANT_CATEGORIES = [
    "Supermarket", "Electronics", "Travel", "Restaurant", "Clothing",
    "Online Marketplace", "Gas Station", "Pharmacy", "Home Goods"
]

CHANNELS = ["POS", "Online", "ATM"]

FRAUD_TYPES = [
    "stolen_card", "card_not_present", "high_value", "location_anomaly",
    "merchant_anomaly", "velocity"
]

fake = Faker()

# Create folders
os.makedirs("data", exist_ok=True)


# -----------------------------------------------------------
#  GENERATE CUSTOMERS
# -----------------------------------------------------------

def generate_customers():
    records = []

    for i in range(1, NUM_CUSTOMERS + 1):
        country = random.choice(list(COUNTRIES.keys()))

        first_name = random.choice(LATAM_NAMES + AMERICAN_NAMES)
        last_name = fake.last_name()

        credit_limit = random.choice([1000, 2000, 3000, 5000, 7000, 10000])

        records.append({
            "customer_id": i,
            "name": f"{first_name} {last_name}",
            "age": random.randint(18, 75),
            "country": country,
            "account_open_date": fake.date_between(start_date="-8y", end_date="today"),
            "credit_limit": credit_limit,
            "card_type": random.choice(["Classic", "Gold", "Platinum"])
        })

    return pd.DataFrame(records)


# -----------------------------------------------------------
#  GENERATE MERCHANTS
# -----------------------------------------------------------

def generate_merchants():
    records = []

    for i in range(1, NUM_MERCHANTS + 1):
        country = random.choice(list(COUNTRIES.keys()))

        merchant_name = (
            random.choice(["Supermercado", "La Tienda", "Tech Planet", "ElectroMax", "Brasilia Moda"])
            + " "
            + random.choice(["Caribe", "USA", "Latina", "Premium", "Express"])
        )

        records.append({
            "merchant_id": i,
            "merchant_name": merchant_name,
            "merchant_category": random.choice(MERCHANT_CATEGORIES),
            "country": country
        })

    return pd.DataFrame(records)


# -----------------------------------------------------------
#  GENERATE TRANSACTIONS
# -----------------------------------------------------------

def generate_transactions(customers, merchants):
    records = []

    for i in range(1, NUM_TRANSACTIONS + 1):

        customer = customers.sample(1).iloc[0]
        merchant = merchants.sample(1).iloc[0]

        # Transaction date
        tx_date = fake.date_time_between(start_date="-18M", end_date="now")

        # Amount in local currency
        amount_original = round(np.random.exponential(scale=40) + 5, 2)

        # Multi-currency fields
        info = COUNTRIES[customer["country"]]
        currency = info["currency"]
        fx_rate = info["fx_to_usd"]
        amount_usd = round(amount_original * fx_rate, 2)

        # Fraud logic
        is_fraud = 1 if random.random() < FRAUD_RATE else 0
        fraud_type = random.choice(FRAUD_TYPES) if is_fraud else None
        fraud_score = round(random.uniform(0.5, 1.0), 3) if is_fraud else round(random.uniform(0, 0.15), 3)

        records.append({
            "transaction_id": i,
            "customer_id": customer["customer_id"],
            "merchant_id": merchant["merchant_id"],
            "transaction_date": tx_date,
            "transaction_currency": currency,
            "fx_rate_to_usd": fx_rate,
            "amount_original_currency": amount_original,
            "amount_usd": amount_usd,
            "channel": random.choice(CHANNELS),
            "is_international": int(customer["country"] != merchant["country"]),
            "fraud_flag": is_fraud,
            "fraud_type": fraud_type,
            "fraud_probability": fraud_score
        })

    return pd.DataFrame(records)


# -----------------------------------------------------------
#  EXECUTION
# -----------------------------------------------------------

customers_df = generate_customers()
merchants_df = generate_merchants()
transactions_df = generate_transactions(customers_df, merchants_df)

customers_df.to_csv("data/customers.csv", index=False)
merchants_df.to_csv("data/merchants.csv", index=False)
transactions_df.to_csv("data/transactions.csv", index=False)

print("✓ Synthetic credit card dataset successfully generated!")
print("Files created in /data folder:")
print(" - customers.csv")
print(" - merchants.csv")
print(" - transactions.csv")