# ==========================================
# Stage 1 Builder
# ==========================================
FROM registry.access.redhat.com/hi/python:latest-builder AS builder
USER root
WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
RUN mkdir -p /data

# ==========================================
# Stage 2 Final (rootless, hardened)
# ==========================================
FROM registry.access.redhat.com/hi/python:latest AS final

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GAME_DB_PATH=/data/games.db

USER root
WORKDIR /usr/src/app

COPY --from=builder --chown=1001:0 /opt/venv /opt/venv
COPY --from=builder --chown=1001:0 /data /data
COPY --chown=1001:0 game.py lemke_howson.py williams.py project.py repeated.py ./
COPY --chown=1001:0 games ./games
COPY --chown=1001:0 webapp ./webapp

USER 1001
EXPOSE 8080
VOLUME /data

CMD ["uvicorn", "webapp.app:app", "--host", "0.0.0.0", "--port", "8080"]
