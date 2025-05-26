import unittest
from models.sql_generator import generate_sql
from utils.schema_extractor import get_database_schema

class TestSQLGeneration(unittest.TestCase):
    
    def setUp(self):
        self.schema = get_database_schema()
    
    def test_simple_query(self):
        question = "How many employees are there?"
        sql = generate_sql(question, self.schema)
        self.assertIn("SELECT", sql)
        self.assertIn("FROM", sql)
    
    def test_complex_query(self):
        question = "What is the average salary by department?"
        sql = generate_sql(question, self.schema)
        self.assertIn("AVG", sql)
        self.assertIn("GROUP BY", sql)

if __name__ == "__main__":
    unittest.main()
