import sys
from pathlib import Path

from dotenv import load_dotenv
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from database.db import get_connection

load_dotenv()

def get_products():
    print("Fetching products from the database...")
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, name, brand, category,
                       price, description, stock, rating
                FROM products
            """)

            return cursor.fetchall()


def get_products_by_category(category):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, name, brand, category,
                       price, rating
                FROM products
                WHERE category = %s
                ORDER BY rating DESC
            """, (category,))

            return cursor.fetchall()

def get_products_under_price(category, max_price):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, name, brand, category,
                       price, rating
                FROM products
                WHERE category = %s
                AND price <= %s
                ORDER BY rating DESC
            """, (category, max_price))

            return cursor.fetchall()

def get_reviews(product_id):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT product_id, rating, text, date
                FROM reviews
                WHERE product_id = %s
                ORDER BY date DESC
            """, (product_id,))

            return cursor.fetchall()

def get_policies(policy_type):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT policy_type,
                       description,
                       conditions,
                       timeframe
                FROM store_policies
                WHERE policy_type = %s
            """, (policy_type,))

            return cursor.fetchall()