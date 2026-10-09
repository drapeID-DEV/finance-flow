
import os
from logging.config import fileConfig

from dotenv import dotenv_values
from sqlalchemy import create_engine, pool
from sqlalchemy.engine import make_url

from alembic import context
from finance_flow.config import get_settings
from finance_flow.models.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = get_settings()

env_values = dotenv_values(".env")

database_url = (
    os.getenv("TEST_DATABASE_URL")
    or env_values.get("TEST_DATABASE_URL")
    or ""
)

if not database_url:
    raise RuntimeError(
        "TEST_DATABASE_URL is missing in environment and .env"
    )

parsed_url = make_url(database_url)

if parsed_url.database != "finance_flow_test":
    raise RuntimeError(
        "Alembic is allowed to run only on finance_flow_test. "
        f"Current database: {parsed_url.database!r}"
    )


database_url = database_url.replace(
    "postgresql+asyncpg://",
    "postgresql+psycopg://",
)

config.set_main_option(
    "sqlalchemy.url",
    database_url,
)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    try:
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
            )

            with context.begin_transaction():
                context.run_migrations()
    finally:
        connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
