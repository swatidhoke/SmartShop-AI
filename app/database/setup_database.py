from pathlib import Path
import csv
import os

import psycopg
from dotenv import load_dotenv

# --------------------------------------------------
# Project setup
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")


# --------------------------------------------------
# Create Tables
# --------------------------------------------------
def create_tables(conn):

    with conn.cursor() as cursor:

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                brand TEXT,
                category TEXT,
                price NUMERIC(10,2),
                description TEXT,
                stock INTEGER,
                rating NUMERIC(2,1)
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                product_id TEXT NOT NULL,
                rating NUMERIC(2,1),
                text TEXT,
                date DATE
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS store_policies (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                policy_type TEXT,
                description TEXT,
                conditions TEXT,
                timeframe INTEGER
            );
        """)

    conn.commit()

    print("✅ Tables created")


# --------------------------------------------------
# Load Products
# --------------------------------------------------
def load_products(conn):

    file_path = DATA_DIR / "products.csv"

    with open(file_path, encoding="utf-8") as file:

        reader = csv.DictReader(file)

        with conn.cursor() as cursor:

            for row in reader:

                cursor.execute(
                    """
                    INSERT INTO products
                    (
                        id,
                        name,
                        brand,
                        category,
                        price,
                        description,
                        stock,
                        rating
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        row["id"],
                        row["name"],
                        row["brand"],
                        row["category"],
                        row["price"],
                        row["description"],
                        row["stock"],
                        row["rating"]
                    )
                )

    conn.commit()

    print("✅ Products loaded")


# --------------------------------------------------
# Load Reviews
# --------------------------------------------------
def load_reviews(conn):

    file_path = DATA_DIR / "reviews.csv"

    with open(file_path, encoding="utf-8") as file:

        reader = csv.DictReader(file)

        with conn.cursor() as cursor:

            for row in reader:

                cursor.execute(
                    """
                    INSERT INTO reviews
                    (
                        product_id,
                        rating,
                        text,
                        date
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        row["product_id"],
                        row["rating"],
                        row["text"],
                        row["date"]
                    )
                )

    conn.commit()

    print("✅ Reviews loaded")


# --------------------------------------------------
# Load Store Policies
# --------------------------------------------------
def load_policies(conn):

    file_path = DATA_DIR / "store_policies.csv"

    with open(file_path, encoding="utf-8") as file:

        reader = csv.DictReader(file)

        with conn.cursor() as cursor:

            for row in reader:

                cursor.execute(
                    """
                    INSERT INTO store_policies
                    (
                        policy_type,
                        description,
                        conditions,
                        timeframe
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        row["policy_type"],
                        row["description"],
                        row["conditions"],
                        row["timeframe"]
                    )
                )

    conn.commit()

    print("✅ Store policies loaded")


# --------------------------------------------------
# Main
# --------------------------------------------------
def main():

    if not DATABASE_URL:
        print("❌ DATABASE_URL is missing from .env")
        return

    print("🔌 Connecting to PostgreSQL...")

    with psycopg.connect(DATABASE_URL) as conn:

        print("✅ Connected to PostgreSQL")

        create_tables(conn)
        load_products(conn)
        load_reviews(conn)
        load_policies(conn)

    print("\n🎉 SmartShop database setup completed!")


if __name__ == "__main__":
    main()
