from typing import Any


class RiotError(Exception):
    def __init__(
            self,
            message: str,
            *,
            method: str,
            url: str,
    ) -> None:
        self.message = message
        self.method = method
        self.url = url

        super().__init__(message)

    def __str__(self):
        return (
            f'{self.__class__.__name__}: '
            f'{self.message} [{self.method} {self.url}]'
        )

class RiotRequestError(RiotError):
    pass


class RiotAPIError(RiotError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        method: str,
        url: str,
        response_body: Any | None = None,
    ) -> None:
        self.status_code = status_code
        self.response_body = response_body

        super().__init__(message, method=method, url=url)


class RiotForbiddenError(RiotAPIError):
    def __init__(
            self,
            *,
            method: str,
            url: str,
            response_body: Any | None = None,
    ) -> None:
        super().__init__(
            'Riot API key is invalid or expired',
            status_code=403,
            method=method,
            url=url,
            response_body=response_body,
        )


class RiotNotFoundError(RiotAPIError):
    def __init__(
            self,
            *,
            method: str,
            url: str,
            response_body: Any | None = None,
    ) -> None:
        super().__init__(
            'Requested Riot resource was not found',
            status_code=404,
            method=method,
            url=url,
            response_body=response_body,
        )


class RiotRateLimitError(RiotAPIError):
    def __init__(
            self,
            *,
            method: str,
            url: str,
            retry_after: int,
            response_body: Any | None = None,
    ) -> None:
        self.retry_after = retry_after

        super().__init__(
            f'Riot API rate limit exceeded. Retry after {retry_after}s',
            status_code=429,
            method=method,
            url=url,
            response_body=response_body,
        )


class RiotServerError(RiotAPIError):
    def __init__(
            self,
            *,
            method: str,
            url: str,
            status_code: int = 500,
            response_body: Any | None = None,
    ) -> None:
        super().__init__(
            'Riot API temporary server error',
            status_code=status_code,
            method=method,
            url=url,
            response_body=response_body,
        )
