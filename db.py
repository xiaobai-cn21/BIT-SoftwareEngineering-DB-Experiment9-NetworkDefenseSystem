import psycopg2
from config import DB_CONFIG
from config import DB_CONFIG2


def get_db_connection():
    try:
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

def get_db_connection_baiqinyu():
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG2["host"],
            port=DB_CONFIG2["port"],
            database=DB_CONFIG2["database"],
            user=DB_CONFIG2["user"],
            password=DB_CONFIG2["password"]
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise