import logging
import os
import uuid
from decimal import Decimal

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_postgres import PGEngine, PGVectorStore

from app.config.config import embeddings
from app.database.db import get_connection


load_dotenv()
# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Vector store configuration
# ---------------------------------------------------------

EMBEDDING_SIZE = 1536

PRODUCTS_VECTOR_TABLE = "products_vector_store"
REVIEWS_VECTOR_TABLE = "reviews_vector_store"
POLICIES_VECTOR_TABLE = "policies_vector_store"


# ---------------------------------------------------------
# PostgreSQL / PGVector helpers
# ---------------------------------------------------------

def get_pgvector_connection_string() -> str:
    """
    Return the PostgreSQL connection string required by PGEngine.
    """

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError(
            "DATABASE_URL is not configured."
        )

    return database_url.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1,
    )


def create_pg_engine() -> PGEngine:
    """
    Create one shared PGVector database engine.
    """

    logger.info("Creating PostgreSQL PGVector engine")

    return PGEngine.from_connection_string(
        url=get_pgvector_connection_string()
    )


def create_vector_table(
    pg_engine: PGEngine,
    table_name: str,
) -> None:
    """
    Create a vector table.

    During development we rebuild the vector table so
    indexing can be safely rerun from scratch.
    """

    logger.info(
        "Creating vector table: %s",
        table_name,
    )

    pg_engine.init_vectorstore_table(
        table_name=table_name,
        vector_size=EMBEDDING_SIZE,
        overwrite_existing=True,
    )


def get_vector_store(
    pg_engine: PGEngine,
    table_name: str,
) -> PGVectorStore:
    """
    Connect LangChain to an existing PostgreSQL vector table.
    """

    return PGVectorStore.create_sync(
        engine=pg_engine,
        table_name=table_name,
        embedding_service=embeddings,
    )


# ---------------------------------------------------------
# Small data helpers
# ---------------------------------------------------------

def to_float(value):
    """
    Convert PostgreSQL Decimal values into normal Python floats
    so they can safely be stored as metadata.
    """

    if value is None:
        return None

    if isinstance(value, Decimal):
        return float(value)

    return float(value)


def create_document_id(
    source: str,
    source_id,
) -> str:
    """
    Create a repeatable UUID for each source record.
    """

    return str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            f"smartshop-{source}-{source_id}",
        )
    )


# ---------------------------------------------------------
# Product documents
# ---------------------------------------------------------

def load_products() -> list[Document]:
    """
    Load products from PostgreSQL and convert them
    into documents for semantic product search.
    """

    logger.info("Loading products from PostgreSQL")

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    brand,
                    category,
                    price,
                    description,
                    stock,
                    rating
                FROM products
                """
            )

            products = cursor.fetchall()

    documents = []

    for product in products:

        product_text = f"""
Product: {product["name"]}
Brand: {product["brand"]}
Category: {product["category"]}
Description: {product["description"]}
""".strip()

        document = Document(
            id=create_document_id(
                "product",
                product["id"],
            ),
            page_content=product_text,
            metadata={
                "product_id": str(product["id"]),
                "name": product["name"],
                "brand": product["brand"],
                "category": product["category"],
                "price": to_float(product["price"]),
                "rating": to_float(product["rating"]),
                "stock": product["stock"],
            },
        )

        documents.append(document)

    logger.info(
        "Loaded %s products",
        len(documents),
    )

    return documents


# ---------------------------------------------------------
# Review documents
# ---------------------------------------------------------

def load_reviews() -> list[Document]:
    """
    Load reviews and convert them into documents
    for semantic review search.
    """

    logger.info("Loading reviews from PostgreSQL")

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    r.id,
                    r.product_id,
                    r.rating,
                    r.text,
                    r.date,
                    p.name AS product_name
                FROM reviews r
                LEFT JOIN products p
                    ON p.id = r.product_id
                """
            )

            reviews = cursor.fetchall()

    documents = []

    for review in reviews:

        review_text = f"""
Product: {review["product_name"]}
Customer review: {review["text"]}
Rating: {review["rating"]}
""".strip()

        document = Document(
            id=create_document_id(
                "review",
                review["id"],
            ),
            page_content=review_text,
            metadata={
                "review_id": str(review["id"]),
                "product_id": str(review["product_id"]),
                "product_name": review["product_name"],
                "rating": to_float(review["rating"]),
                "date": (
                    str(review["date"])
                    if review["date"]
                    else None
                ),
            },
        )

        documents.append(document)

    logger.info(
        "Loaded %s reviews",
        len(documents),
    )

    return documents


