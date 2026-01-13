from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
import os
import httpx
from dotenv import load_dotenv
from typing import Dict, Any, List

# Import local modules
from src.community.search import HybridSearchClient
from src.treatment.calculator import calculate_bolus

# Load environment variables
load_dotenv()

# Transport security settings for Fly.io deployment
# Allows the Fly.io proxy Host header to pass validation
transport_security = TransportSecuritySettings(
    enable_dns_rebinding_protection=True,
    allowed_hosts=["t1d-mcp.fly.dev", "t1d-mcp-lite.fly.dev", "localhost", "localhost:8080", "127.0.0.1:8080"],
    allowed_origins=["*"],  # PlayMCP에서 접근 허용
)

# Initialize MCP Server with transport security
mcp = FastMCP("T1D Manager", transport_security=transport_security)

# Initialize Services
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
        elif item.get("source") == "Daum Web":
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


# ===== Dexcom Developer API (Official Sandbox) Tools =====
# Conditionally enabled via ENABLE_DEXCOM environment variable
# These tools require OAuth authentication

ENABLE_DEXCOM = os.getenv("ENABLE_DEXCOM", "true").lower() == "true"

if ENABLE_DEXCOM:
    from src.tools.dexcom_tools import register_dexcom_tools
    register_dexcom_tools(mcp)
