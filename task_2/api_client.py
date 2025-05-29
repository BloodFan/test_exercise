import logging

import aiohttp
from my_backoff import backoff

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("api_client")


class HTTPException(Exception):
    def __init__(self, status_code, detail, response_text=None):
        super().__init__(f"HTTP error {status_code}: {detail}")
        self.status_code = status_code
        self.detail = detail
        self.response_text = response_text


class ServerError(Exception):
    def __init__(self, status_code, detail, response_text=None):
        super().__init__(f"Server error {status_code}: {detail}")
        self.status_code = status_code
        self.detail = detail
        self.response_text = response_text


class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()

    @backoff(
        start_sleep_time=0.1,
        factor=2,
        border_sleep_time=10,
        max_restart=5,
        errors=(aiohttp.ClientError, aiohttp.ServerTimeoutError, ServerError),
        client_errors=(HTTPException,),
    )
    async def request(self, method: str, endpoint: str, **kwargs):
        if not self.session:
            logger.error("APIClient used outside async context manager")
            raise RuntimeError(
                "APIClient must be used within an async context manager"
            )
        url = f"{self.base_url}{endpoint}"
        try:
            async with self.session.request(method, url, **kwargs) as response:
                response_text = (
                    await response.text() if response.status >= 400 else None
                )
                if 400 <= response.status < 500:
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Client error: {response_text}",
                        response_text=response_text,
                    )
                elif 500 <= response.status < 600:
                    raise ServerError(
                        status_code=response.status,
                        detail=f"Server error: {response_text}",
                        response_text=response_text,
                    )
                return await response.json()
        except aiohttp.ClientError as client_error:
            logger.warning(
                f"Network error during request to "
                f"{url} (will retry): {client_error}",
                extra={"method": method, "endpoint": endpoint},
            )
            raise client_error
