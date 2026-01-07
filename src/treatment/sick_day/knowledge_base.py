"""
Sick Day Knowledge Base for Type 1 Diabetes Management

This module contains evidence-based clinical guidelines for managing
Type 1 Diabetes during illness (sick days).

All data is sourced from verified medical guidelines:
- ISPAD Clinical Practice Consensus Guidelines 2024
- ADA Standards of Care in Diabetes
- IDF (International Diabetes Federation) Guidelines

DISCLAIMER: This information is for educational purposes only and should
not replace professional medical advice. Always consult with your
healthcare team for personalized guidance.
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    """Risk level classification based on ISPAD/ADA guidelines."""
    NORMAL = "normal"
    CAUTION = "caution"
    WARNING = "warning"
    DANGER = "danger"
    EMERGENCY = "emergency"


# =============================================================================
# GLUCOSE RISK LEVELS
# Based on ISPAD 2024 Clinical Practice Consensus Guidelines
# and ADA Standards of Care in Diabetes
# =============================================================================

GLUCOSE_RISK_LEVELS: Dict[str, Dict[str, Any]] = {
    "severe_hypoglycemia": {
        "range_mg_dl": (0, 54),
        "range_mmol_l": (0, 3.0),
        "level": RiskLevel.EMERGENCY,
        "emoji": "🔴",
        "name_ko": "심각한 저혈당",
        "name_en": "Severe Hypoglycemia",
        "actions": [
            "의식이 있으면: 즉시 15-20g 속효성 탄수화물 섭취 (포도당, 주스, 사탕)",
            "15분 후 재측정, 여전히 낮으면 반복",
            "의식 저하 시: 글루카곤 투여 또는 119 호출"
        ],
        "follow_up": "회복 후 복합 탄수화물 섭취, 의료팀에 보고",
        "source": "ISPAD 2024 - Level 2 Hypoglycemia (<54 mg/dL)"
    },
    "hypoglycemia": {
        "range_mg_dl": (54, 70),
        "range_mmol_l": (3.0, 3.9),
        "level": RiskLevel.DANGER,
        "emoji": "🟠",
        "name_ko": "저혈당",
        "name_en": "Hypoglycemia",
        "actions": [
            "15g 속효성 탄수화물 섭취 (포도당 정제, 주스 120ml)",
            "15분 후 재측정",
            "70 mg/dL 이상 될 때까지 반복"
        ],
        "follow_up": "원인 파악 (인슐린 과다, 식사 지연, 운동 등)",
        "source": "ADA Standards of Care - Hypoglycemia Alert Value"
    },
    "low_normal": {
        "range_mg_dl": (70, 90),
        "range_mmol_l": (3.9, 5.0),
        "level": RiskLevel.CAUTION,
        "emoji": "🟡",
        "name_ko": "낮은 정상",
        "name_en": "Low Normal",
        "actions": [
            "아픈 날에는 간식 준비",
            "30분 후 재측정 권장",
            "활동 전 탄수화물 섭취 고려"
        ],
        "follow_up": "정상 범위 유지 모니터링",
        "source": "ISPAD 2024 - Sick Day Target Range (70-180 mg/dL)"
    },
    "target_range": {
        "range_mg_dl": (90, 180),
        "range_mmol_l": (5.0, 10.0),
        "level": RiskLevel.NORMAL,
        "emoji": "🟢",
        "name_ko": "목표 범위",
        "name_en": "Target Range",
        "actions": [
            "현재 관리 유지",
            "아픈 날: 2-4시간 간격 모니터링 지속",
            "수분 섭취 유지"
        ],
        "follow_up": "증상 호전까지 모니터링 지속",
        "source": "ISPAD 2024 - Sick Day Target Range (70-180 mg/dL)"
    },
    "elevated": {
        "range_mg_dl": (180, 250),
        "range_mmol_l": (10.0, 13.9),
        "level": RiskLevel.CAUTION,
        "emoji": "🟡",
        "name_ko": "높음",
        "name_en": "Elevated",
        "actions": [
            "수분 섭취 증가 (무설탕 음료)",
            "2시간 간격 모니터링",
            "케톤 측정 고려 (특히 240 mg/dL 이상 시)"
        ],
        "follow_up": "교정 인슐린 고려 (의료팀 지시에 따라)",
        "source": "ADA Standards of Care - Increased Monitoring Threshold"
    },
    "high": {
        "range_mg_dl": (250, 300),
        "range_mmol_l": (13.9, 16.7),
        "level": RiskLevel.WARNING,
        "emoji": "🟠",
        "name_ko": "매우 높음",
        "name_en": "High",
        "actions": [
            "케톤 측정 필수",
            "수분 섭취 증가 (시간당 120-180ml)",
            "의료팀에 연락하여 인슐린 조절 상담"
        ],
        "follow_up": "케톤이 양성이면 즉시 의료팀 연락",
        "source": "ADA - Check ketones if glucose >240 mg/dL"
    },
    "dka_risk": {
        "range_mg_dl": (300, 9999),
        "range_mmol_l": (16.7, 999),
        "level": RiskLevel.DANGER,
        "emoji": "🔴",
        "name_ko": "DKA 위험",
        "name_en": "DKA Risk Zone",
        "actions": [
            "즉시 케톤 측정",
            "의료팀 또는 응급실 연락",
            "수분 섭취 지속 (구토 없는 경우)",
            "추가 인슐린 용량은 의료팀 지시에 따라 투여"
        ],
        "follow_up": "케톤 >3.0 mmol/L 또는 증상 악화 시 응급실 방문",
        "source": "ISPAD 2024 - DKA Prevention, ADA Sick Day Rules"
    }
}


# =============================================================================
# KETONE RISK LEVELS
# Based on ISPAD 2024 and ADA Guidelines
# Blood ketone (beta-hydroxybutyrate) levels
# =============================================================================

KETONE_RISK_LEVELS: Dict[str, Dict[str, Any]] = {
    "normal": {
        "range_mmol_l": (0, 0.6),
        "level": RiskLevel.NORMAL,
        "emoji": "🟢",
        "name_ko": "정상",
        "name_en": "Normal",
        "actions": [
            "모니터링 지속",
            "혈당이 높으면 수분 섭취 증가"
        ],
        "source": "ISPAD 2024 - Target ketone level <0.6 mmol/L"
    },
    "mild": {
        "range_mmol_l": (0.6, 1.5),
        "level": RiskLevel.CAUTION,
        "emoji": "🟡",
        "name_ko": "경미한 케톤혈증",
        "name_en": "Mild Ketonemia",
        "actions": [
            "의료팀에 연락",
            "수분 섭취 증가",
            "추가 인슐린 투여 고려 (의료팀 지시)",
            "2시간마다 케톤 재측정"
        ],
        "source": "ISPAD 2024 - Contact diabetes team if >0.6 mmol/L"
    },
    "moderate": {
        "range_mmol_l": (1.5, 3.0),
        "level": RiskLevel.WARNING,
        "emoji": "🟠",
        "name_ko": "중등도 케톤혈증",
        "name_en": "Moderate Ketonemia",
        "actions": [
            "즉시 의료팀에 연락",
            "추가 인슐린 필요 (총 일일량의 10-20%)",
            "수분 섭취 지속",
            "1-2시간마다 혈당 및 케톤 모니터링"
        ],
        "source": "ISPAD 2024 - Moderate ketones require medical guidance"
    },
    "severe": {
        "range_mmol_l": (3.0, 999),
        "level": RiskLevel.EMERGENCY,
        "emoji": "🔴",
        "name_ko": "심각한 케톤혈증 (DKA 위험)",
        "name_en": "Severe Ketonemia (DKA Risk)",
        "actions": [
            "즉시 응급실 방문",
            "IV 수액 및 인슐린 치료 필요",
            "구토, 복통, 빠른 호흡 등 DKA 증상 확인"
        ],
        "source": "ISPAD 2024 - Blood ketones >3.0 mmol/L require hospital treatment"
    }
}


# =============================================================================
# SYMPTOM GUIDELINES
# Based on ISPAD Sick Day Management Chapter and ADA Guidelines
# =============================================================================

SYMPTOM_GUIDELINES: Dict[str, Dict[str, Any]] = {
    "fever": {
        "name_ko": "발열",
        "name_en": "Fever",
        "glucose_impact": "상승 가능성 높음 (스트레스 호르몬 분비 증가)",
        "risk_multiplier": 1.3,  # 혈당 변동 위험 증가 계수
        "advice": [
            "혈당 모니터링 빈도 증가 (2-4시간 간격)",
            "수분 섭취 증가 (시간당 100ml 이상)",
            "해열제 복용 가능 (파라세타몰/이부프로펜, 당분 미포함 제품)"
        ],
        "warning_signs": [
            "38.5°C 이상 24시간 지속",
            "오한 동반",
            "해열제에 반응 없음"
        ],
        "source": "ISPAD 2024 - Treat fever as in children without diabetes"
    },
    "vomiting": {
        "name_ko": "구토",
        "name_en": "Vomiting",
        "glucose_impact": "불안정 (탈수 + 음식 흡수 저하)",
        "risk_multiplier": 2.0,  # 높은 위험
        "advice": [
            "탈수 방지: 15분마다 한 모금씩 물 섭취",
            "전해질 음료 권장 (이온음료 희석)",
            "케톤 측정 필수",
            "인슐린은 중단하지 않되, 용량 조절 필요할 수 있음"
        ],
        "warning_signs": [
            "2시간 이상 지속",
            "수분 섭취 불가",
            "혈액 섞임"
        ],
        "emergency_threshold": "2시간 이상 구토 지속 시 응급실 방문",
        "source": "ISPAD 2024 - Vomiting >2 hours requires medical attention"
    },
    "diarrhea": {
        "name_ko": "설사",
        "name_en": "Diarrhea",
        "glucose_impact": "저혈당 위험 증가 (흡수 장애)",
        "risk_multiplier": 1.5,
        "advice": [
            "탈수 방지가 최우선",
            "전해질 보충 필요 (ORS 또는 희석 이온음료)",
            "혈당이 낮아지면 당분 포함 음료 섭취",
            "BRAT 식이 권장 (바나나, 쌀, 사과소스, 토스트)"
        ],
        "warning_signs": [
            "24시간 이상 지속",
            "혈변 또는 점액 섞임",
            "심한 복통 동반"
        ],
        "source": "ADA Sick Day Rules - Fluid replacement priority"
    },
    "nausea": {
        "name_ko": "메스꺼움",
        "name_en": "Nausea",
        "glucose_impact": "식사량 감소로 저혈당 가능",
        "risk_multiplier": 1.3,
        "advice": [
            "적은 양 자주 섭취",
            "무탄산, 무카페인 음료 권장",
            "혈당 180 mg/dL 이하면 당분 포함 음료 가능",
            "쿠키, 크래커 등 담백한 음식 시도"
        ],
        "warning_signs": [
            "24시간 이상 지속",
            "구토로 진행"
        ],
        "source": "ISPAD 2024 - If appetite decreased, consider sugary fluids"
    },
    "cold_flu": {
        "name_ko": "감기/독감",
        "name_en": "Cold/Flu",
        "glucose_impact": "상승 가능성 (면역 반응)",
        "risk_multiplier": 1.2,
        "advice": [
            "충분한 휴식",
            "수분 섭취 증가",
            "무설탕 기침약 선택",
            "증상 완화제 복용 가능 (당분 미포함 확인)"
        ],
        "warning_signs": [
            "호흡 곤란",
            "고열 동반 (38.5°C 이상)",
            "증상 악화"
        ],
        "source": "ADA - Treat underlying illness appropriately"
    },
    "infection": {
        "name_ko": "감염",
        "name_en": "Infection",
        "glucose_impact": "상승 가능성 높음",
        "risk_multiplier": 1.5,
        "advice": [
            "의료진 진찰 필요",
            "처방된 항생제 복용 (필요시)",
            "혈당 모니터링 강화",
            "인슐린 용량 증가 필요할 수 있음"
        ],
        "warning_signs": [
            "발열 지속",
            "국소 증상 악화",
            "전신 쇠약감"
        ],
        "source": "ISPAD 2024 - Treat bacterial infections with antibiotics"
    }
}


# =============================================================================
# EMERGENCY CRITERIA
# When to seek immediate medical attention
# Based on ISPAD and ADA Guidelines
# =============================================================================

EMERGENCY_CRITERIA: Dict[str, Dict[str, Any]] = {
    "dka_symptoms": {
        "name_ko": "당뇨병성 케톤산증 (DKA) 증상",
        "indicators": [
            "혈당 >300 mg/dL (16.7 mmol/L) 지속",
            "혈중 케톤 >3.0 mmol/L",
            "과일 냄새 나는 호흡 (아세톤 냄새)",
            "빠르고 깊은 호흡 (쿠스마울 호흡)",
            "심한 복통",
            "의식 혼란 또는 졸림",
            "심한 구토 (2시간 이상)"
        ],
        "action": "즉시 119 호출 또는 응급실 방문",
        "source": "ISPAD 2024 - DKA Recognition"
    },
    "severe_hypoglycemia": {
        "name_ko": "심각한 저혈당",
        "indicators": [
            "의식 저하 또는 혼란",
            "경련",
            "스스로 당분 섭취 불가"
        ],
        "action": "글루카곤 투여, 119 호출",
        "source": "ADA - Severe Hypoglycemia Management"
    },
    "dehydration": {
        "name_ko": "심한 탈수",
        "indicators": [
            "4시간 이상 수분 섭취 불가",
            "소변량 현저히 감소",
            "눈 함몰, 피부 탄력 저하",
            "빠른 심박수",
            "어지러움 또는 기립성 저혈압"
        ],
        "action": "응급실 방문 (IV 수액 필요)",
        "source": "ISPAD 2024 - Signs of Dehydration"
    }
}


# =============================================================================
# SICK DAY ESSENTIAL RULES
# Core principles that always apply
# =============================================================================

SICK_DAY_ESSENTIAL_RULES = [
    {
        "rule": "인슐린 절대 중단 금지",
        "explanation": "아프면 혈당이 올라가는 경우가 많아 오히려 인슐린이 더 필요합니다. 식사를 못 해도 기저 인슐린은 유지해야 DKA를 예방합니다.",
        "source": "ISPAD 2024 - Never stop insulin"
    },
    {
        "rule": "혈당 자주 측정 (2-4시간 간격)",
        "explanation": "아픈 날에는 혈당 변동이 심합니다. 평소보다 자주 측정해야 위험을 조기에 발견할 수 있습니다.",
        "source": "ADA - Monitor blood glucose every 2-4 hours"
    },
    {
        "rule": "수분 섭취 증가",
        "explanation": "탈수는 혈당 상승과 케톤 증가의 위험을 높입니다. 시간당 100ml 이상 마시세요.",
        "source": "ISPAD 2024 - 100ml/hour fluid intake"
    },
    {
        "rule": "케톤 모니터링",
        "explanation": "특히 혈당이 240 mg/dL 이상이거나 구토가 있을 때 케톤을 측정하세요. 조기 발견이 DKA를 예방합니다.",
        "source": "ADA - Check ketones if glucose >240 mg/dL"
    },
    {
        "rule": "의료팀 연락 기준 숙지",
        "explanation": "구토 2시간 이상, 케톤 양성, 혈당 조절 불가, 증상 악화 시 즉시 의료팀에 연락하세요.",
        "source": "ISPAD 2024 - When to contact diabetes team"
    }
]


# =============================================================================
# HYDRATION GUIDELINES
# Fluid intake recommendations during illness
# =============================================================================

HYDRATION_GUIDELINES = {
    "general": {
        "target": "시간당 100ml 이상 (5-10분마다 소량씩)",
        "source": "ISPAD 2024"
    },
    "glucose_high": {
        "threshold_mg_dl": 250,
        "recommendation": "무설탕/무탄수화물 음료 (물, 무설탕 차, 무설탕 이온음료)",
        "source": "ADA Sick Day Rules"
    },
    "glucose_low_normal": {
        "threshold_mg_dl": 180,
        "recommendation": "당분 포함 음료 가능 (희석 주스, 이온음료, 스포츠드링크)",
        "source": "ISPAD 2024 - Prevent starvation ketosis"
    },
    "examples_sugar_free": [
        "물",
        "무설탕 차",
        "무설탕 이온음료",
        "국물 (저나트륨)"
    ],
    "examples_with_sugar": [
        "희석 과일주스 (50%)",
        "이온음료",
        "스포츠드링크"
    ]
}
