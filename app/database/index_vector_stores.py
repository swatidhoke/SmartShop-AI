import logging
import os
from functools import lru_cache

from langchain_postgres import PGEngine, PGVectorStore

from app.config.config import embeddings


logger = logging.getLogger(__name__)


PRODUCTS_VECTOR_TABLE = "products_vector_store"
REVIEWS_VECTOR_TABLE = "reviews_vector_store"
POLICIES_VECTOR_TABLE = "policies_vector_store"


def get_pgvector_connection_string() -> str:
    """
    Convert the normal PostgreSQL URL into the format
    expected by PGEngine using psycopg.
    """

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL is not configured.")

    return database_url.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1,
    )


@lru_cache(maxsize=1)
def get_pg_engine() -> PGEngine:
    """Create one shared PostgreSQL connection pool."""

    logger.info("Creating PGVector PostgreSQL engine")

    return PGEngine.from_connection_string(
        url=get_pgvector_connection_string()
    )


@lru_cache(maxsize=10)
def get_vector_store(table_name: str) -> PGVectorStore:
    """
    Return a PGVectorStore for an existing vector table.
    """
    logger.info(
        "Opening vector store table: %s",
        table_name,
    )

    return PGVectorStore.create_sync(
        engine=get_pg_engine(),
        table_name=table_name,
        embedding_service=embeddings,
    )

def get_products_vector_store() -> PGVectorStore:
    return get_vector_store(PRODUCTS_VECTOR_TABLE)

def get_reviews_vector_store() -> PGVectorStore:
    return get_vector_store(REVIEWS_VECTOR_TABLE)

def get_policies_vector_store() -> PGVectorStore:
    return get_vector_store(POLICIES_VECTOR_TABLE)