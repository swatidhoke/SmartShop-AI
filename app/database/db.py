import os
import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()

def get_connection():
    return psycopg.connect(
        os.getenv("DATABASE_URL"),
        row_factory=dict_row
    )
