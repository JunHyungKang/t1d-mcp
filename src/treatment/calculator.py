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
    
    # Detailed text explanation
    explanation = (
        f"### 🧮 인슐린 계산 상세\n"
        f"- **교정 인슐린** (높은 혈당 잡기): `({current_bg} - {target_bg}) ÷ {isf} = {correction_units:.2f}단위`\n"
        f"- **식사 인슐린** (밥 먹는 것 커버): `{carbs}g ÷ {icr} = {meal_units:.2f}단위`\n"
        f"- **총 필요량**: `{total_units:.2f} 단위`\n\n"
        f"_(※ 실제 주입 시에는 펜/펌프 단위에 맞춰 반올림하세요)_"
    )
    
    return {
        "units": total_units,
        "correction_units": correction_units,
        "meal_units": meal_units,
        "explanation": explanation,
        "educational_content": edu["simple_logic"], # Short text
        "markdown_table": edu["markdown_table"],
        "mermaid_diagram": edu["mermaid_diagram"]
    }
