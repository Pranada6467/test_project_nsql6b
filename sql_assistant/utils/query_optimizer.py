import re
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

def optimize_schema_context(schema: str, question: str) -> str:
    """Reduce schema size by including only relevant tables"""
    question_lower = question.lower()
    
    # Keywords that suggest which tables might be relevant
    table_keywords = {
        'employees': ['employee', 'worker', 'staff', 'person', 'name', 'first', 'last', 'gender', 'birth', 'hire'],
        'departments': ['department', 'dept', 'division'],
        'salaries': ['salary', 'pay', 'wage', 'income', 'earn', 'money'],
        'titles': ['title', 'position', 'job', 'role'],
        'dept_emp': ['department', 'work', 'assign', 'belong'],
        'dept_manager': ['manager', 'head', 'lead', 'boss', 'manage']
    }
    
    relevant_tables = set()
    
    # Check which tables are relevant based on keywords
    for table, keywords in table_keywords.items():
        if any(keyword in question_lower for keyword in keywords):
            relevant_tables.add(table)
    
    # Always include employees as it's central to most queries
    relevant_tables.add('employees')
    
    # If asking about relationships, include junction tables
    if any(word in question_lower for word in ['department', 'manager', 'title', 'salary']):
        if 'department' in question_lower:
            relevant_tables.update(['departments', 'dept_emp'])
        if 'manager' in question_lower:
            relevant_tables.add('dept_manager')
        if 'title' in question_lower:
            relevant_tables.add('titles')
        if 'salary' in question_lower:
            relevant_tables.add('salaries')
    
    # Filter schema to include only relevant tables
    schema_lines = schema.split('\n')
    filtered_schema = []
    include_line = False
    current_table = None
    
    for line in schema_lines:
        line_stripped = line.strip()
        
        if line_stripped.startswith('CREATE TABLE'):
            # Extract table name - handle different formats
            match = re.search(r'CREATE TABLE\s+(\w+)', line, re.IGNORECASE)
            if match:
                current_table = match.group(1)
                include_line = current_table in relevant_tables
            else:
                include_line = False
        elif line_stripped.startswith(');') or line_stripped == ')':
            # End of table definition
            if include_line:
                filtered_schema.append(line)
            include_line = False
            current_table = None
            continue
        
        if include_line or line_stripped == '':
            filtered_schema.append(line)
    
    result = '\n'.join(filtered_schema)
    logger.info(f"Schema optimized: included tables {relevant_tables}")
    return result

def validate_sql_syntax(sql_query: str) -> Tuple[bool, str]:
    """Basic SQL validation and cleanup"""
    if not sql_query or not sql_query.strip():
        return False, "Empty query"
    
    sql_cleaned = sql_query.strip()
    
    # Remove common artifacts from generation
   
    sql_cleaned = re.sub(r'```\s*', '', sql_cleaned)
    sql_cleaned = sql_cleaned.replace('``````', '')
    
    # Remove extra whitespace
    sql_cleaned = ' '.join(sql_cleaned.split())
    
    sql_upper = sql_cleaned.upper().strip()
    
    # Check if it starts with SELECT
    if not sql_upper.startswith("SELECT"):
        return False, "Query must start with SELECT"
    
    # Check for balanced parentheses
    open_parens = sql_cleaned.count('(')
    close_parens = sql_cleaned.count(')')
    if open_parens != close_parens:
        return False, f"Unbalanced parentheses: {open_parens} open, {close_parens} close"
    
    # Check for basic SQL structure
    if 'FROM' not in sql_upper:
        return False, "Query must contain FROM clause"
    
    # Add semicolon if missing
    if not sql_cleaned.strip().endswith(';'):
        sql_cleaned += ';'
    
    # Check for common SQL injection patterns (basic security)
    dangerous_patterns = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE']
    for pattern in dangerous_patterns:
        # Only flag if it's not part of a SELECT statement
        if pattern in sql_upper and not sql_upper.startswith('SELECT'):
            return False, f"Potentially dangerous operation detected: {pattern}"
    
    # Basic syntax checks
    try:
        # Check for common SQL syntax issues
        if sql_upper.count('SELECT') > sql_upper.count('FROM'):
            # This might be okay for subqueries, but let's be cautious
            pass
        
        # Check for unmatched quotes
        single_quotes = sql_cleaned.count("'")
        if single_quotes % 2 != 0:
            return False, "Unmatched single quotes"
        
        double_quotes = sql_cleaned.count('"')
        if double_quotes % 2 != 0:
            return False, "Unmatched double quotes"
            
    except Exception as e:
        logger.warning(f"Error during syntax validation: {str(e)}")
    
    return True, sql_cleaned

def extract_table_names(schema: str) -> List[str]:
    """Extract table names from schema"""
    tables = []
    for line in schema.split('\n'):
        line_stripped = line.strip()
        if line_stripped.startswith('CREATE TABLE'):
            match = re.search(r'CREATE TABLE\s+(\w+)', line, re.IGNORECASE)
            if match:
                tables.append(match.group(1))
    return tables

def clean_generated_sql(sql_text: str) -> str:
    """Clean up generated SQL text"""
    if not sql_text:
        return ""
    
    # Remove markdown code blocks
    
    sql_text = re.sub(r'```\s*', '', sql_text)
    
    # Remove common artifacts
    sql_text = sql_text.replace('``````', '')
    
    
    # Clean up whitespace
    sql_text = ' '.join(sql_text.split())
    
    return sql_text.strip()
