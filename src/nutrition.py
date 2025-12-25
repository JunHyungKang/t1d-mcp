from typing import Dict, Optional, Any
# In real production, we might use a public API like FoodSafetyKorea
# For stability in this completion, we use a robust local dictionary for common diabetic-relevant foods.

FOOD_DB = {
    "현미밥": {"carbs": 23, "unit": "100g", "desc": "식이섬유가 풍부해 혈당 스파이크가 적음"},
    "백미밥": {"carbs": 28, "unit": "100g", "desc": "흡수가 빨라 혈당이 급격히 오를 수 있음"},
    "사과": {"carbs": 14, "unit": "100g (반 쪽)", "desc": "껍질째 먹으면 좋음"},
    "바나나": {"carbs": 23, "unit": "100g (중간 크기 1개)", "desc": "숙성될수록 당도가 높음"},
    "우유": {"carbs": 5, "unit": "100ml", "desc": "유당이 있어 혈당을 완만히 올림"},
    "피자": {"carbs": 30, "unit": "1조각 (약 100g)", "desc": "지방이 많아 식사 후반 혈당 상승 주의"},
    "짜장면": {"carbs": 70, "unit": "1그릇", "desc": "고탄수화물 + 고지방으로 '피자 효과' 주의"},
    "김치찌개": {"carbs": 5, "unit": "1그릇 (건더기 위주)", "desc": "국물에는 나트륨이 많음"}
}

class FoodDatabase:
    def __init__(self):
        pass

    def search(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Search for food nutrition. 
        Returns dict with carbs info if found, else None.
        """
        # Simple substring match
        for name, info in FOOD_DB.items():
            if name in query or query in name:
                return {
                    "name": name,
                    "carbs": info["carbs"],
                    "unit": info["unit"],
                    "desc": info["desc"]
                }
        return None
