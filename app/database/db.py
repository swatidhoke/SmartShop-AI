"""
Database connection helper for SmartShop AI.

This module creates PostgreSQL database connections.
Other modules import get_connection() from here.
"""

import os

import psycopg
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    """
    Create and return a PostgreSQL database connection.

    DATABASE_URL should be stored in the .env file.

    Example:
        DATABASE_URL=postgresql://postgres:password@host:5432/smartshop
    """

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError(
            "DATABASE_URL is not configured. "
            "Add it to your .env file."
        )

    return psycopg.connect(database_url)