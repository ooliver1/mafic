FROM python:3.11-slim-bullseye

WORKDIR /bot

RUN apt-get update && apt-get install build-essential git -y && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root --only=main

COPY . .

ENTRYPOINT ["poetry", "run", "python3"]
CMD ["-m", "bot"]
