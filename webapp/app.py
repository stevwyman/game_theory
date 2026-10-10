import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware

from webapp.service import analyze, list_examples, load_example, save_example
from webapp.store import init_store

BASE_DIR = Path(__file__).resolve().parent


def configured_root_path() -> str:
    raw = os.environ.get("ROOT_PATH", "").strip().rstrip("/")
    if not raw or raw == "/":
        return ""
    if not raw.startswith("/"):
        raw = f"/{raw}"
    parts = [part for part in raw.split("/") if part != ""]
    if not parts or any(part in {".", ".."} for part in parts):
        return ""
    return "/" + "/".join(parts)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_store()
    yield


app = FastAPI(
    title="Game theory solver",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'"
        )
        response.headers["Cache-Control"] = "no-store"
        return response


class RootPathMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] in {"http", "websocket"}:
            prefix = configured_root_path()
            path = scope.get("path", "")
            if prefix and (path == prefix or path.startswith(f"{prefix}/")):
                scope = dict(scope)
                remainder = path[len(prefix) :] or "/"
                scope["path"] = remainder
                raw_path = scope.get("raw_path")
                if isinstance(raw_path, (bytes, bytearray)):
                    scope["raw_path"] = remainder.encode("ascii")
        await self.app(scope, receive, send)


app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RootPathMiddleware)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"examples": list_examples(), "root_path": configured_root_path()},
    )


@app.get("/api/examples")
def examples():
    return {"examples": list_examples()}


@app.get("/api/examples/{example_id}")
def example(example_id: str):
    try:
        return load_example(example_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.post("/api/games")
def create_or_update_game(payload: dict):
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="JSON object required")
    try:
        return save_example(payload)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/solve")
def solve(payload: dict):
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="JSON object required")
    try:
        return analyze(payload)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
