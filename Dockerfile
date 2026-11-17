FROM node:24-slim AS assets

RUN npm install --global pnpm@10

WORKDIR /app

# Install dependencies in their own layer so source changes don't rebuild them
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN --mount=type=cache,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile

COPY build.mjs ./
COPY static ./static
RUN pnpm build


FROM python:3.14-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/venv \
    PATH="/venv/bin:$PATH"

WORKDIR /app

# Install dependencies in their own layer so code changes don't rebuild them
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

COPY . /app
COPY --from=assets /app/build /app/build

# The manifest storage is only active with DEBUG off
RUN SECRET_KEY=collectstatic DEBUG=false python manage.py collectstatic --noinput

CMD ["/venv/bin/gunicorn", "open_humans.wsgi", "--bind", "0.0.0.0:8000"]
