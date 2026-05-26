from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any
from urllib.parse import quote, urlparse

import httpx
from aiolimiter import AsyncLimiter

from .constants import (
    DEFAULT_MATCH_COUNT,
    PLATFORM_BASE_URL,
    REGIONAL_BASE_URL,
)
from .exceptions import (
    RiotAPIError,
    RiotForbiddenError,
    RiotNotFoundError,
    RiotRateLimitError,
    RiotRequestError,
    RiotServerError,
)
from .schemas import (
    RiotAccountSchema,
    RiotMatchesSchema,
    RiotMatchSchema,
    RiotRankedEntriesSchema,
    RiotRankedEntrySchema,
    RiotSummonerSchema,
)


class RiotAPIClient:
    MAX_RETRIES = 3

    def __init__(self, *, client: httpx.AsyncClient) -> None:
        self._client = client
        self._limiters: dict[str, tuple[AsyncLimiter, AsyncLimiter]] = {}

    def _get_limiters(self, url: str) -> tuple[AsyncLimiter, AsyncLimiter]:
        host = urlparse(url).netloc

        if host not in self._limiters:
            self._limiters[host] = (
                AsyncLimiter(20, 1),
                AsyncLimiter(100, 120),
            )

        return self._limiters[host]

    @staticmethod
    def _platform_url(platform: str, path: str) -> str:
        return f'{PLATFORM_BASE_URL.format(platform=platform)}{path}'

    @staticmethod
    def _regional_url(region: str, path: str) -> str:
        return f'{REGIONAL_BASE_URL.format(region=region)}{path}'

    async def _request(self, method: str, url: str, **kwargs) -> dict[str, Any]:
        short_limiter, long_limiter = self._get_limiters(url)

        for attempt in range(self.MAX_RETRIES):
            try:
                async with short_limiter:
                    async with long_limiter:
                        response = await self._client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as err:
                if attempt == self.MAX_RETRIES - 1:
                    raise RiotRequestError(str(err), method=method, url=url) from err

                backoff = 2**attempt
                await asyncio.sleep(backoff)
            except httpx.HTTPStatusError as err:
                status_code = err.response.status_code

                if status_code == 403:
                    raise RiotForbiddenError(
                        method=method,
                        url=url,
                        response_body=err.response.text[:1000],
                    ) from err

                if status_code == 404:
                    raise RiotNotFoundError(
                        method=method,
                        url=url,
                        response_body=err.response.text[:1000],
                    ) from err

                if status_code == 429:
                    retry_after = int(err.response.headers.get('Retry-After', '1'))
                    
                    if attempt == self.MAX_RETRIES - 1:
                        raise RiotRateLimitError(
                            method=method,
                            url=url,
                            retry_after=retry_after,
                            response_body=err.response.text[:1000],
                        ) from err

                    await asyncio.sleep(retry_after)
                    continue

                if status_code >= 500:
                    if attempt == self.MAX_RETRIES - 1:
                        raise RiotServerError(
                            method=method,
                            url=url,
                            status_code=status_code,
                            response_body=err.response.text[:1000],
                        ) from err

                    backoff = 2**attempt
                    await asyncio.sleep(backoff)
                    continue

                raise RiotAPIError(
                    message='Unexpected Riot API error',
                    status_code=status_code,
                    method=method,
                    url=url,
                    response_body=err.response.text[:1000],
                ) from err

        raise RuntimeError('Unreachable code reached in RiotAPIClient._request')

    async def get_account_by_riot_id(
            self,
            *,
            region: str,
            game_name: str,
            tag_line: str,
    ) -> RiotAccountSchema:
        safe_game_name = quote(game_name, safe='')
        safe_tag_line = quote(tag_line, safe='')
        
        url = self._regional_url(
            region,
            (
                '/riot/account/v1/accounts/by-riot-id/'
                f'{safe_game_name}/{safe_tag_line}'
            ),
        )

        data = await self._request(method='GET', url=url)

        return RiotAccountSchema.model_validate(data)

    async def get_summoner_by_puuid(
            self,
            *,
            platform: str,
            puuid: str,
    ) -> RiotSummonerSchema:
        url = self._platform_url(
            platform,
            f'/lol/summoner/v4/summoners/by-puuid/{puuid}',
        )

        data = await self._request(method='GET', url=url)

        return RiotSummonerSchema.model_validate(data)

    async def get_league_entries_by_puuid(
            self,
            *,
            platform: str,
            puuid: str,
    ) -> list[RiotRankedEntrySchema]:
        url = self._platform_url(
            platform,
            f'/lol/league/v4/entries/by-puuid/{puuid}',
        )

        data = await self._request(method='GET', url=url)

        return RiotRankedEntriesSchema.model_validate(data).root

    async def get_match_ids_by_puuid(
            self,
            *,
            region: str,
            puuid: str,
            start: int = 0,
            count: int = DEFAULT_MATCH_COUNT,
            start_time: int | None = None,
    ) -> list[str]:
        url = self._regional_url(
            region,
            f'/lol/match/v5/matches/by-puuid/{puuid}/ids',
        )

        params = {
            'start': start,
            'count': count,
        }

        if start_time is not None:
            params['startTime'] = start_time

        data = await self._request(method='GET', url=url, params=params)

        return RiotMatchesSchema.model_validate(data).root

    async def iter_match_id_pages(
            self,
            *,
            region: str,
            puuid: str,
            start_time: int | None = None,
            page_size: int = DEFAULT_MATCH_COUNT,
    ) -> AsyncIterator[list[str]]:
        start = 0

        while True:
            page = await self.get_match_ids_by_puuid(
                region=region,
                puuid=puuid,
                start_time=start_time,
                count=page_size,
                start=start,
            )
            if not page:
                break

            yield page

            if len(page) < page_size:
                break
            
            start += page_size

    async def get_match(
            self,
            *,
            region: str,
            match_id: str,
    ) -> RiotMatchSchema:
        url = self._regional_url(
            region,
            f'/lol/match/v5/matches/{match_id}',
        )

        data = await self._request(method='GET', url=url)

        return RiotMatchSchema.model_validate(data)
