FROM registry.access.redhat.com/ubi9/python-312:1

# Red Hat UBI Python image: regularly patched, non-root UID 1001,
# OpenShift-compatible filesystem layout under /opt/app-root.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY --chown=1001:0 requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY --chown=1001:0 game.py lemke_howson.py williams.py project.py repeated.py ./
COPY --chown=1001:0 games ./games
COPY --chown=1001:0 webapp ./webapp

USER 0
RUN mkdir -p /opt/app-root/src/data \
    && chown -R 1001:0 /opt/app-root/src/data \
    && chmod 775 /opt/app-root/src/data
USER 1001

ENV GAME_DB_PATH=/opt/app-root/src/data/games.db
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=3)"

CMD ["uvicorn", "webapp.app:app", "--host", "0.0.0.0", "--port", "8080"]
