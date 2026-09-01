import asyncio
import logging

from langchain_core.documents import Document
from psycopg.rows import dict_row
from app.database.db import get_connection
from scripts.setup_index_vector_stores import (
    PRODUCTS_VECTOR_TABLE,
    REVIEWS_VECTOR_TABLE,
    POLICIES_VECTOR_TABLE,
    create_document_id,
    create_pg_engine,
    get_vector_store,
    to_float,
)

# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# One-time preparation
# ---------------------------------------------------------

def ensure_indexed_column(conn, table_name: str) -> None:
    """
    Add an 'indexed' column if it does not already exist.

    Existing rows are marked True because your full indexing script
    has already indexed them.

    Future rows automatically get indexed=False, so this script can
    find only the new incoming data.
    """

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = %s
                  AND column_name = 'indexed'
            )
            """,
            (table_name,),
        )

        column_exists = cursor.fetchone()[0]

        if column_exists:
            return

        logger.info("Adding indexed column to %s", table_name)

        # Existing rows become TRUE.
        cursor.execute(
            f"""
            ALTER TABLE {table_name}
            ADD COLUMN indexed BOOLEAN NOT NULL DEFAULT TRUE
            """
        )

        # New rows inserted later will become FALSE.
        cursor.execute(
            f"""
            ALTER TABLE {table_name}
            ALTER COLUMN indexed SET DEFAULT FALSE
            """
        )

    conn.commit()


def prepare_tables() -> None:
    """
    Prepare all source tables for incremental indexing.
    """

    with get_connection() as conn:
        ensure_indexed_column(conn, "products")
        ensure_indexed_column(conn, "reviews")
        ensure_indexed_column(conn, "store_policies")


# ---------------------------------------------------------
# Load new products
# ---------------------------------------------------------

def load_new_products():
    """
    Load only products that have not been indexed yet.
    """

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
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
                WHERE indexed = FALSE
                """
            )

            rows = cursor.fetchall()

    documents = []
    vector_ids = []
    database_ids = []

    for product in rows:
        product_text = f"""
Product: {product["name"]}
Brand: {product["brand"]}
Category: {product["category"]}
Description: {product["description"]}
""".strip()

        vector_id = create_document_id(
            "product",
            product["id"],
        )

        document = Document(
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
        vector_ids.append(vector_id)
        database_ids.append(product["id"])

    return documents, vector_ids, database_ids


# ---------------------------------------------------------
# Load new reviews
# ---------------------------------------------------------

def load_new_reviews():
    """
    Load only reviews that have not been indexed yet.
    """

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
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
                WHERE r.indexed = FALSE
                """
            )

            rows = cursor.fetchall()

    documents = []
    vector_ids = []
    database_ids = []

    for review in rows:
        review_text = f"""
Product: {review["product_name"]}
Customer review: {review["text"]}
Rating: {review["rating"]}
""".strip()

        vector_id = create_document_id(
            "review",
            review["id"],
        )

        document = Document(
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
        vector_ids.append(vector_id)
        database_ids.append(review["id"])

    return documents, vector_ids, database_ids

# ---------------------------------------------------------
# Load new policies
# ---------------------------------------------------------

def load_new_policies():
    """
    Load only store policies that have not been indexed yet.
    """

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    policy_type,
                    description,
                    conditions,
                    timeframe
                FROM store_policies
                WHERE indexed = FALSE
                """
            )
            rows = cursor.fetchall()

    documents = []
    vector_ids = []
    database_ids = []

    for policy in rows:
        policy_text = f"""
Policy type: {policy["policy_type"]}
Description: {policy["description"]}
Conditions: {policy["conditions"]}
Timeframe: {policy["timeframe"]}
""".strip()

        vector_id = create_document_id(
            "policy",
            policy["id"],
        )

        document = Document(
            page_content=policy_text,
            metadata={
                "policy_id": str(policy["id"]),
                "policy_type": policy["policy_type"],
            },
        )

        documents.append(document)
        vector_ids.append(vector_id)
        database_ids.append(policy["id"])

    return documents, vector_ids, database_ids


# ---------------------------------------------------------
# Mark source rows as indexed
# ---------------------------------------------------------

def mark_as_indexed(
    table_name: str,
    database_ids: list,
) -> None:
    """
    Mark rows as indexed only after their vectors were stored successfully.
    """

    if not database_ids:
        return

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.executemany(
                f"""
                UPDATE {table_name}
                SET indexed = TRUE
                WHERE id = %s
                """,
                [(database_id,) for database_id in database_ids],
            )

        conn.commit()


# ---------------------------------------------------------
# Common incremental indexing
# ---------------------------------------------------------

def index_new_documents(
    vector_store,
    documents: list[Document],
    vector_ids: list[str],
    database_ids: list,
    table_name: str,
    display_name: str,
) -> None:
    """
    Embed only new documents and add them to the existing vector store.
    """

    if not documents:
        logger.info("No new %s found", display_name)
        return

    logger.info(
        "Indexing %s new %s",
        len(documents),
        display_name,
    )

    # This DOES NOT recreate the vector table.
    vector_store.add_documents(
        documents=documents,
        ids=vector_ids,
    )

    # Only mark rows complete after vector insertion succeeds.
    mark_as_indexed(
        table_name,
        database_ids,
    )

    logger.info(
        "%s new %s indexed successfully",
        len(documents),
        display_name,
    )


# ---------------------------------------------------------
# Main workflow
# ---------------------------------------------------------

def main() -> None:
    logger.info("Starting incremental SmartShop indexing")

    # Run once safely. Existing rows are treated as already indexed,
    # while future inserts default to indexed=False.
    prepare_tables()

    pg_engine = create_pg_engine()

    try:
        # Products
        products_store = get_vector_store(
            pg_engine,
            PRODUCTS_VECTOR_TABLE,
        )

        product_docs, product_vector_ids, product_db_ids = (
            load_new_products()
        )

        index_new_documents(
            products_store,
            product_docs,
            product_vector_ids,
            product_db_ids,
            "products",
            "products",
        )

        # Reviews
        reviews_store = get_vector_store(
            pg_engine,
            REVIEWS_VECTOR_TABLE,
        )

        review_docs, review_vector_ids, review_db_ids = (
            load_new_reviews()
        )

        index_new_documents(
            reviews_store,
            review_docs,
            review_vector_ids,
            review_db_ids,
            "reviews",
            "reviews",
        )

        # Policies
        policies_store = get_vector_store(
            pg_engine,
            POLICIES_VECTOR_TABLE,
        )

        policy_docs, policy_vector_ids, policy_db_ids = (
            load_new_policies()
        )

        index_new_documents(
            policies_store,
            policy_docs,
            policy_vector_ids,
            policy_db_ids,
            "store_policies",
            "policies",
        )

        logger.info("Incremental indexing completed successfully")

    finally:
        asyncio.run(pg_engine.close())


if __name__ == "__main__":
    main()