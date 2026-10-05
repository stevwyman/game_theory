import os

import uvicorn

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8080


def main() -> None:
    host = os.environ.get("HOST", DEFAULT_HOST)
    port = int(os.environ.get("PORT", str(DEFAULT_PORT)))
    uvicorn.run("webapp.app:app", host=host, port=port)


if __name__ == "__main__":
    main()
