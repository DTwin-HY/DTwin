FROM python:3.12-alpine3.22

RUN apk add --no-cache \
    build-base \
    curl \
    libffi-dev \
    openssl-dev \
    libpq-dev \
    postgresql

RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/usr/local python3 -

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --only main --no-interaction --no-ansi

COPY . .

ENV MPLCONFIGDIR=/tmp/matplotlib_cache

EXPOSE 5000

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]