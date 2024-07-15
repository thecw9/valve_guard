from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.db import engine, init_db
from src.wait_for_nrmock import wait_for_nrmock
from src.api import (
    auth_router,
    measures_router,
    model_router,
    alarm_router,
    devices_router,
    fusion_model_router,
    train_logs_router,
)

wait_for_nrmock()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    engine.dispose()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    auth_router,
    prefix="/auth-service",
    tags=["auth-service"],
)
app.include_router(
    measures_router,
    prefix="/measures-service",
    tags=["measures-service"],
)
app.include_router(
    devices_router,
    prefix="/devices-service",
    tags=["devices-service"],
)
app.include_router(
    alarm_router,
    prefix="/alarm-service",
    tags=["alarm-service"],
)
app.include_router(
    model_router,
    prefix="/model-service",
    tags=["model-service"],
)
app.include_router(
    fusion_model_router,
    prefix="/fusion-model-service",
    tags=["fusion-model-service"],
)
app.include_router(
    train_logs_router,
    prefix="/train-logs-service",
    tags=["train-logs-service"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
