from typing import Dict

def get_insulin_education() -> Dict[str, str]:
    """
    Returns educational content about insulin types with simple analogies for seniors.
    """
    markdown_table = """
| 구분 | 종류 (예시) | 역할 (비유) | 설명 |
|---|---|---|---|
| **기저 인슐린**<br>(배경) | 트레시바, 란투스 | 📱 **스마트폰 배경화면** | 24시간 은은하게 깔려 있어야 해요.<br>밥을 안 먹어도 몸 유지를 위해 필요합니다. |
| **식사 인슐린**<br>(급속) | 노보래피드, 휴마로그 | ⚡ **급속 충전기** | 밥(탄수화물) 먹어서 혈당 오를 때,<br>또는 혈당이 너무 높을 때 '팍!' 깎아줍니다. |
"""
    
    # Accessible explanation for "Why calculate?"
    simple_logic = """
> **💡 왜 따로 계산하나요?**
> * **기저(지속형)**는 건물의 **기초**입니다. 흔들리면 안 돼요.
> * **초속(식사)**은 그때그때 날씨(**음식/혈당**)에 맞춰 대응하는 **창문**입니다.
    """

    mermaid_diagram = """
graph LR
    A[밥/탄수화물 🍚] -->|혈당 급상승 🚀| B(내 몸의 혈당)
    C[식사 인슐린 ⚡] -->|빠르게 깎기 📉| B
    D[기저 인슐린 📱] -->|24시간 잔잔하게 받치기 〰️| B
    style C fill:#ff9999,stroke:#333,stroke-width:2px
    style D fill:#99ccff,stroke:#333,stroke-width:2px
    """
    
    return {
        "markdown_table": markdown_table.strip(),
        "simple_logic": simple_logic.strip(),
        "mermaid_diagram": mermaid_diagram.strip()
    }
