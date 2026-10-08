FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY src ./src

RUN pip install --no-cache-dir .

COPY alembic ./alembic
COPY alembic.ini .
COPY entrypoint.sh .

RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]