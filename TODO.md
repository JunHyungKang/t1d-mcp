# 📋 T1D Manager 개선 TODO

프로젝트 분석 결과, 코드 안정성과 사용자 경험을 위해 개선이 필요한 사항들을 정리했습니다.

## 🛠️ 긴급 수정 (Critical)
- [x] **SSE 서버 안정화**: `src/sse.py` 내 `messages_endpoint` 함수가 정의되지 않아 POST 요청 시 오류 발생 예상.
- [x] **변수명 정합성**: `src/sse.py`에서 `handle_messages`로 정의된 함수가 `routes`에서는 `messages_endpoint`로 참조되고 있음.
- [x] **FastMCP 세션 관리**: `sse_endpoint`에서 `mcp._server.run` 호출 시 `streams` 전달 방식 확인 및 최적화.

## ✨ 기능 개선 (Features)
- [x] **혈당 변화량(Delta) 계산 구현**: `src/cgm/dexcom.py`의 `get_readings`에서 `TODO`로 남겨진 delta 계산 로직 추가.
- [x] **Nightscout 연동 활성화**: `src/main.py`에서 `NightscoutClient`는 import 되어 있으나 실제 Tool로 노출되지 않음.
- [x] **영양 정보 데이터 확충**: 현재 `FoodDatabase`가 하드코딩된 소량의 데이터만 가지고 있다면, 외부 API 또는 더 큰 CSV 연동 고려.
- [x] **공감형 페르소나 강화**: `get_glucose_status_with_empathy`에서 단순히 문자열 매핑이 아닌, LLM의 context를 더 잘 활용할 수 있도록 가이드라인(Instructions) 정교화.

## 🚀 PlayMCP 기반 고도화 (Advanced)
- [x] **도구 설계 최적화 (Token Efficiency)**: 모든 MCP Tool의 name, description, parameter description을 영어로 작성하여 LLM 토큰 소비 최적화 및 정확도 향상.
- [ ] **표준 HTTP POST 지원**: 분산 환경 및 Serverless 배포를 고려하여 SSE뿐만 아니라 Stateless HTTP POST 기반의 MCP 호출이 원활하도록 엔드포인트 보강.
- [ ] **OAuth 2.0 인증 도입**: Dexcom이나 Kakao 연동 시 보안성을 높이기 위해 OAuth 2.0 (PKCE 포함) 인증 플로우 지원.
- [x] **MCP Resource API 활용**: 실시간 혈당 데이터(`cgm://current`), 인슐린 기록(`treatment/history`) 등을 전용 **Resource**로 정의하여 AI가 능동적으로 참조하게 함.
- [x] **MCP Prompt API 도입**: '아픈 날 가이드', '식단 분석' 등 자주 쓰이는 복합 프롬프트를 **Prompt 템플릿**으로 제공하여 일관된 AI 페르소나 유지.

## 🏗️ 코드 품질 & 인프라 (Code Quality)
- [x] **로깅 시스템 도입**: `print` 문 대신 Python `logging` 모듈을 사용하여 레벨별 로그 관리.
- [ ] **에러 핸들링 강화**: API 호출 실패(Naver, Kakao, Dexcom) 시 사용자에게 더 친절하고 구체적인 피드백 제공.
- [x] **환경 변수 유효성 검사**: 필수 API 키가 설정되어 있는지 체크하는 로직 추가. 서버 시작 시 필수 환경 변수(`NAVER_CLIENT_ID` 등)가 누락되었는지 확인하는 로직 추가.
- [ ] **TDD 강화**: Edge case(네트워크 오류, 잘못된 계정 정보 등)에 대한 테스트 케이스 보강.

## 📖 문서화 (Documentation)
- [x] **MCP 가이드라인 추가**: MCP 서버 생성 가이드 및 심사 정책 문서([GUIDELINE.md](./GUIDELINE.md)) 추가.
- [ ] **API Reference 추가**: 各 MCP Tool의 입출력 예시를 README에 보강.
- [ ] **Architecture 설명**: `src/` 내부 모듈 간의 데이터 흐름을 Mermaid 다이어그램으로 README에 추가.
