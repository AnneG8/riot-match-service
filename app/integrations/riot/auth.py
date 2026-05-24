from collections.abc import Generator

import httpx


class RiotAPIAuth(httpx.Auth):
    def __init__(self, *, token: str) -> None:
        self.token = token

    def auth_flow(
        self,
        request: httpx.Request,
    ) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers['X-Riot-Token'] = self.token
        yield request
