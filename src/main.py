from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv
from typing import Dict, Any, List

# Import local modules
from cgm.dexcom import DexcomClient
from cgm.nightscout import NightscoutClient
from nutrition.database import FoodDatabase
from community.search import HybridSearchClient
from treatment.calculator import calculate_bolus

# Load environment variables
load_dotenv()

# Initialize MCP Server
mcp = FastMCP("T1D Manager")

# Initialize Services
food_db = FoodDatabase()
search_client = HybridSearchClient()

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

@mcp.tool()
def activate_sick_day_mode(symptoms: str = "감기 기운") -> str:
    """
    Activate 'Sick Day Rules' when the user feels unwell.
    Returns specific guidelines for managing T1D during illness.
    
    Args:
        symptoms: User's reported symptoms (e.g., "cold", "fever").
    """
    return f"""
### 🚨 아픈 날(Sick Day) 모드 시작
어머니, 많이 편찮으신가요? ('{symptoms}')
몸이 아프면 스트레스 호르몬 때문에 **혈당이 평소보다 오를 수 있어요.**

**✅ 지금 지켜주세요:**
1. **혈당 체크**: 평소보다 자주 (2~4시간 간격) 확인해주세요.
2. **인슐린**: 식사를 못 하셔도 **기저 인슐린은 절대 중단하면 안 됩니다.**
3. **수분 섭취**: 탈수를 막기 위해 물을 1시간에 한 컵씩 꼭 드세요. 💧
4. **응급 상황**: 구토가 멈추지 않거나 숨쉬기 힘들면 바로 병원에 가셔야 합니다.

제가 더 자주 상태를 여쭤볼게요. 무리하지 마시고 푹 쉬세요. 힘내세요! 💖
"""

@mcp.tool()
def get_glucose_status_with_empathy(dexcom_username: str, dexcom_password: str, region: str = "OUS") -> str:
    """
    Check current glucose with a warm, empathetic persona.
    Analyzes trends and gives context (e.g., "It seems to be stable").
    """
    cgm_result = get_recent_cgm(dexcom_username, dexcom_password, region)
    
    # Simple logic to add empathy based on the result string using keyword matching
    # In a real scenario, LLM does this, but we can hint strongly in the return value
    
    msg = cgm_result + "\n\n"
    msg += "--- \n**🤖 AI 코멘트**:\n"
    
    if "Error" in cgm_result:
        msg += "어머니, 연결에 잠시 문제가 생긴 것 같아요. 인터넷 연결을 한번 확인해주시겠어요?"
    elif "No recent data" in cgm_result:
        msg += "데이터가 아직 안 넘어왔네요. 센서가 조금 멀리 있나요?"
    else:
        # Extract number roughly for logic (This is a naive parsing for demo)
        # Real logic should happen in get_recent_cgm or here by calling client directly
        # But to avoid re-calling, we rely on the string output or LLM's interpretation.
        # Let's trust LLM to convert this data into empathy, 
        # BUT we provide the 'Persona Instruction' as a distinct return block.
        
        msg += "어머니, 식사하신 게 소화되고 있나요? "
        msg += "수치가 안정적이라면 무리하지 마시고 편안하게 계세요. "
        msg += "혹시 조금 높더라도 교정 인슐린이 도와줄 거니까 너무 걱정 마시고요. 🍵"
    
    return msg

# ... existing tools ...