# ---------------------------------------------------------
# Policy documents
# ---------------------------------------------------------

def load_policies() -> list[Document]:
    """
    Load store policies and convert them into documents
    for semantic policy search.
    """

    logger.info("Loading store policies from PostgreSQL")

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    policy_type,
                    description,
                    conditions,
                    timeframe
                FROM store_policies
                """
            )

            policies = cursor.fetchall()

    documents = []

    for policy in policies:

        policy_text = f"""
Policy type: {policy["policy_type"]}
Description: {policy["description"]}
Conditions: {policy["conditions"]}
Timeframe: {policy["timeframe"]}
""".strip()

        document = Document(
            id=create_document_id(
                "policy",
                policy["id"],
            ),
            page_content=policy_text,
            metadata={
                "policy_id": str(policy["id"]),
                "policy_type": policy["policy_type"],
            },
        )

        documents.append(document)

    logger.info(
        "Loaded %s policies",
        len(documents),
    )

    return documents


# ---------------------------------------------------------
# Common indexing logic
# ---------------------------------------------------------

def index_documents(
    vector_store: PGVectorStore,
    documents: list[Document],
    name: str,
) -> None:
    """
    Create embeddings and store documents in PGVector.
    """

    if not documents:
        logger.warning(
            "No %s documents found. Skipping.",
            name,
        )
        return

    logger.info(
        "Creating embeddings for %s %s documents",
        len(documents),
        name,
    )

    vector_store.add_documents(
        documents=documents,
    )

    logger.info(
        "%s indexing completed successfully",
        name.capitalize(),
    )


# ---------------------------------------------------------
# Main indexing workflow
# ---------------------------------------------------------

def create_all_vector_stores() -> None:
    """
    Create and populate all SmartShop vector stores.
    """

    logger.info(
        "Starting SmartShop vector indexing"
    )

    pg_engine = create_pg_engine()

    try:
        # -------------------------------------------------
        # Products
        # -------------------------------------------------

        create_vector_table(
            pg_engine,
            PRODUCTS_VECTOR_TABLE,
        )

        products_vector_store = get_vector_store(
            pg_engine,
            PRODUCTS_VECTOR_TABLE,
        )

        index_documents(
            products_vector_store,
            load_products(),
            "products",
        )

        # -------------------------------------------------
        # Reviews
        # -------------------------------------------------

        create_vector_table(
            pg_engine,
            REVIEWS_VECTOR_TABLE,
        )

        reviews_vector_store = get_vector_store(
            pg_engine,
            REVIEWS_VECTOR_TABLE,
        )

        index_documents(
            reviews_vector_store,
            load_reviews(),
            "reviews",
        )

        # -------------------------------------------------
        # Policies
        # -------------------------------------------------

        create_vector_table(
            pg_engine,
            POLICIES_VECTOR_TABLE,
        )

        policies_vector_store = get_vector_store(
            pg_engine,
            POLICIES_VECTOR_TABLE,
        )

        index_documents(
            policies_vector_store,
            load_policies(),
            "policies",
        )

        logger.info(
            "All SmartShop vector stores created successfully"
        )

    finally:
        pg_engine.close()

if __name__ == "__main__":
    create_all_vector_stores()