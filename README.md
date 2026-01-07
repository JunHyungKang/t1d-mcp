# 🩸 T1D Manager (1형 당뇨 관리 MCP)

**카카오 MCP Develop Competition (MCP Player 10) 출품작**

1형 당뇨 환자와 보호자를 위한 **AI 에이전트 서버**입니다.
어머니가 **"내 덱스콤 아이디는 이거야"**라고 말만 하면, 복잡한 설정 없이도 실시간 혈당 관리와 아픈 날(Sick Day) 케어를 받을 수 있습니다.

---

## ✨ 핵심 기능

### 1. 📊 Dexcom CGM 실시간 연동 (OAuth 2.0 권장)
- **핵심**: "엄마, 나 지금 혈당 45인데 주스 마셔?" → "네! 저혈당이네요. 포도당 15g 섭취하세요."
- **기능**: Dexcom Share API 및 **공식 Developer API (OAuth 2.0)** 지원.
- **예시**: "내 아이디는 mom@example.com, 비번은 1234야. 혈당 어때?" (Legacy) / "Dexcom 로그인 할래" (OAuth)

### 2. 🏥 아픈 날 (Sick Day) 케어 (임상 가이드라인 준수)
- **기능**: "나 열 나고 토했어" → ISPAD/ADA 가이드라인 기반 위험도 분석 및 행동 지침(JSON) 제공.
- **데이터**: 인슐린 용량이 아닌, **수분 섭취, 케톤 측정, 응급실 방문 기준** 등 안전한 의료 지침을 안내합니다.



### 3. 🍽️ 스마트 인슐린 계산 & 시각화
- **기능**: 현재 혈당과 탄수화물 양을 입력하면 인슐린 용량을 계산하고, 이해하기 쉬운 Mermaid 도표로 보여줍니다.

### 4. 🔍 하이브리드 커뮤니티 검색
- **기능**: 네이버 블로그(환자 경험담)와 카카오 웹(정보)을 동시에 검색하여 실질적인 꿀팁을 제공합니다.

---

## 🛠️ 기술 스택 & 구조
- **Core**: Python 3.12, `mcp` (Model Context Protocol), `FastMCP`
- **Transport**: **Streamable HTTP** (MCP 표준 준수, SSE over HTTP)
- **Integrations**: Dexcom Share API, Dexcom Developer API (OAuth), Naver/Kakao Search
- **Infra**: Docker, Fly.io (Ready)

```
t1d-mcp/
├── src/
│   ├── server.py        # Streamable HTTP Server Entrypoint
│   ├── main.py          # FastMCP Tool Definitions
│   ├── cgm/             # Dexcom (Legacy & OAuth), Nightscout
│   ├── treatment/       # Sick Day Logic, Insulin Calc
│   ├── community/       # Hybrid Search
│   └── nutrition/       # Food DB
└── tests/               # 단위 테스트 (100% Coverage)
```

## ✅ 검증 및 테스트 결과

## 🚀 시작하기

### 1. 로컬 실행
```bash
# 의존성 설치 (uv 사용 권장)
uv sync

# 서버 실행 (Streamable HTTP on port 8080)
uv run uvicorn src.server:app --host 0.0.0.0 --port 8080
```

### 2. MCP Inspector로 테스트
```bash
npx @modelcontextprotocol/inspector --transport http --server-url http://127.0.0.1:8080/mcp
```

---

## ✅ 검증 및 테스트 결과

### 1. 전송 방식 (Transport)
- **방식**: Streamable HTTP (MCP 가이드라인 준수)
- **구현**: `FastMCP.streamable_http_app()` 사용

### 2. 주요 도구 테스트 (`pytest`)
- `fetch_dexcom_glucose_state`: Dexcom 실시간 혈당 및 추세(Trend) JSON 반환 검증 완료
- `analyze_sick_day_guidelines`: Sick Day 가이드라인 분석 및 JSON 출력 검증 완료
- `calculate_insulin`: 탄수화물/혈당 기반 계산 로직 검증 완료
- **테스트 결과**: 총 16개 테스트 케이스 **ALL PASS** ✅

### 3. Dexcom 인증 (Security)
- **레거시**: Share ID/PW 방식 지원 (보안 경고 포함)
- **권장**: OAuth 2.0 Auth Code Flow 구현 완료 (`get_dexcom_auth_url`, `get_cgm_with_token`)

---

## 📅 To-Do / Roadmap

### 완료됨
- [x] SSE → Streamable HTTP 마이그레이션 (`src/server.py`)
- [x] `analyze_sick_day_guidelines` 도구 개선 (JSON 구조화, 의학적 근거 보강)
- [x] `fetch_dexcom_glucose_state` 도구 개선 (JSON 구조화, OAuth 권장)
- [x] MCP Inspector 연동 및 테스트

### 예정
- [ ] Fly.io 배포 설정 최신화
- [ ] 실제 Dexcom Developer Portal 앱 등록 및 Production 테스트

---

## ⚠️ 면책 조항 (Medical Disclaimer)
> 본 서비스는 의료 기기가 아니며, 제공되는 정보는 참고용입니다.
> 의학적 결정은 반드시 담당 의료진과 상의해야 합니다.
> 인슐린 용량 계산이나 Sick Day 관리는 환자의 개별 상황에 따라 달라질 수 있습니다.

### 배포 가이드
상세한 배포 방법 및 심사 가이드는 다음 문서를 참고하세요.
- [DEPLOYMENT.md](./DEPLOYMENT.md): Fly.io 배포 가이드
- [GUIDELINE.md](./GUIDELINE.md): MCP 서버 생성 가이드 및 심사 정책


