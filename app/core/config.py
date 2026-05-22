from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    riot_api_key: str

    db_host: str
    db_port: int
    db_name: str = Field(alias='POSTGRES_DB')
    db_user: str = Field(alias='POSTGRES_USER')
    db_password: str = Field(alias='POSTGRES_PASSWORD')

    @property
    def database_url(self) -> str:
        return (
            f'postgresql+asyncpg://'
            f'{self.db_user}:{self.db_password}'
            f'@{self.db_host}:{self.db_port}/{self.db_name}'
        )

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
