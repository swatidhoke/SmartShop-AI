from pathlib import Path
import sys
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from database.db import get_connection

load_dotenv()

def test_connection():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT current_database();")
            db_name = cursor.fetchone()

            print("✅ Connected to:", db_name)

test_connection()