FROM python:3.11-slim-bookworm

RUN export PYTHONDONTWRITEBYTECODE=1

RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y --no-install-recommends tini && \
    apt-get -y clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd --create-home appuser
USER appuser

WORKDIR /app
COPY app .

EXPOSE 8000

ENTRYPOINT ["tini", "--", "uvicorn", "--host", "0.0.0.0", "app:api"]
