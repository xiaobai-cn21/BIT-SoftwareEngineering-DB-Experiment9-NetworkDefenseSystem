from db import get_db_connection
from .tableCreator import tableCreator

def getInformation(sql_query, params=None):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(sql_query, params or ())
        
        results = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        
        table = tableCreator(columns, results)
        return table

    except Exception as e:
        print(f"Error executing query: {e}")
        return None
    
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    tables = execute_sql_query("SELECT * FROM information_schema.tables;")
    if tables:
        for row in tables:
            print(row)