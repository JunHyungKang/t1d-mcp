import unittest
import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import main to access tools logic (functions)
# Since they are decorated, we can still call them if FastMCP allows, 
# or we can import the underlying logic if separated.
# FastMCP decorators usually wrap the function. Calling the decorated function 
# might try to invoke MCP RPC context or just run the function.
# Let's inspect implementation of activate_sick_day_mode first.
# It returns string, no side effects.

from src.main import analyze_sick_day_guidelines

class TestMCPTools(unittest.TestCase):
    def test_sick_day_mode(self):
        import json
        result = analyze_sick_day_guidelines("열이 나요")
        data = json.loads(result)
        
        # Verify JSON structure
        self.assertIn("summary", data)
        self.assertIn("analysis", data)
        self.assertIn("guidelines", data)
        
        # Verify specific content
        self.assertEqual(data["summary"]["input_symptoms"], "열이 나요")
        self.assertTrue(any(s["symptom_key"] == "fever" for s in data["analysis"]["symptoms"]))
        
        # Verify essential rule exists
        rules = data["guidelines"]["essential_rules"]
        self.assertTrue(any("인슐린" in r for r in rules))
        


if __name__ == '__main__':
    unittest.main()
