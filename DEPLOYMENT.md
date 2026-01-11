# 🚀 배포 가이드라인 (Deployment Guide)

본 문서는 **T1D Manager MCP 서버**를 클라우드 환경(Fly.io)에 배포하여 **공용(Public) MCP 서버**로 운영하기 위한 절차를 설명합니다.

---

## 🤔 왜 Fly.io인가? (vs Vercel)

| 항목 | Fly.io ✅ | Vercel ❌ |
|------|----------|----------|
| **장시간 연결** | WebSocket, SSE 무제한 지원 | Serverless 특성상 30초 타임아웃 |
| **MCP 호환성** | Streamable HTTP 완벽 지원 | 연결 끊김 문제 발생 |
| **상시 실행** | 머신이 항상 켜져 있음 | Cold Start 지연 발생 |
| **Docker 지원** | 네이티브 Docker 배포 | 제한적 |
| **비용** | ~$2/월 (무료 범위 내) | 무료지만 MCP 부적합 |

> **결론**: MCP 서버는 **지속적인 연결**이 필요하므로 Serverless(Vercel, Netlify)보다 **컨테이너 기반 플랫폼(Fly.io, Railway, Render)**이 적합합니다.

---

## 1. 배포 전 체크리스트

1.  **Fly.io 계정 및 CLI**: `flyctl`이 설치되어 있어야 합니다.
2.  **API 키 준비**:
    *   `MCP_AUTH_TOKEN`: 서버 보호용 비밀 토큰 (임의 생성)
    *   `NAVER_CLIENT_ID` / `SECRET`: 네이버 검색 API
    *   `KAKAO_API_KEY`: 카카오 검색 API

---

## 2. Fly.io 배포

이 프로젝트는 `fly.toml`과 `Dockerfile`이 이미 최적화되어 있습니다.

### 1단계: Fly CLI 설치 및 로그인
```bash
# 설치
curl -L https://fly.io/install.sh | sh

# 로그인
~/.fly/bin/flyctl auth login
```

### 2단계: 앱 런칭 (최초 1회)
```bash
fly launch --name t1d-mcp --region nrt --yes
```
*   **Region**: 한국과 가까운 `nrt` (Tokyo) 권장

### 3단계: 환경 변수(Secrets) 설정
```bash
fly secrets set \
  MCP_AUTH_TOKEN="your-secure-token-1234" \
  NAVER_CLIENT_ID="your-id" \
  NAVER_CLIENT_SECRET="your-secret" \
  KAKAO_API_KEY="your-kakao-key"
```

### 4단계: 배포 실행
```bash
fly deploy
```

### 5단계: 무료 범위 유지 (중요!)
Fly.io 무료 한도: **월 $5 미만은 청구 면제**

```bash
# 머신 1개로 고정 (비용 최소화)
fly scale count 1
```

| 리소스 | 설정 | 예상 비용 |
|--------|------|----------|
| VM | shared-cpu-1x, 256MB | ~$1.94/월 |
| Storage | 없음 | $0 |
| **합계** | | **~$2/월 (면제!)** |

---

## 3. 배포 결과

| 항목 | 값 |
|------|-----|
| **MCP Endpoint** | `https://t1d-mcp.fly.dev/mcp` |
| **Health Check** | `https://t1d-mcp.fly.dev/health` |
| **대시보드** | [fly.io/apps/t1d-mcp](https://fly.io/apps/t1d-mcp) |

---

## 4. PlayMCP / Claude Desktop 등록

### Claude Desktop 설정 (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "t1d-manager": {
      "url": "https://t1d-mcp.fly.dev/mcp",
      "transport": "http"
    }
  }
}
```

---

## 5. 로컬 테스트

### 서버 실행
```bash
uv run uvicorn src.server:app --host 0.0.0.0 --port 8080
```

### MCP Inspector 테스트
```bash
npx @modelcontextprotocol/inspector --transport http --server-url http://127.0.0.1:8080/mcp
```

### VS Code Task
`Cmd + Shift + P` → `Run Task` → **🚀 Run Local** 또는 **☁️ Deploy to Fly.io**
