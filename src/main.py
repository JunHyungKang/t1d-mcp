from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv
from typing import Dict, Any, List

# Import local modules
from dexcom_client import DexcomClient
# ... imports ...

@mcp.tool()
def get_recent_cgm(dexcom_username: str, dexcom_password: str, region: str = "OUS") -> str:
    """
    Get real-time CGM readings directly from Dexcom Share.
    This requires the user's Dexcom account credentials.
    
    Args:
        dexcom_username: Dexcom account ID (email or username)
        dexcom_password: Dexcom account password
        region: Account region ('OUS' for Korea/International, 'US' for USA). Default is 'OUS'.
    """
    if not dexcom_username or not dexcom_password:
        return "Error: Dexcom ID and Password are required."
    
    try:
        # Initialize Dexcom Client (Stateless)
        client = DexcomClient(dexcom_username, dexcom_password, region)
        
        # Get data
        # Fetching a bit of history to calculate delta
        readings = client.get_readings(minutes=30, max_count=2)
        
        if not readings:
            return "No recent data found from Dexcom."
        
        latest = readings[0]
        # Calculate delta if possible
        delta_str = ""
        if len(readings) > 1:
            diff = latest['sgv'] - readings[1]['sgv']
            sign = "+" if diff > 0 else ""
            delta_str = f"[Delta: {sign}{diff}]"
            
        result = f"### 🩸 실시간 덱스콤 혈당\n"
        result += f"- **{latest['sgv']}** mg/dL ({latest['direction']}) {delta_str}\n"
        result += f"- 측정 시간: {latest['time']}\n"
        
        return result

    except Exception as e:
        return f"Dexcom Error: {str(e)}"

@mcp.tool()
def calculate_insulin_dosage(current_bg: int, target_bg: int, isf: int, carbs: int, icr: int) -> str:
    """
    Calculate suggested insulin bolus (Correction + Meal).
    ALWAYS returns educational explanation detailing the calculation.
    """
    result = calculate_bolus(current_bg, target_bg, isf, carbs, icr)
    
    output = f"""
## 💉 인슐린 계산 결과
**총 권장 용량: {result['units']:.1f} 단위**

{result['explanation']}

{result['educational_content']}

{result['markdown_table']}
"""
    return output

@mcp.tool()
def search_nutrition_info(food_name: str) -> str:
    """
    Search for carbohydrate content of a food item.
    """
    info = food_db.search(food_name)
    if info:
        return f"### 🍎 {info['name']}\n- **탄수화물**: {info['carbs']}g ({info['unit']})\n- **참고**: {info['desc']}"
    else:
        return f"'{food_name}'에 대한 영양 정보를 찾을 수 없습니다."

@mcp.tool()
def search_diabetes_community(query: str) -> str:
    """
    Search Naver Blogs and Kakao Web for patient experiences and tips.
    Use this for finding non-medical life tips (e.g. snacks, patches, travel).
    """
    results = search_client.search_hybrid(query)
    if not results:
        return "검색 결과가 없습니다."
    
    output = f"### 🔍 '{query}' 커뮤니티 검색 결과\n"
    for item in results:
        icon = "🟢" if item['source'] == "Naver Blog" else "🟡"
        output += f"- {icon} [{item['title']}]({item['link']})\n"
    
    return output

if __name__ == "__main__":
    mcp.run()
