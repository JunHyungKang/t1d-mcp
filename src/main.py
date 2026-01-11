from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
import os
import httpx
from dotenv import load_dotenv
from typing import Dict, Any, List

# Import local modules
from src.cgm.dexcom import DexcomClient
from src.cgm.nightscout import NightscoutClient
from src.nutrition.database import FoodDatabase
from src.community.search import HybridSearchClient
from src.treatment.calculator import calculate_bolus

# Load environment variables
load_dotenv()

# Transport security settings for Fly.io deployment
# Allows the Fly.io proxy Host header to pass validation
transport_security = TransportSecuritySettings(
    enable_dns_rebinding_protection=True,
    allowed_hosts=["t1d-mcp.fly.dev", "localhost", "localhost:8080", "127.0.0.1:8080"],
    allowed_origins=["*"],  # PlayMCP에서 접근 허용
)

# Initialize MCP Server with transport security
mcp = FastMCP("T1D Manager", transport_security=transport_security)

# Initialize Services
food_db = FoodDatabase()
search_client = HybridSearchClient()

@mcp.tool()
def calculate_insulin_dosage(current_bg: int, target_bg: int, isf: int, carbs: int, icr: int) -> str:
    """
    Calculate suggested insulin bolus dose for Type 1 diabetes management.

    This tool calculates both correction dose (for high blood glucose) and
    meal dose (for carbohydrate intake) using standard formulas.

    Use this when a user asks:
    - "How much insulin should I take?"
    - "Calculate my bolus for this meal"
    - "I need to correct my high blood sugar"

    Args:
        current_bg: Current blood glucose level in mg/dL
        target_bg: Target blood glucose level in mg/dL (typically 100-120)
        isf: Insulin Sensitivity Factor - how much 1 unit lowers glucose (mg/dL)
        carbs: Carbohydrates to be consumed in grams
        icr: Insulin-to-Carb Ratio - grams of carbs covered by 1 unit

    Returns:
        JSON with correction_dose, meal_dose, total_dose, and calculation breakdown
    """
    import json
    result = calculate_bolus(current_bg, target_bg, isf, carbs, icr)
    return json.dumps(result, ensure_ascii=False)

@mcp.tool()
def search_nutrition_info(food_name: str) -> str:
    """
    Search for carbohydrate content of a food item in the nutrition database.

    Use this tool when a user asks about carbs in food for insulin calculation,
    such as "How many carbs in rice?" or "탄수화물 정보 알려줘".

    Args:
        food_name: Name of the food item in Korean or English

    Returns:
        Formatted nutrition info with carbohydrate content per serving
    """
    info = food_db.search(food_name)
    if info:
        return f"### 🍎 {info['name']}\n- **탄수화물**: {info['carbs']}g ({info['unit']})\n- **참고**: {info['desc']}"
    else:
        return f"'{food_name}'에 대한 영양 정보를 찾을 수 없습니다."

@mcp.tool()
def search_diabetes_community(query: str) -> str:
    """
    Search Korean blogs and web pages for Type 1 diabetes patient experiences and tips.

    Use this tool to find real-world advice from the diabetes community, such as:
    - Low blood sugar snack recommendations
    - CGM sensor patch tips
    - Travel advice for diabetics
    - Daily life management tips

    Args:
        query: Search query in Korean or English

    Returns:
        JSON array of search results with title, link, and source
    """
    import json
    results = search_client.search_hybrid(query)
    
    # Add source icons for better structured data context
    for item in results:
        if item.get("source") == "Naver Blog":
            item["icon"] = "🟢"
        elif item.get("source") == "Kakao Web":
            item["icon"] = "🟡"
            
    return json.dumps(results, ensure_ascii=False)

@mcp.tool()
def analyze_sick_day_guidelines(
    symptoms: str = "감기 기운",
    current_glucose_mg_dl: int | None = None,
    ketone_mmol_l: float | None = None
) -> str:
    """
    Analyze sick day risks and retrieve clinical guidelines based on patient status.
    
    Use this tool when the user reports being unwell. It returns evidence-based
    recommendations (JSON) from ISPAD/ADA guidelines to help the LLM generate
    safe and personalized medical advice.
    
    Args:
        symptoms: User's reported symptoms (comma-separated).
        current_glucose_mg_dl: Current blood glucose in mg/dL (optional).
        ketone_mmol_l: Current blood ketone level in mmol/L (optional).
        
    Returns:
        JSON string containing risk level, advice, and emergency warnings.
    """
    import json
    from src.treatment.sick_day.risk_analyzer import (
        analyze_sick_day_risk,
        serialize_sick_day_result
    )
    
    result = analyze_sick_day_risk(
        symptoms_input=symptoms,
        glucose_mg_dl=current_glucose_mg_dl,
        ketone_mmol_l=ketone_mmol_l
    )
    
    # Return JSON string for MCP compatibility
    return json.dumps(serialize_sick_day_result(result, symptoms), ensure_ascii=False)


