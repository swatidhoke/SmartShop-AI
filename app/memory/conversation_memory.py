import logging
import os

from langgraph.checkpoint.postgres import PostgresSaver
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool


logger = logging.getLogger(__name__)


database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise ValueError(
        "DATABASE_URL is not configured."
    )


conversation_pool = ConnectionPool(
    conninfo=database_url,
    min_size=1,
    max_size=5,
    kwargs={
        "autocommit": True,
        "prepare_threshold": 0,
        "row_factory": dict_row,
    },
)


conversation_checkpointer = PostgresSaver(
    conversation_pool
)


def setup_conversation_memory() -> None:
    """
    Create LangGraph checkpoint tables if needed.

    Call this once when the application starts.
    """

    logger.info(
        "Setting up LangGraph conversation persistence"
    )

    conversation_checkpointer.setup()

    logger.info(
        "Conversation persistence ready"
    )


def close_conversation_memory() -> None:
    """Close PostgreSQL connections."""

    conversation_pool.close()