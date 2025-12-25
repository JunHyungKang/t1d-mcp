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

from main import activate_sick_day_mode, get_glucose_status_with_empathy

class TestMCPTools(unittest.TestCase):
    def test_sick_day_mode(self):
        result = activate_sick_day_mode("열이 나요")
        self.assertIn("아픈 날(Sick Day) 모드 시작", result)
        self.assertIn("열이 나요", result)
        self.assertIn("기저 인슐린은 절대 중단하면 안 됩니다", result)

    @patch('main.get_recent_cgm')
    def test_empathy_normal(self, mock_cgm):
        # Mock CGM tool returning standard data
        mock_cgm.return_value = "- **120** mg/dL (→) [Delta: 0]"
        
        result = get_glucose_status_with_empathy("user", "pass")
        
        # Check if original data is preserved
        self.assertIn("120", result)
        # Check if empathy comment is added
        self.assertIn("🤖 AI 코멘트", result)
        self.assertIn("수치가 안정적이라면", result)

    @patch('main.get_recent_cgm')
    def test_empathy_error(self, mock_cgm):
        mock_cgm.return_value = "Error: Dexcom Login Failed"
        
        result = get_glucose_status_with_empathy("user", "pass")
        
        self.assertIn("Error", result)
        self.assertIn("연결에 잠시 문제가 생긴 것 같아요", result)

if __name__ == '__main__':
    unittest.main()
