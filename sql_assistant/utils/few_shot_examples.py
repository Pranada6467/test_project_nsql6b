# Few-shot examples for the employee database
EMPLOYEE_DB_EXAMPLES = [
    {
        "question": "How many employees are there in total?",
        "sql": "SELECT COUNT(*) FROM employees;",
        "keywords": ["count", "total", "employees", "how many"]
    },
    {
        "question": "List all departments",
        "sql": "SELECT dept_name FROM departments;",
        "keywords": ["list", "departments", "all departments"]
    },
    {
        "question": "Find employees in the Sales department",
        "sql": "SELECT e.first_name, e.last_name FROM employees e JOIN dept_emp de ON e.emp_no = de.emp_no JOIN departments d ON de.dept_no = d.dept_no WHERE d.dept_name = 'Sales';",
        "keywords": ["sales", "department", "employees in"]
    },
    {
        "question": "What is the average salary by department?",
        "sql": "SELECT d.dept_name, AVG(s.salary) as avg_salary FROM departments d JOIN dept_emp de ON d.dept_no = de.dept_no JOIN salaries s ON de.emp_no = s.emp_no GROUP BY d.dept_name;",
        "keywords": ["average", "salary", "department", "group by"]
    },
    {
        "question": "Find the highest paid employee",
        "sql": "SELECT e.first_name, e.last_name, s.salary FROM employees e JOIN salaries s ON e.emp_no = s.emp_no ORDER BY s.salary DESC LIMIT 1;",
        "keywords": ["highest", "paid", "maximum", "salary", "top"]
    },
    {
        "question": "Show employees hired after 2000",
        "sql": "SELECT first_name, last_name, hire_date FROM employees WHERE hire_date > '2000-01-01';",
        "keywords": ["hired", "after", "date", "2000"]
    },
    {
        "question": "Count employees by gender",
        "sql": "SELECT gender, COUNT(*) as count FROM employees GROUP BY gender;",
        "keywords": ["count", "gender", "group by"]
    },
    {
        "question": "Find all managers",
        "sql": "SELECT DISTINCT e.first_name, e.last_name FROM employees e JOIN dept_manager dm ON e.emp_no = dm.emp_no;",
        "keywords": ["managers", "manager", "distinct"]
    }
]

def get_examples():
    """Return the list of few-shot examples"""
    return EMPLOYEE_DB_EXAMPLES

def add_custom_example(question, sql, keywords):
    """Add a new example to the list"""
    new_example = {
        "question": question,
        "sql": sql,
        "keywords": keywords
    }
    EMPLOYEE_DB_EXAMPLES.append(new_example)
    return True
