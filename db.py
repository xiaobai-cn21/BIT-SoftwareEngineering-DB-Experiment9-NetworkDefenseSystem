import psycopg2
from config import DB_CONFIG


def get_db_connection():
    try:
        print(DB_CONFIG)
        print(DB_CONFIG["host"])
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

