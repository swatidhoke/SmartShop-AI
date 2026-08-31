from app.database.db import get_connection

def test_connection():
    """Verify the app can open a connection to PostgreSQL."""

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT current_database();")
            row = cursor.fetchone()

            assert row is not None
