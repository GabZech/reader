FROM mcr.microsoft.com/devcontainers/python:3.12

# Same uv version as the production Dockerfile and CI.
COPY --from=ghcr.io/astral-sh/uv:0.12.1 /uv /uvx /usr/local/bin/
