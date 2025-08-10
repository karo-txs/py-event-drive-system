FROM python:3.12-slim AS base

RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app

RUN pip install uv

COPY pyproject.toml .
RUN uv pip install --system -r pyproject.toml --extra dev

COPY app/ app/

# AWS Lambda Runtime Interface Emulator
RUN apt-get update && apt-get install -y curl

RUN mkdir -p /usr/local/aws-lambda-rie && \
    curl -Lo /usr/local/aws-lambda-rie/aws-lambda-rie \
    https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie && \
    chmod +x /usr/local/aws-lambda-rie/aws-lambda-rie
ENV PATH="/usr/local/aws-lambda-rie:${PATH}"

CMD ["uv", "run", "uvicorn", "app.interfaces.http.main:get_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
