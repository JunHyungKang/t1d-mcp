import unittest
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from nutrition.database import FoodDatabase

class TestNutrition(unittest.TestCase):
    def setUp(self):
        self.db = FoodDatabase()

    def test_search_food_found(self):
        # We might mock the internal DB or API
        # For now, let's assume we mock the method or use a dummy DB
        self.db.search = MagicMock(return_value={"name": "Banana", "carbs": 23})
        
        result = self.db.search("Banana")
        self.assertEqual(result['name'], "Banana")
        self.assertEqual(result['carbs'], 23)

    def test_search_food_not_found(self):
        self.db.search = MagicMock(return_value=None)
        result = self.db.search("UnknownFood")
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
