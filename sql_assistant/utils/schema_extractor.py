from database.connector import get_connection

def get_database_schema():
    """Extract and format the database schema"""
    connection = get_connection()
    cursor = connection.cursor()
    
    # Get all tables
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor.fetchall()]
    
    schema = []
    
    for table in tables:
        # Get columns for each table
        cursor.execute(f"DESCRIBE {table}")
        columns = cursor.fetchall()
        
        column_definitions = []
        for column in columns:
            column_name = column[0]
            data_type = column[1]
            column_definitions.append(f"{column_name} {data_type}")
        
        table_schema = f"CREATE TABLE {table} (\n  "
        table_schema += ",\n  ".join(column_definitions)
        table_schema += "\n);"
        
        schema.append(table_schema)
    
    cursor.close()
    connection.close()
    
    return "\n\n".join(schema)
