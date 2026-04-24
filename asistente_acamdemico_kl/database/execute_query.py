from database.connection import get_connection

def run_query(sql):

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()