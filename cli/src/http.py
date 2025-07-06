import traceback
import socket
from typing import Optional, Type, TypeVar, Union
from pydantic import BaseModel, ValidationError
import typer
import httpx

# ✅ Force IPv4 (patch for some Windows/ISP networks)
original_getaddrinfo = socket.getaddrinfo
def getaddrinfo_ipv4(*args, **kwargs):
    return [info for info in original_getaddrinfo(*args, **kwargs) if info[0] == socket.AF_INET]
socket.getaddrinfo = getaddrinfo_ipv4

from src.exceptions import (
    APIError,
    MismatchingExpectedStatusCodeError,
)
from src.log import render_error, render_success
from src.schemas import AccessToken, AgentSchema, RegisterResponse
from src.settings import get_settings
from src.credentials import CredentialsManager

settings = get_settings()

T = TypeVar("T", bound=BaseModel)

def http_client(headers: dict = None, timeout: Optional[int] = 60) -> httpx.AsyncClient:
    timeout = httpx.Timeout(timeout=timeout)
    client = httpx.AsyncClient(
        base_url=settings.CLI_BACKEND_ORIGIN_URL, headers=headers, timeout=timeout
    )
    return client

class TokenPayload(BaseModel):
    exp: Optional[int] = None
    sub: Optional[str] = None

class HTTPRepository:
    def __init__(self):
        self.client = http_client()
        self.creds_manager = CredentialsManager()

    def get_token(self) -> Optional[str]:
        return "dev-token"  # override token logic for dev/testing

    async def _request(
        self,
        method: str,
        url: str,
        expected_status_code: int,
        parse_as: Optional[Type[T]] = None,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
        timeout: Optional[httpx.Timeout] = httpx.Timeout(60),
    ) -> Optional[Union[T, httpx.Response]]:
        try:
            # ✅ Debug logging
            print(f"[HTTP REQUEST] {method} {url}")
            print(f"  Headers: {headers}")
            print(f"  JSON: {json}")

            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json,
                headers=headers,
                timeout=timeout,
            )

            if response.status_code == expected_status_code:
                if not parse_as:
                    return response

                try:
                    if response.content:
                        return parse_as(**response.json())
                    elif issubclass(parse_as, BaseModel):
                        return None
                    else:
                        return None
                except ValidationError as e:
                    raise APIError(
                        f"Failed to cast HTTP response from {url}, method={method} to pydantic model: {parse_as.__name__}\n{e.json()}",
                        status_code=response.status_code,
                        response_body=response.text,
                    )
                except Exception:
                    render_error(f"Unknown error occurred: {traceback.format_exc()}")
                    raise typer.Exit(1)
            else:
                raise MismatchingExpectedStatusCodeError(
                    f"API request failed for {url}, method={method}",
                    status_code=response.status_code,
                    response_body=response.text,
                )

        except httpx.RequestError as e:
            raise APIError(f"HTTP request failed: {e}")

    # 🔐 Auth methods (disabled in local dev)
    async def login_user(self, username: str, password: str) -> Optional[AccessToken]:
        raise APIError("🔒 Login is disabled in this local development mode.")

    async def register_user(self, username: str, password: str) -> None:
        raise APIError("🔒 User registration is disabled in this local development mode.")

    # 🔁 Agent CRUD endpoints
    async def list_agents(
        self, limit: int, offset: int, headers: Optional[dict] = {}
    ) -> httpx.Response:
        return await self._request(
            url="/api/agents/",
            method="GET",
            params={"limit": limit, "offset": offset},
            expected_status_code=200,
            headers=headers,
        )

    async def register_agent(
        self, agent_id: str, name: str, description: str, headers: Optional[dict] = {}
    ) -> httpx.Response:
        return await self._request(
            method="POST",
            url="/api/agents/register",
            json={
                "id": agent_id,
                "name": name,
                "description": description,
                "input_parameters": {},
            },
            expected_status_code=200,
            headers=headers,
        )

    async def delete_agent(self, agent_id: str, headers: Optional[dict] = {}):
        return await self._request(
            method="DELETE",
            url=f"/api/agents/{agent_id}",
            expected_status_code=204,
            headers=headers,
        )

    async def lookup_agent(
        self, agent_id: str, headers: Optional[dict] = {}
    ) -> Optional[AgentSchema]:
        response = await self._request(
            url=f"/api/agents/{agent_id}",
            method="GET",
            expected_status_code=200,
            parse_as=AgentSchema,
            headers=headers,
        )
        if not response:
            raise APIError(
                "HTTP request was successful, but unexpectedly agent response was malformed"
            )
        return response


http_repo = HTTPRepository()
