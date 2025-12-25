import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Assuming we put logic in treatment/calculator.py
from treatment.calculator import calculate_bolus

class TestBolusCalculator(unittest.TestCase):
    def test_calculate_correction_only(self):
        # BG: 200, Target: 100, ISF: 50, Carbs: 0, ICR: 10
        # (200 - 100) / 50 = 2.0 units
        result = calculate_bolus(current_bg=200, target_bg=100, isf=50, carbs=0, icr=10)
        self.assertAlmostEqual(result['units'], 2.0)
        self.assertIn("교정 인슐린", result['explanation'])

    def test_calculate_carb_only(self):
        # BG: 100, Target: 100, ISF: 50, Carbs: 50, ICR: 10
        # (50 / 10) = 5.0 units
        result = calculate_bolus(current_bg=100, target_bg=100, isf=50, carbs=50, icr=10)
        self.assertAlmostEqual(result['units'], 5.0)
        self.assertIn("식사 인슐린", result['explanation'])

    def test_calculate_total(self):
        # BG: 200, Target: 100, ISF: 50 (Cor: 2u)
        # Carbs: 50, ICR: 10 (Carb: 5u)
        # Total: 7u
        result = calculate_bolus(current_bg=200, target_bg=100, isf=50, carbs=50, icr=10)
        self.assertAlmostEqual(result['units'], 7.0)

    def test_negative_correction(self):
        # BG: 80, Target: 100 -> Negative correction should be treated carefully
        # Usually pumps subtract, but MDI usually doesn't reduce meal bolus unless critical
        # For safety, let's assume simple subtraction but warn if total < 0
        # (80 - 100) / 50 = -0.4
        # Carbs: 50 / 10 = 5.0
        # Total: 4.6
        result = calculate_bolus(current_bg=80, target_bg=100, isf=50, carbs=50, icr=10)
        self.assertAlmostEqual(result['units'], 4.6)

    def test_visual_explanation(self):
        # Check if markdown table/explanation exists
        result = calculate_bolus(current_bg=200, target_bg=100, isf=50, carbs=50, icr=10)
        self.assertIn("| 구분 |", result['markdown_table'])
        self.assertIn("기저 인슐린", result['markdown_table'])
        self.assertIn("기초", result['educational_content'])

if __name__ == '__main__':
    unittest.main()
