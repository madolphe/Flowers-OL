# syntax=docker/dockerfile:1
FROM python:3.8.20-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ADD . /src

WORKDIR /src

RUN uv sync --frozen

WORKDIR /src/flowers-ol

CMD ["uv", "run", "python", "./scripts/deploy.py", "-r"]

