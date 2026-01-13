"""
Dexcom Developer API Tools (OAuth-based)

These tools require OAuth authentication and are conditionally loaded
when ENABLE_DEXCOM=true environment variable is set.
"""

import httpx
from src.cgm.dexcom_official import DexcomOfficialClient, format_egvs_for_display


def register_dexcom_tools(mcp):
    """Register Dexcom OAuth tools to the MCP server."""
    
    @mcp.tool()
    def get_dexcom_auth_url(client_id: str, client_secret: str, redirect_uri: str = "http://localhost:8080/callback") -> str:
        """
        Generate Dexcom OAuth authorization URL for Sandbox environment.
        
        Use this to get the URL where users can authorize your app.
        In Sandbox mode, no password is required - users select from a dropdown.
        
        Args:
            client_id: OAuth client ID from Dexcom Developer Portal
            client_secret: OAuth client secret (stored for later token exchange)
            redirect_uri: Callback URL registered with your Dexcom app
            
        Returns:
            Authorization URL to redirect the user to
        """
        client = DexcomOfficialClient(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            sandbox=True
        )
        
        auth_url = client.get_authorization_url(state="mcp_sandbox_test")
        
        return f"""
### 🔐 Dexcom OAuth 인증 URL (Sandbox)

**아래 URL로 이동하여 인증하세요:**

[인증 페이지 열기]({auth_url})

> [!NOTE]
> Sandbox 환경에서는 비밀번호 입력 없이 드롭다운에서 테스트 사용자를 선택합니다.
> 사용 가능한 테스트 사용자: SandboxUser1 ~ SandboxUser7 (SandboxUser7은 G7 데이터)

인증 완료 후 redirect_uri로 돌아오는 URL에서 `code` 파라미터를 확인하세요.
그 코드를 `get_cgm_sandbox` 도구에 전달하면 혈당 데이터를 조회할 수 있습니다.
"""


    @mcp.tool()
    async def get_cgm_sandbox(
        client_id: str,
        client_secret: str,
        authorization_code: str,
        redirect_uri: str = "http://localhost:8080/callback"
    ) -> str:
        """
        Get CGM data from Dexcom Developer API Sandbox using authorization code.
        
        This tool uses the official Dexcom API (not Share API) and works with
        the Sandbox environment, which provides simulated CGM data for testing.
        
        Args:
            client_id: OAuth client ID from Dexcom Developer Portal
            client_secret: OAuth client secret from Dexcom Developer Portal
            authorization_code: Code received from OAuth callback after user authorization
            redirect_uri: Same redirect_uri used in get_dexcom_auth_url
            
        Returns:
            Formatted CGM data from the last 24 hours
        """
        try:
            client = DexcomOfficialClient(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                sandbox=True
            )
            
            # Exchange authorization code for access token
            token_response = await client.exchange_code_for_token(authorization_code)
            access_token = token_response.get("access_token")
            
            if not access_token:
                return "❌ 토큰 교환 실패: access_token을 받지 못했습니다."
            
            # Get EGV data
            egvs_data = await client.get_egvs(access_token)
            
            # Format for display
            result = format_egvs_for_display(egvs_data, limit=10)
            result += "\n\n> ✅ Dexcom Developer API Sandbox에서 데이터를 성공적으로 조회했습니다."
            
            return result
            
        except httpx.HTTPStatusError as e:
            return f"❌ API 오류: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            return f"❌ 오류 발생: {str(e)}"


    @mcp.tool()
    async def get_cgm_with_token(
        access_token: str,
        hours: int = 24,
        sandbox: bool = True
    ) -> str:
        """
        Get CGM data using an existing access token.
        
        Use this if you already have a valid access token from a previous OAuth flow.
        
        Args:
            access_token: Valid OAuth access token
            hours: Number of hours of data to retrieve (default: 24, max: 720 for 30 days)
            sandbox: Whether to use sandbox environment (default: True)
            
        Returns:
            Formatted CGM data
        """
        from datetime import datetime, timedelta
        
        try:
            # Create a minimal client just for API calls
            base_url = (
                "https://sandbox-api.dexcom.com" if sandbox 
                else "https://api.dexcom.com"
            )
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(hours=min(hours, 720))  # Max 30 days
            
            async with httpx.AsyncClient() as http_client:
                response = await http_client.get(
                    f"{base_url}/v3/users/self/egvs",
                    params={
                        "startDate": start_date.strftime("%Y-%m-%dT%H:%M:%S"),
                        "endDate": end_date.strftime("%Y-%m-%dT%H:%M:%S"),
                    },
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                response.raise_for_status()
                egvs_data = response.json()
            
            result = format_egvs_for_display(egvs_data, limit=10)
            env_label = "Sandbox" if sandbox else "Production"
            result += f"\n\n> ✅ Dexcom Developer API ({env_label})에서 조회 완료"
            
            return result
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "❌ 인증 실패: 토큰이 만료되었거나 유효하지 않습니다. 다시 인증해주세요."
            return f"❌ API 오류: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            return f"❌ 오류 발생: {str(e)}"
