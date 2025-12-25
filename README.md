# 🩸 T1D Manager (1형 당뇨 관리 MCP)

**카카오 MCP Develop Competition (MCP Player 10) 출품작**

1형 당뇨 환자와 보호자를 위한 **AI 에이전트 서버**입니다.
실시간 혈당 모니터링부터 인슐린 계산, 영양 정보, 그리고 커뮤니티 지식 탐색까지—**"단 하나의 대화창"**에서 모든 관리가 가능하도록 돕습니다.

---

## ✨ 핵심 기능

### 1. 실시간 혈당 브리핑 (`Nightscout`)
- **기능**: Dexcom/Libre 등 CGM(연속혈당측정기) 데이터를 Nightscout 서버에서 실시간으로 가져옵니다.
- **예시**: "엄마 지금 혈당 어때?" → *"현재 145 mg/dL이며 완만하게 오르고 있습니다(↗). 최근 15분간 상승세입니다."*

### 2. 스마트 인슐린 계산기 + 교육 (`Calculator & Visualizer`)
- **기능**: 현재 혈당, 목표 혈당, 섭취할 탄수화물 양을 입력하면 **필요한 인슐린 용량(Bolus)**을 계산해줍니다.
- **특징**: 단순히 숫자만 던져주지 않고, **어르신도 이해하기 쉬운 비유(배경화면 vs 급속충전기)**와 **도식(Mermaid Diagram)**을 함께 보여주어 질병 이해도를 높입니다.
- **검증**: TDD(테스트 주도 개발)로 계산 로직의 정확성을 검증했습니다.

### 3. 안심 영양 성분 검색 (`Nutrition`)
- **기능**: "순대국밥 탄수화물 몇이야?" 같은 질문에 대해 내장 DB(또는 API)를 검색하여 당뇨 관리에 편향된 정확한 영양 정보를 제공합니다.

### 4. 하이브리드 커뮤니티 검색 (`Hybrid Search`)
- **기능**: **네이버 블로그(환자 경험담)**와 **카카오 웹 문서(정보)**를 동시에 검색하여 최적의 정보를 제공합니다.
- **활용**: "무가당 간식 추천해줘", "인슐린 펌프 부착 부위 꿀팁" 등 생활 밀착형 질문 해결.

### 5. 기록하기 (`Logging`)
- **기능**: 대화를 통해 식사와 인슐린 투여 내역을 Nightscout에 자동으로 기록합니다. (구현 예정/진행 중)

---

## 🛠️ 기술 스택 & 구조
- **Language**: Python 3.12+
- **Framework**: `mcp` (Model Context Protocol), `FastMCP`
- **Web Server**: `Starlette`, `Uvicorn` (SSE 지원)
- **Deployment**: Docker (Fly.io / Render 호환)
- **Dependency Manager**: `uv`

```
t1d-mcp/
├── src/
│   ├── main.py          # 로컬 실행용 (Stdio)
│   ├── sse.py           # 웹 서버용 (SSE 엔드포인트)
│   ├── nightscout.py    # Nightscout API 클라이언트
│   ├── nutrition.py     # 영양 정보 검색기
│   ├── search.py        # 네이버/카카오 하이브리드 검색기
│   └── utils/
│       └── calculator.py # 인슐린 계산 로직
└── tests/               # 단위 테스트 (TDD)
```

---

## 🚀 설치 및 실행 가이드

### 1. 로컬 실행 (개발용)
```bash
# 의존성 설치
uv sync

# 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 NIGHTSCOUT_URL 등을 입력하세요.

# 실행 (Claude Desktop 연결용)
uv run src/main.py
```

### 2. 서버 배포 (PlayMCP 제출용)
이 프로젝트는 **Remote MCP Server** 규격을 준수하며, `Dockerfile`이 포함되어 있습니다.

1. **Fly.io / Render** 등에 이 저장소를 연결합니다.
2. 환경 변수(Secrets)를 설정합니다. (`NIGHTSCOUT_URL`, `KAKAO_API_KEY` 등)
3. 배포된 URL의 `/sse` 엔드포인트를 PlayMCP에 등록합니다.
   - 예: `https://abcd-t1d-mcp.fly.dev/sse`

---

## ⚠️ 면책 조항 (Medical Disclaimer)
> **본 서비스는 의료 진단 및 치료를 위한 의료 기기가 아닙니다.**
> 제공되는 모든 정보와 계산 결과는 사용자의 판단을 돕기 위한 **참고 자료**일 뿐이며, 실제 투약 및 의료적 결정은 반드시 **전문의와의 상담** 또는 **환자/보호자의 최종 판단**에 따라야 합니다. 개발자는 본 서비스 사용으로 인해 발생하는 어떠한 결과에 대해서도 법적 책임을 지지 않습니다.
