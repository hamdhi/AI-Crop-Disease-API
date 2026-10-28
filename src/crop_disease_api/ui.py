"""Serve the local upload page and open it once the server is ready."""

from contextlib import asynccontextmanager
import logging
from pathlib import Path
from threading import Event, Thread
from urllib.request import ProxyHandler, build_opener
import webbrowser

from fastapi import APIRouter, FastAPI
from fastapi.responses import FileResponse

router = APIRouter()
UI_URL = "http://127.0.0.1:8000/ui"
logger = logging.getLogger(__name__)


@router.get("/ui", include_in_schema=False)
async def ui() -> FileResponse:
    return FileResponse(Path(__file__).with_name("ui.html"), media_type="text/html")


def open_browser_when_ready(stop: Event) -> None:
    # Run outside the event loop so startup can finish before the first request.
    opener = build_opener(ProxyHandler({}))
    for _ in range(60):
        if stop.wait(0.5):
            return
        try:
            with opener.open(UI_URL, timeout=1) as response:
                if response.status != 200:
                    continue
        except OSError:
            continue
        if stop.is_set():
            return
        try:
            if not webbrowser.open(UI_URL, new=2):
                logger.warning("Open the UI manually at %s", UI_URL)
        except Exception:
            logger.warning("Could not launch the browser. Open %s manually.", UI_URL)
        return
    logger.warning("UI readiness check timed out. Open %s manually.", UI_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    stop = Event()
    Thread(target=open_browser_when_ready, args=(stop,), daemon=True).start()
    try:
        yield
    finally:
        stop.set()
