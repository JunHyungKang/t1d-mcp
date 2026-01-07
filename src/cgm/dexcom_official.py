"""
Dexcom Developer API Client (Official)

This module provides a client for the official Dexcom Developer API,
which supports OAuth 2.0 authentication and includes a Sandbox environment
for testing without real user accounts.

Reference: https://developer.dexcom.com/docs
"""

import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import os


class DexcomOfficialClient:
    """
    Client for the official Dexcom Developer API.
    
    This is different from the pydexcom library which uses the Dexcom Share API.
    The Developer API:
    - Uses OAuth 2.0 authentication
    - Provides retrospective data (not real-time)
    - Has a Sandbox environment for testing
    """
    
    SANDBOX_BASE_URL = "https://sandbox-api.dexcom.com"
    PRODUCTION_BASE_URL = "https://api.dexcom.com"
    
    # Sandbox users available for testing
    SANDBOX_USERS = [
        "SandboxUser1",  # G6 data
        "SandboxUser2",
        "SandboxUser3", 
        "SandboxUser4",
        "SandboxUser5",
        "SandboxUser6",
        "SandboxUser7",  # G7 data
    ]
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str = "http://localhost:8080/callback",
        sandbox: bool = True
    ):
        """
        Initialize the Dexcom Developer API client.
        
        Args:
            client_id: OAuth client ID from Dexcom Developer Portal
            client_secret: OAuth client secret from Dexcom Developer Portal
            redirect_uri: OAuth redirect URI registered with your app
            sandbox: If True, use sandbox environment (default)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.sandbox = sandbox
        self.base_url = self.SANDBOX_BASE_URL if sandbox else self.PRODUCTION_BASE_URL
        
    def get_authorization_url(self, state: str = "state") -> str:
        """
        Generate the OAuth authorization URL.
        
        In Sandbox mode, the user won't need a password - 
        they select from a dropdown of test users.
        
        Args:
            state: CSRF protection state parameter
            
        Returns:
            Authorization URL to redirect the user to
        """
        return (
            f"{self.base_url}/v2/oauth2/login"
            f"?client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&response_type=code"
            f"&scope=offline_access"
            f"&state={state}"
        )
    
    async def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens.
        
        Args:
            authorization_code: Code received from OAuth callback
            
        Returns:
            Token response containing access_token, refresh_token, expires_in
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v2/oauth2/token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": authorization_code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            return response.json()
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an expired access token.
        
        Args:
            refresh_token: The refresh token from previous token exchange
            
        Returns:
            New token response
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v2/oauth2/token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_egvs(
        self,
        access_token: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get Estimated Glucose Values (EGVs) for the authenticated user.
        
        Args:
            access_token: Valid OAuth access token
            start_date: Start of date range (default: 24 hours ago)
            end_date: End of date range (default: now)
            
        Returns:
            EGV data including glucose values, trends, and timestamps
        """
        if end_date is None:
            end_date = datetime.utcnow()
        if start_date is None:
            start_date = end_date - timedelta(hours=24)
        
        # Format dates as ISO 8601
        start_str = start_date.strftime("%Y-%m-%dT%H:%M:%S")
        end_str = end_date.strftime("%Y-%m-%dT%H:%M:%S")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v3/users/self/egvs",
                params={
                    "startDate": start_str,
                    "endDate": end_str,
                },
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_data_range(self, access_token: str) -> Dict[str, Any]:
        """
        Get the available data range for the authenticated user.
        
        This endpoint doesn't require date parameters.
        
        Args:
            access_token: Valid OAuth access token
            
        Returns:
            Data range information
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v3/users/self/dataRange",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_events(
        self,
        access_token: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get events (insulin, carbs, exercise, etc.) for the authenticated user.
        
        Args:
            access_token: Valid OAuth access token
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            Event data
        """
        if end_date is None:
            end_date = datetime.utcnow()
        if start_date is None:
            start_date = end_date - timedelta(hours=24)
        
        start_str = start_date.strftime("%Y-%m-%dT%H:%M:%S")
        end_str = end_date.strftime("%Y-%m-%dT%H:%M:%S")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v3/users/self/events",
                params={
                    "startDate": start_str,
                    "endDate": end_str,
                },
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            return response.json()


def format_egvs_for_display(egvs_data: Dict[str, Any], limit: int = 5) -> str:
    """
    Format EGV data for user-friendly display.
    
    Args:
        egvs_data: Raw EGV response from API
        limit: Maximum number of readings to show
        
    Returns:
        Formatted markdown string
    """
    records = egvs_data.get("records", [])
    
    if not records:
        return "📊 데이터가 없습니다."
    
    output = "### 🩸 Dexcom CGM 데이터 (Developer API)\n\n"
    output += "| 시간 | 혈당 (mg/dL) | 추세 |\n"
    output += "|------|-------------|------|\n"
    
    # Trend mapping
    trend_map = {
        "doubleUp": "⬆️⬆️ 급상승",
        "singleUp": "⬆️ 상승",
        "fortyFiveUp": "↗️ 완만한 상승",
        "flat": "➡️ 안정",
        "fortyFiveDown": "↘️ 완만한 하강",
        "singleDown": "⬇️ 하강",
        "doubleDown": "⬇️⬇️ 급하강",
        "notComputable": "❓ 계산 불가",
        "rateOutOfRange": "⚠️ 범위 초과",
    }
    
    for record in records[:limit]:
        value = record.get("value", "N/A")
        trend = record.get("trend", "unknown")
        trend_display = trend_map.get(trend, trend)
        
        # Parse and format time
        system_time = record.get("systemTime", "")
        try:
            dt = datetime.fromisoformat(system_time.replace("Z", "+00:00"))
            time_str = dt.strftime("%H:%M")
        except:
            time_str = system_time[:16] if system_time else "N/A"
        
        output += f"| {time_str} | {value} | {trend_display} |\n"
    
    if len(records) > limit:
        output += f"\n_총 {len(records)}개의 기록 중 {limit}개만 표시_\n"
    
    return output
