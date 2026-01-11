# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

T1D Manager is an MCP (Model Context Protocol) server for Type 1 diabetes management. It provides AI-powered tools for CGM data retrieval (Dexcom), sick day care guidelines, insulin calculation, and community search.

## Development Commands

```bash
# Install dependencies
uv sync

# Run server (Streamable HTTP on port 8080)
uv run uvicorn src.server:app --host 0.0.0.0 --port 8080

# Test with MCP Inspector
npx @modelcontextprotocol/inspector --transport http --server-url http://127.0.0.1:8080/mcp

# Run tests
uv run pytest

# Run single test file
uv run pytest tests/test_cgm.py

# Run specific test
uv run pytest tests/test_cgm.py::test_function_name -v
```

## Architecture

```
src/
├── server.py          # Streamable HTTP server (Starlette + FastMCP)
├── main.py            # MCP tool definitions using FastMCP
├── cgm/
│   ├── dexcom.py          # Dexcom Share API (legacy ID/PW)
│   ├── dexcom_official.py # Dexcom Developer API (OAuth 2.0)
│   └── nightscout.py      # Nightscout integration
├── treatment/
│   ├── calculator.py      # Bolus insulin calculation
│   ├── sick_day/          # ISPAD/ADA guideline-based sick day analysis
│   │   ├── risk_analyzer.py
│   │   └── knowledge_base.py
│   └── visualizer.py
├── community/
│   └── search.py          # Hybrid search (Naver Blog + Kakao Web)
└── nutrition/
    └── database.py        # Food carbohydrate database
```

**Key data flow**: `server.py` (HTTP transport) → `main.py` (FastMCP tools) → domain modules (cgm/, treatment/, community/)

## MCP Tools Exposed

- `fetch_dexcom_glucose_state` - CGM data via Dexcom Share API
- `get_dexcom_auth_url` / `get_cgm_sandbox` / `get_cgm_with_token` - OAuth 2.0 flow
- `calculate_insulin_dosage` - Bolus calculation (correction + meal)
- `analyze_sick_day_guidelines` - ISPAD/ADA clinical guidelines
- `get_sick_day_quick_check` - Quick glucose risk assessment
- `search_diabetes_community` - Naver/Kakao hybrid search
- `search_nutrition_info` - Food carbohydrate lookup

## Development Rules

- 한글로 대답해 (Answer in Korean)
- Implementation Plan도 한글로 만들 것
- TDD로 개발할 것 (Develop with TDD)

## Environment Variables

Required for production:
- `MCP_AUTH_TOKEN` - Bearer token for server authentication
- `NAVER_CLIENT_ID` / `NAVER_CLIENT_SECRET` - Naver Search API
- `KAKAO_API_KEY` - Kakao Search API

For Dexcom OAuth (optional):
- Dexcom Developer Portal client ID/secret

## Transport

Uses Streamable HTTP (MCP standard) via `FastMCP.streamable_http_app()`. Single endpoint at `/mcp`.
