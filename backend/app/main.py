from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .database import Base, engine
from .errors import BudgetExceededError, NotFoundError, PermissionDeniedError
from .routers import auth_router, items_router, lists_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ShareList")

app.include_router(auth_router.router)
app.include_router(lists_router.router)
app.include_router(items_router.router)


@app.exception_handler(BudgetExceededError)
def handle_budget_exceeded(request: Request, exc: BudgetExceededError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(PermissionDeniedError)
def handle_permission_denied(request: Request, exc: PermissionDeniedError):
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.exception_handler(NotFoundError)
def handle_not_found(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR / "static"), name="static")
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
