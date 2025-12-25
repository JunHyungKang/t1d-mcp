from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv
from typing import Dict, Any, List

# Import local modules
from nightscout import NightscoutClient
from nutrition import FoodDatabase
from search import HybridSearchClient
from utils.calculator import calculate_bolus

# Load environment variables
load_dotenv()

# Initialize MCP Server
mcp = FastMCP("T1D Manager")

# Initialize Services
ns_url = os.getenv("NIGHTSCOUT_URL")
ns_secret = os.getenv("NIGHTSCOUT_SECRET")
nightscout = NightscoutClient(ns_url, ns_secret) if ns_url else None

food_db = FoodDatabase()
search_client = HybridSearchClient()

@mcp.tool()
def get_recent_cgm(count: int = 1) -> str:
    """
    Get recent CGM (Continuous Glucose Monitor) readings from Nightscout.
    Returns current glucose, direction, and trends.
    """
    if not nightscout:
        return "Error: Nightscout URL is not configured."
    
    try:
        entries = nightscout.get_sgv(count)
        if not entries:
            return "No recent data found."
        
        # Format for LLM
        result = "### 🩸 최근 혈당 데이터\n"
        for e in entries:
            direction_arrow = {
                "Flat": "→", "FortyFiveUp": "↗", "SingleUp": "↑", "DoubleUp": "↑↑",
                "FortyFiveDown": "↘", "SingleDown": "↓", "DoubleDown": "↓↓"
            }.get(e['direction'], e['direction'])
            
            result += f"- **{e['sgv']}** mg/dL ({direction_arrow}) [Delta: {e['delta']}]\n"
        return result
    except Exception as e:
        return f"Error fetching CGM data: {str(e)}"

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
