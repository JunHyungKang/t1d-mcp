# 🩸 T1D Manager (1형 당뇨 관리 MCP)

**카카오 MCP Develop Competition (MCP Player 10) 출품작**

1형 당뇨 환자와 보호자를 위한 **AI 에이전트 서버**입니다.
어머니가 **"내 덱스콤 아이디는 이거야"**라고 말만 하면, 복잡한 설정 없이도 실시간 혈당 관리와 아픈 날(Sick Day) 케어를 받을 수 있습니다.

---

## ✨ 핵심 기능

### 1. 덱스콤 다이렉트 연동 (`Dexcom Share`)
- **기능**: 별도의 서버(Nightscout) 구축 없이, **Dexcom 계정 아이디/비번**만 있으면 즉시 실시간 혈당을 가져옵니다.
- **보안**: 계정 정보는 서버에 저장되지 않고, 조회 시점에만 사용된 후 즉시 파기됩니다 (Stateless).
- **예시**: "내 아이디는 mom@example.com, 비번은 1234야. 혈당 어때?"

### 2. 아픈 날 (Sick Day) 케어
- **기능**: "나 감기 기운 있어"라고 말하면, 즉시 위기 관리 모드로 전환됩니다.
- **케어 내용**: 수분 섭취 알림, 기저 인슐린 유지 강조, 케톤 측정 권고 등 임상 가이드라인 기반 조언 제공.

### 3. 공감형 AI (`Empathy Persona`)
- **기능**: 딱딱한 기계음 대신, **"어머니, 수치가 안정적이네요. 편안하게 쉬세요."** 처럼 따뜻한 위로와 격려를 건넸습니다.

### 4. 스마트 인슐린 계산 & 시각화
- **기능**: 현재 혈당과 탄수화물 양을 입력하면 인슐린 용량을 계산하고, 이해하기 쉬운 도표로 보여줍니다.

### 5. 하이브리드 커뮤니티 검색
- **기능**: 네이버 블로그(환자 경험담)와 카카오 웹(정보)을 동시에 검색하여 실질적인 꿀팁을 제공합니다.

---

## 🛠️ 기술 스택
- **Core**: Python 3.12, `mcp`, `FastMCP`
- **Dexcom**: `pydexcom` (Direct Share API)
- **Web**: `Starlette` (SSE Server), `Uvicorn`
- **Infra**: Docker, Fly.io (Always-on configured)

---

## 🚀 배포 및 설정 가이드

이 서버는 **공용(Public)**으로 설계되었으므로, **개인 의료 정보나 비밀번호를 서버에 저장하지 않습니다.**
서버 관리자(개발자)는 오직 **검색 API 키**와 **서버 보호 토큰**만 설정하면 됩니다.

### 1. 환경 변수 (Secrets) 설정
`.env` 파일이나 클라우드 Secrets(Fly.io)에 다음 값들만 설정하세요.

```bash
# [필수] 서버 보호용 토큰 (아무 문자열이나 설정)
MCP_AUTH_TOKEN="my-secret-token"

# [필수] 검색 기능을 위해 필요
NAVER_CLIENT_ID="your-naver-id"
NAVER_CLIENT_SECRET="your-naver-secret"
KAKAO_API_KEY="your-kakao-key"

# (삭제됨) NIGHTSCOUT_URL, DEXCOM_PASSWORD 등은 설정하지 않습니다!
# 사용자에게 대화 중에 직접 물어봅니다.
```

### 2. Fly.io 배포 (무료 범위 유지)
```bash
# 1. 앱 생성
fly launch --no-deploy

# 2. 필수 키 설정 (개인정보 X)
fly secrets set MCP_AUTH_TOKEN="changeme" NAVER_CLIENT_ID="..." ...

# 3. 배포
fly deploy

# 4. 머신 1개 고정 (비용 방지, Sleep 방지 설정은 fly.toml에 됨)
fly scale count 1
```

### 3. PlayMCP 등록
배포 후 생성된 URL(예: `https://t1d-mcp.fly.dev/sse`)을 등록하세요.
사용자가 접속하면, **"Dexcom 아이디와 비밀번호를 입력해주세요"**라는 안내와 함께 서비스가 시작됩니다.

---

## ⚠️ 면책 조항 (Medical Disclaimer)
> 본 서비스는 의료 기기가 아니며, 제공되는 정보는 참고용입니다.
> 투약 및 처치 결정은 반드시 전문의의 상담과 자가혈당측정 결과에 따라야 합니다.
