from fastapi import FastAPI, HTTPException

from kivai_sdk.validator import validate_command
from kivai_sdk.runtime import execute_intent


app = FastAPI(
    title="KIVAI Gateway (v0.1)",
    version="0.1.0",
    description="Reference Gateway/Hub for Kivai intents (Tech4Life & Beyond).",
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "kivai-gateway", "version": "0.1.0"}


@app.post("/v1/validate")
def validate_intent(payload: dict):
    ok, message = validate_command(payload)
    if not ok:
        raise HTTPException(status_code=400, detail=message)
    return {"ok": True, "message": message}


@app.post("/v1/execute")
def execute(payload: dict):
    ack = execute_intent(payload)
    # If failed, return 400 but include ACK body (auditable)
    if ack.get("status") != "ok":
        raise HTTPException(status_code=400, detail=ack)
    return ack
