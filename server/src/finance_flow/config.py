from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FinanceFlow API"
    app_version: str = "0.1.0"
    database_url: str
    nbu_base_url: str = "https://bank.gov.ua/NBUStatService/v1"
    jwt_secret: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]  # loaded from environment