# 🚀 배포 가이드라인 (Deployment Guide)

본 문서는 **T1D Manager MCP 서버**를 클라우드 환경(Fly.io)에 배포하여 **공용(Public) MCP 서버**로 운영하기 위한 절차를 설명합니다.

---

## 1. 배포 전 체크리스트

1.  **Fly.io 계정 및 CLI**: `flyctl`이 설치되어 있어야 합니다.
2.  **API 키 준비**:
    *   `MCP_AUTH_TOKEN`: 서버 보호용 비밀 토큰 (임의 생성)
    *   `NAVER_CLIENT_ID` / `SECRET`: 네이버 검색 API
    *   `KAKAO_API_KEY`: 카카오 검색 API

---

## 2. Fly.io 배포 (권장)

이 프로젝트는 `fly.toml`과 `Dockerfile`이 이미 최적화되어 있습니다.
터미널에서 아래 명령어를 순서대로 실행하세요.

### 1단계: 앱 런칭 (최초 1회)
```bash
fly launch --no-deploy
```
*   질문이 나오면 **App Name**만 지정하고 나머지는 기본값(또는 No)으로 진행하세요.
*   **Region**은 한국과 가까운 `nrt` (Tokyo)를 권장합니다.

### 2단계: 환경 변수(Secrets) 설정
개인정보(Dexcom 비번)는 절대 서버에 저장하지 않습니다. 공통 API 키만 설정하세요.

```bash
fly secrets set \
  MCP_AUTH_TOKEN="your-secure-token-1234" \
  NAVER_CLIENT_ID="your-id" \
  NAVER_CLIENT_SECRET="your-secret" \
  KAKAO_API_KEY="your-kakao-key"
```

### 3단계: 배포 실행
```bash
fly deploy
```

### 4단계: 무료 범위 유지 설정 (중요)
Fly.io의 과금 방지를 위해 머신 개수를 1개로 고정합니다. (이 설정은 `fly.toml`의 `auto_stop_machines = false`와 함께 작동하여 서버가 항상 깨어있게 합니다.)

```bash
fly scale count 1
```

---

## 3. PlayMCP / Claude Desktop 등록

배포가 완료되면 `https://<APP-NAME>.fly.dev/sse` 주소가 생성됩니다.

### Claude Desktop 설정 예시 (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "t1d-manager": {
      "url": "https://your-app-name.fly.dev/sse",
      "transport": "sse",
      "env": {
        "MCP_AUTH_TOKEN": "your-secure-token-1234"
      }
    }
  }
}
```

---

## 4. 로컬 테스트 (VS Code)

VS Code를 사용 중이라면 `.vscode/tasks.json`에 정의된 태스크를 활용하세요.

*   `Cmd + Shift + P` -> `Run Task` 선택
*   **🚀 Run Local (SSE)**: 로컬 서버 실행
*   **☁️ Deploy to Fly.io**: 배포 명령 실행
