from database.connector import get_connection

def execute_query(query, fetch_all=True):
    """Execute a SQL query and return results"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute(query)
        if fetch_all:
            results = cursor.fetchall()
        else:
            results = cursor.fetchone()
        return results
    except Exception as e:
        return {"error": str(e)}
    finally:
        cursor.close()
        connection.close()