@mcp.tool()
def get_sick_day_quick_check(current_glucose_mg_dl: int) -> str:
    """
    Quick glucose risk check during sick day.
    Returns immediate action recommendations based on current blood glucose.
    
    Based on ISPAD 2024 sick day target range (70-180 mg/dL).
    
    Args:
        current_glucose_mg_dl: Current blood glucose in mg/dL.
        
    Returns:
        Risk level and immediate actions to take.
    """
    from src.treatment.sick_day.risk_analyzer import get_glucose_risk
    
    result = get_glucose_risk(current_glucose_mg_dl)
    
    output = f"""
### 🩸 혈당 상태: {result.emoji} {result.name_ko}

**현재 혈당**: {current_glucose_mg_dl} mg/dL

**즉시 조치**:
"""
    for action in result.actions:
        output += f"- {action}\n"
    
    output += f"\n**후속 조치**: {result.follow_up}\n"
    output += f"\n_출처: {result.source}_"
    
    return output




# ... existing tools ...

# ===== Dexcom Developer API (Official Sandbox) Tools =====

from src.cgm.dexcom_official import DexcomOfficialClient, format_egvs_for_display

@mcp.tool()
def get_dexcom_auth_url(client_id: str, client_secret: str, redirect_uri: str = "http://localhost:8080/callback") -> str:
    """
    Generate Dexcom OAuth authorization URL for Sandbox environment.
    
    Use this to get the URL where users can authorize your app.
    In Sandbox mode, no password is required - users select from a dropdown.
    
    Args:
        client_id: OAuth client ID from Dexcom Developer Portal
        client_secret: OAuth client secret (stored for later token exchange)
        redirect_uri: Callback URL registered with your Dexcom app
        
    Returns:
        Authorization URL to redirect the user to
    """
    client = DexcomOfficialClient(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        sandbox=True
    )
    
    auth_url = client.get_authorization_url(state="mcp_sandbox_test")
    
    return f"""
### 🔐 Dexcom OAuth 인증 URL (Sandbox)

**아래 URL로 이동하여 인증하세요:**

[인증 페이지 열기]({auth_url})

> [!NOTE]
> Sandbox 환경에서는 비밀번호 입력 없이 드롭다운에서 테스트 사용자를 선택합니다.
> 사용 가능한 테스트 사용자: SandboxUser1 ~ SandboxUser7 (SandboxUser7은 G7 데이터)

인증 완료 후 redirect_uri로 돌아오는 URL에서 `code` 파라미터를 확인하세요.
그 코드를 `get_cgm_sandbox` 도구에 전달하면 혈당 데이터를 조회할 수 있습니다.
"""


@mcp.tool()
async def get_cgm_sandbox(
    client_id: str,
    client_secret: str,
    authorization_code: str,
    redirect_uri: str = "http://localhost:8080/callback"
) -> str:
    """
    Get CGM data from Dexcom Developer API Sandbox using authorization code.
    
    This tool uses the official Dexcom API (not Share API) and works with
    the Sandbox environment, which provides simulated CGM data for testing.
    
    Args:
        client_id: OAuth client ID from Dexcom Developer Portal
        client_secret: OAuth client secret from Dexcom Developer Portal
        authorization_code: Code received from OAuth callback after user authorization
        redirect_uri: Same redirect_uri used in get_dexcom_auth_url
        
    Returns:
        Formatted CGM data from the last 24 hours
    """
    try:
        client = DexcomOfficialClient(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            sandbox=True
        )
        
        # Exchange authorization code for access token
        token_response = await client.exchange_code_for_token(authorization_code)
        access_token = token_response.get("access_token")
        
        if not access_token:
            return "❌ 토큰 교환 실패: access_token을 받지 못했습니다."
        
        # Get EGV data
        egvs_data = await client.get_egvs(access_token)
        
        # Format for display
        result = format_egvs_for_display(egvs_data, limit=10)
        result += "\n\n> ✅ Dexcom Developer API Sandbox에서 데이터를 성공적으로 조회했습니다."
        
        return result
        
    except httpx.HTTPStatusError as e:
        return f"❌ API 오류: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"❌ 오류 발생: {str(e)}"


@mcp.tool()
async def get_cgm_with_token(
    access_token: str,
    hours: int = 24,
    sandbox: bool = True
) -> str:
    """
    Get CGM data using an existing access token.
    
    Use this if you already have a valid access token from a previous OAuth flow.
    
    Args:
        access_token: Valid OAuth access token
        hours: Number of hours of data to retrieve (default: 24, max: 720 for 30 days)
        sandbox: Whether to use sandbox environment (default: True)
        
    Returns:
        Formatted CGM data
    """
    from datetime import datetime, timedelta
    
    try:
        # Create a minimal client just for API calls
        base_url = (
            "https://sandbox-api.dexcom.com" if sandbox 
            else "https://api.dexcom.com"
        )
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(hours=min(hours, 720))  # Max 30 days
        
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                f"{base_url}/v3/users/self/egvs",
                params={
                    "startDate": start_date.strftime("%Y-%m-%dT%H:%M:%S"),
                    "endDate": end_date.strftime("%Y-%m-%dT%H:%M:%S"),
                },
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            egvs_data = response.json()
        
        result = format_egvs_for_display(egvs_data, limit=10)
        env_label = "Sandbox" if sandbox else "Production"
        result += f"\n\n> ✅ Dexcom Developer API ({env_label})에서 조회 완료"
        
        return result
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return "❌ 인증 실패: 토큰이 만료되었거나 유효하지 않습니다. 다시 인증해주세요."
        return f"❌ API 오류: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"❌ 오류 발생: {str(e)}"

