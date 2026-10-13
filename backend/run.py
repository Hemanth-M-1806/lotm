import asyncio
import selectors
import sys
import uvicorn
from app.main import app


class SelectorServer(uvicorn.Server):
    """Custom Uvicorn server enforcing asyncio.SelectorEventLoop on Windows for Psycopg 3."""

    def run(self, sockets=None) -> None:
        if sys.platform == "win32":
            return asyncio.run(
                self.serve(sockets=sockets),
                loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector()),
            )
        return super().run(sockets=sockets)


def main() -> None:
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
        access_log=True,
    )
    server = SelectorServer(config=config)
    server.run()


if __name__ == "__main__":
    main()
