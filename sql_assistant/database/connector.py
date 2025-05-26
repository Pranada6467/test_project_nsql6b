import mysql.connector

# Establish connection
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='forget@7',  
    database='employees'
)

cursor = conn.cursor()


query = query = """
SELECT e.emp_no, e.first_name, e.last_name, d.dept_name
FROM employees e
JOIN dept_emp de ON e.emp_no = de.emp_no
JOIN departments d ON de.dept_no = d.dept_no
WHERE d.dept_no = 'd005'
LIMIT 10;
"""
cursor.execute(query)


for row in cursor.fetchall():
    print(row)


cursor.close()
conn.close()


from config.config import DB_CONFIG

def get_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        raise
