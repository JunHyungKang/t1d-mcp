from typing import Dict, Any, Union
from .visualizer import get_insulin_education

def calculate_bolus(current_bg: int, target_bg: int, isf: int, carbs: int, icr: int) -> Dict[str, Any]:
    """
    Calculates insulin bolus units based on user parameters.
    Returns calculation breakdown and educational visuals.
    """
    
    # 1. Correction Bolus (교정량: 현재 혈당 - 목표 혈당)
    bg_diff = current_bg - target_bg
    correction_units = bg_diff / isf
    
    # 2. Meal Bolus (식사량: 탄수화물 / 탄수비)
    meal_units = carbs / icr
    
    total_units = correction_units + meal_units
    
    # Generate Education Content
    edu = get_insulin_education()
    
    return {
        "calculation": {
            "total_units": round(total_units, 2),
            "correction_units": round(correction_units, 2),
            "meal_units": round(meal_units, 2),
            "formula": {
                "correction": f"({current_bg} - {target_bg}) / {isf}",
                "meal": f"{carbs} / {icr}"
            }
        },
        "educational": {
            "simple_logic": edu["simple_logic"],
            "analogy_table": edu["markdown_table"], # Keeping markdown table as it's complex to structure purely
            "mermaid_diagram": edu["mermaid_diagram"]
        }
    }
