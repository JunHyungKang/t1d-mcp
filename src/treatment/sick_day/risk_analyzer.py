"""
Sick Day Risk Analyzer for Type 1 Diabetes

This module provides risk analysis functionality that combines
blood glucose levels and symptoms to generate personalized
sick day management recommendations.

All analysis logic is based on ISPAD and ADA clinical guidelines.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from .knowledge_base import (
    GLUCOSE_RISK_LEVELS,
    KETONE_RISK_LEVELS,
    SYMPTOM_GUIDELINES,
    EMERGENCY_CRITERIA,
    SICK_DAY_ESSENTIAL_RULES,
    HYDRATION_GUIDELINES,
    RiskLevel
)


@dataclass
class GlucoseRiskResult:
    """Result of glucose risk analysis."""
    level: RiskLevel
    category: str
    emoji: str
    name_ko: str
    actions: List[str]
    follow_up: str
    source: str


@dataclass
class SymptomRiskResult:
    """Result of symptom risk analysis."""
    symptom_key: str
    name_ko: str
    glucose_impact: str
    risk_multiplier: float
    advice: List[str]
    warning_signs: List[str]
    source: str


@dataclass
class CombinedRiskResult:
    """Combined risk analysis result."""
    overall_level: RiskLevel
    overall_emoji: str
    overall_description: str
    glucose_status: Optional[GlucoseRiskResult]
    symptom_advice: List[SymptomRiskResult]
    priority_actions: List[str]
    hydration_advice: str
    essential_rules: List[str]
    emergency_warnings: List[str]
    needs_medical_attention: bool


def get_glucose_risk(glucose_mg_dl: int) -> GlucoseRiskResult:
    """
    Analyze glucose level and return risk assessment.
    
    Args:
        glucose_mg_dl: Blood glucose in mg/dL
        
    Returns:
        GlucoseRiskResult with risk level and recommended actions
        
    Based on: ISPAD 2024, ADA Standards of Care
    """
    for category, data in GLUCOSE_RISK_LEVELS.items():
        min_val, max_val = data["range_mg_dl"]
        if min_val <= glucose_mg_dl < max_val:
            return GlucoseRiskResult(
                level=data["level"],
                category=category,
                emoji=data["emoji"],
                name_ko=data["name_ko"],
                actions=data["actions"],
                follow_up=data["follow_up"],
                source=data["source"]
            )
    
    # Default to highest risk if out of expected range
    data = GLUCOSE_RISK_LEVELS["dka_risk"]
    return GlucoseRiskResult(
        level=data["level"],
        category="dka_risk",
        emoji=data["emoji"],
        name_ko=data["name_ko"],
        actions=data["actions"],
        follow_up=data["follow_up"],
        source=data["source"]
    )


def get_ketone_risk(ketone_mmol_l: float) -> Dict[str, Any]:
    """
    Analyze ketone level and return risk assessment.
    
    Args:
        ketone_mmol_l: Blood ketone level in mmol/L
        
    Returns:
        Dictionary with risk level and recommended actions
        
    Based on: ISPAD 2024
    """
    for category, data in KETONE_RISK_LEVELS.items():
        min_val, max_val = data["range_mmol_l"]
        if min_val <= ketone_mmol_l < max_val:
            return {
                "category": category,
                "level": data["level"],
                "emoji": data["emoji"],
                "name_ko": data["name_ko"],
                "actions": data["actions"],
                "source": data["source"]
            }
    
    # Default to highest risk
    data = KETONE_RISK_LEVELS["severe"]
    return {
        "category": "severe",
        "level": data["level"],
        "emoji": data["emoji"],
        "name_ko": data["name_ko"],
        "actions": data["actions"],
        "source": data["source"]
    }


def get_symptom_advice(symptom_key: str) -> Optional[SymptomRiskResult]:
    """
    Get advice for a specific symptom.
    
    Args:
        symptom_key: Symptom identifier (e.g., 'fever', 'vomiting')
        
    Returns:
        SymptomRiskResult or None if symptom not found
    """
    # Normalize input - support Korean and English
    symptom_mapping = {
        "발열": "fever",
        "열": "fever",
        "구토": "vomiting",
        "토함": "vomiting",
        "설사": "diarrhea",
        "메스꺼움": "nausea",
        "속이 안좋음": "nausea",
        "감기": "cold_flu",
        "독감": "cold_flu",
        "감염": "infection",
    }
    
    normalized_key = symptom_mapping.get(symptom_key.strip(), symptom_key.lower().strip())
    
    if normalized_key in SYMPTOM_GUIDELINES:
        data = SYMPTOM_GUIDELINES[normalized_key]
        return SymptomRiskResult(
            symptom_key=normalized_key,
            name_ko=data["name_ko"],
            glucose_impact=data["glucose_impact"],
            risk_multiplier=data["risk_multiplier"],
            advice=data["advice"],
            warning_signs=data["warning_signs"],
            source=data["source"]
        )
    return None


def parse_symptoms(symptoms_input: str) -> List[str]:
    """
    Parse symptom input string into list of symptom keys.
    
    Supports:
    - Comma-separated: "발열, 구토"
    - Korean descriptions: "열나고 토해요"
    - English: "fever, vomiting"
    """
    # Common Korean expressions to symptom mapping
    expression_mapping = {
        "열나": "fever",
        "열이": "fever",
        "고열": "fever",
        "토": "vomiting",
        "구역": "nausea",
        "메스꺼": "nausea",
        "속이 안": "nausea",
        "설사": "diarrhea",
        "배탈": "diarrhea",
        "감기": "cold_flu",
        "콧물": "cold_flu",
        "기침": "cold_flu",
        "몸살": "cold_flu",
        "독감": "cold_flu",
        "감염": "infection",
    }
    
    found_symptoms = set()
    
    # Try comma separation first
    parts = [p.strip() for p in symptoms_input.replace("、", ",").split(",")]
    
    for part in parts:
        # Direct match
        symptom = get_symptom_advice(part)
        if symptom:
            found_symptoms.add(symptom.symptom_key)
            continue
        
        # Expression matching
        for expr, key in expression_mapping.items():
            if expr in part:
                found_symptoms.add(key)
    
    return list(found_symptoms) if found_symptoms else ["cold_flu"]  # Default


def get_hydration_advice(glucose_mg_dl: Optional[int] = None) -> str:
    """
    Get hydration advice based on glucose level.
    
    Based on: ISPAD 2024, ADA Sick Day Rules
    """
    base = HYDRATION_GUIDELINES["general"]["target"]
    
    if glucose_mg_dl is None:
        return f"수분 섭취: {base}"
    
    if glucose_mg_dl > HYDRATION_GUIDELINES["glucose_high"]["threshold_mg_dl"]:
        drinks = ", ".join(HYDRATION_GUIDELINES["examples_sugar_free"])
        return f"수분 섭취: {base}\n권장 음료: {drinks} (무설탕)"
    
    if glucose_mg_dl < HYDRATION_GUIDELINES["glucose_low_normal"]["threshold_mg_dl"]:
        drinks = ", ".join(HYDRATION_GUIDELINES["examples_with_sugar"])
        return f"수분 섭취: {base}\n권장 음료: {drinks} (당분 포함 가능)"
    
    return f"수분 섭취: {base}"


def check_emergency_criteria(
    glucose_mg_dl: Optional[int] = None,
    ketone_mmol_l: Optional[float] = None,
    symptoms: Optional[List[str]] = None
) -> List[str]:
    """
    Check if any emergency criteria are met.
    
    Returns list of emergency warnings if applicable.
    """
    warnings = []
    
    # Check glucose-based emergencies
    if glucose_mg_dl is not None:
        if glucose_mg_dl < 54:
            warnings.append("⚠️ 심각한 저혈당: 즉시 15-20g 탄수화물 섭취 필요")
        elif glucose_mg_dl > 300:
            warnings.append("⚠️ DKA 위험 혈당: 케톤 측정 필수, 의료팀 연락")
    
    # Check ketone-based emergencies
    if ketone_mmol_l is not None:
        if ketone_mmol_l >= 3.0:
            warnings.append("🚨 혈중 케톤 >3.0 mmol/L: 즉시 응급실 방문 필요")
        elif ketone_mmol_l >= 1.5:
            warnings.append("⚠️ 중등도 케톤: 즉시 의료팀에 연락하세요")
    
    # Check symptom-based emergencies
    if symptoms:
        if "vomiting" in symptoms:
            warnings.append("⚠️ 구토: 2시간 이상 지속 시 응급실 방문 필요")
    
    return warnings


def analyze_sick_day_risk(
    symptoms_input: str,
    glucose_mg_dl: Optional[int] = None,
    ketone_mmol_l: Optional[float] = None
) -> CombinedRiskResult:
    """
    Comprehensive sick day risk analysis combining glucose, ketones, and symptoms.
    
    Args:
        symptoms_input: Description of symptoms (Korean or English)
        glucose_mg_dl: Current blood glucose in mg/dL (optional)
        ketone_mmol_l: Blood ketone level in mmol/L (optional)
        
    Returns:
        CombinedRiskResult with complete assessment and recommendations
        
    Based on: ISPAD 2024 Sick Day Management, ADA Standards of Care
    """
    # Parse symptoms
    symptom_keys = parse_symptoms(symptoms_input)
    symptom_results = [get_symptom_advice(s) for s in symptom_keys if get_symptom_advice(s)]
    
    # Analyze glucose if provided
    glucose_result = None
    if glucose_mg_dl is not None:
        glucose_result = get_glucose_risk(glucose_mg_dl)
    
    # Determine overall risk level
    max_level = RiskLevel.NORMAL
    
    if glucose_result and glucose_result.level.value in ["danger", "emergency"]:
        max_level = glucose_result.level
    
    for symptom in symptom_results:
        if symptom.risk_multiplier >= 2.0:
            if max_level.value == "normal":
                max_level = RiskLevel.WARNING
    
    if ketone_mmol_l and ketone_mmol_l >= 3.0:
        max_level = RiskLevel.EMERGENCY
    elif ketone_mmol_l and ketone_mmol_l >= 1.5:
        if max_level.value in ["normal", "caution"]:
            max_level = RiskLevel.WARNING
    
    # Check emergency criteria
    emergency_warnings = check_emergency_criteria(glucose_mg_dl, ketone_mmol_l, symptom_keys)
    needs_medical = len(emergency_warnings) > 0 or max_level == RiskLevel.EMERGENCY
    
    # Compile priority actions
    priority_actions = []
    
    if glucose_result:
        priority_actions.extend(glucose_result.actions[:2])
    
    for symptom in symptom_results[:2]:  # Top 2 symptoms
        priority_actions.extend(symptom.advice[:2])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_actions = []
    for action in priority_actions:
        if action not in seen:
            seen.add(action)
            unique_actions.append(action)
    
    # Get hydration advice
    hydration = get_hydration_advice(glucose_mg_dl)
    
    # Get essential rules
    essential = [rule["rule"] for rule in SICK_DAY_ESSENTIAL_RULES[:3]]
    
    # Determine emoji and description
    level_display = {
        RiskLevel.NORMAL: ("🟢", "안정적"),
        RiskLevel.CAUTION: ("🟡", "주의 필요"),
        RiskLevel.WARNING: ("🟠", "경고"),
        RiskLevel.DANGER: ("🔴", "위험"),
        RiskLevel.EMERGENCY: ("🚨", "응급")
    }
    emoji, desc = level_display.get(max_level, ("🟡", "주의 필요"))
    
    return CombinedRiskResult(
        overall_level=max_level,
        overall_emoji=emoji,
        overall_description=desc,
        glucose_status=glucose_result,
        symptom_advice=symptom_results,
        priority_actions=unique_actions,
        hydration_advice=hydration,
        essential_rules=essential,
        emergency_warnings=emergency_warnings,
        needs_medical_attention=needs_medical
    )


def serialize_sick_day_result(result: CombinedRiskResult, symptoms_input: str) -> Dict[str, Any]:
    """
    Serialize the risk analysis result into a structured dictionary for LLM consumption.
    
    Args:
        result: CombinedRiskResult from analyze_sick_day_risk
        symptoms_input: Original symptom input for context
        
    Returns:
        Dictionary containing structured risk data
    """
    # Helper to serialize dataclasses safely
    def _to_dict(obj):
        if hasattr(obj, '__dict__'):
            data = {}
            for k, v in obj.__dict__.items():
                if hasattr(v, 'value'):  # Enum
                    data[k] = v.value
                elif isinstance(v, list):
                    data[k] = [_to_dict(i) for i in v]
                elif hasattr(v, '__dict__'):
                    data[k] = _to_dict(v)
                else:
                    data[k] = v
            return data
        return obj

    data = {
        "summary": {
            "overall_risk_level": result.overall_level.value,
            "description": result.overall_description,
            "emoji": result.overall_emoji,
            "input_symptoms": symptoms_input,
            "medical_attention_needed": result.needs_medical_attention
        },
        "analysis": {
            "symptoms": [_to_dict(s) for s in result.symptom_advice],
            "emergency_warnings": result.emergency_warnings,
            "priority_actions": result.priority_actions,
        },
        "guidelines": {
            "hydration_advice": result.hydration_advice,
            "essential_rules": result.essential_rules,
        },
        "sources": ["ISPAD Clinical Practice Consensus Guidelines 2024", "ADA Standards of Care in Diabetes"]
    }

    if result.glucose_status:
        data["analysis"]["glucose_status"] = _to_dict(result.glucose_status)
        
    return data
