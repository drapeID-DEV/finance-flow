from finance_flow.config import Settings


def test_settings_load_defaults() -> None:
    settings = Settings(
        database_url="postgresql+psycopg://test:test@localhost:5432/test",
        jwt_secret="test-secret",
    )

    assert settings.database_url == (
        "postgresql+psycopg://test:test@localhost:5432/test"
    )
    assert settings.nbu_base_url == "https://bank.gov.ua/NBUStatService/v1"