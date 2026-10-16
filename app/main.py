
from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import check_database_connection

app = FastAPI(
    title="SupportOps AI",
    description="Customer support triage and resolution platform",
    version="0.1.0",
)


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {
        "name": "SupportOps AI",
        "status": "running",
        "message": "Customer support triage platform",
    }


@app.get("/health/live", tags=["health"])
def liveness() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready", tags=["health"])
def readiness() -> dict[str, str]:
    try:
        check_database_connection()
    except (SQLAlchemyError, RuntimeError) as exc:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        ) from exc

    return {
        "status": "ready",
        "database": "ok",
    }
