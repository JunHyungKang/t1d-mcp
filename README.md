# 🩸 T1D Manager (1형 당뇨 관리 MCP)

**카카오 MCP Develop Competition (MCP Player 10) 출품작**

1형 당뇨 환자와 보호자를 위한 **AI 에이전트 서버**입니다.
어머니가 **"내 덱스콤 아이디는 이거야"**라고 말만 하면, 복잡한 설정 없이도 실시간 혈당 관리와 아픈 날(Sick Day) 케어를 받을 수 있습니다.

---

## ✨ 핵심 기능

### 1. 덱스콤 다이렉트 연동 (`Dexcom Share`)
- **기능**: 별도의 서버(Nightscout) 구축 없이, **Dexcom 계정 아이디/비번**만 있으면 즉시 실시간 혈당을 가져옵니다.
- **보안**: 계정 정보는 서버에 저장되지 않고, 조회 시점에만 휘발성으로 사용됩니다 (Stateless).
- **예시**: "내 아이디는 mom@example.com, 비번은 1234야. 혈당 어때?"

### 2. 아픈 날 (Sick Day) 케어
- **기능**: "나 감기 기운 있어"라고 말하면, 즉시 위기 관리 모드로 전환됩니다.
- **케어 내용**: 수분 섭취 알림, 기저 인슐린 유지 강조, 케톤 측정 권고 등 임상 가이드라인 기반 조언 제공.

### 3. 공감형 AI (`Empathy Persona`)
- **기능**: 딱딱한 기계음 대신, **"어머니, 수치가 안정적이네요. 편안하게 쉬세요."** 처럼 따뜻한 위로와 격려를 건넸습니다.

### 4. 스마트 인슐린 계산 & 시각화
- **기능**: 현재 혈당과 탄수화물 양을 입력하면 인슐린 용량을 계산하고, 이해하기 쉬운 Mermaid 도표로 보여줍니다.

### 5. 하이브리드 커뮤니티 검색
- **기능**: 네이버 블로그(환자 경험담)와 카카오 웹(정보)을 동시에 검색하여 실질적인 꿀팁을 제공합니다.

---

## 🛠️ 기술 스택 & 구조
- **Core**: Python 3.12, `mcp`, `FastMCP`
- **Dexcom**: `pydexcom` (Direct Share API)
- **Web**: `Starlette` (SSE Server), `Uvicorn`
- **Infra**: Docker, Fly.io (Always-on configured)

```
t1d-mcp/
├── src/
│   ├── cgm/             # 혈당 데이터 (Dexcom, Nightscout)
│   ├── treatment/       # 인슐린 계산 & 시각화
│   ├── community/       # 하이브리드 검색
│   ├── nutrition/       # 영양 정보 DB
│   ├── sse.py           # 웹 서버 엔트리포인트
│   └── main.py          # MCP 도구 정의
└── tests/               # 단위 테스트 (100% Coverage)
```

---

## 🚀 설치 및 실행

### 로컬 개발
```bash
uv sync
uv run uvicorn src.sse:app --host 0.0.0.0 --port 8080 --reload
```

### 서버 배포
상세한 배포 방법은 [DEPLOYMENT.md](./DEPLOYMENT.md) 문서를 참고하세요.

---

## ⚠️ 면책 조항 (Medical Disclaimer)
> 본 서비스는 의료 기기가 아니며, 제공되는 정보는 참고용입니다.
> 투약 및 처치 결정은 반드시 전문의의 상담과 자가혈당측정 결과에 따라야 합니다.
