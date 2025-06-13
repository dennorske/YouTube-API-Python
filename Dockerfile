FROM --platform=linux/amd64 python:3.13-bullseye

WORKDIR /usr/src/app

COPY . .

RUN apt-get update -qq && apt-get install -qq ffmpeg \
    && rm -rf /var/lib/apt/lists/* && pip install uv && uv sync --no-dev
EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
