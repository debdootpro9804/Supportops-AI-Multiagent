
from fastapi import FastAPI

app= FastAPI(
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
