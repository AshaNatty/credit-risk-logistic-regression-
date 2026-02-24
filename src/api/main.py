"""FastAPI application entry point."""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from src.api.router import router
from src.core.config import Settings
from src.core.logging_config import configure_logging
from src.core.orchestrator import Orchestrator

settings = Settings()
configure_logging(settings.log_level)

app = FastAPI(
    title="Agentic AI Core Framework",
    description="Production-grade multi-agent orchestration platform.",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

app.include_router(router)


@app.on_event("startup")
async def on_startup() -> None:
    orchestrator = Orchestrator(settings=settings)
    await orchestrator.setup()
    app.state.orchestrator = orchestrator
    logging.getLogger(__name__).info("application_startup")


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await app.state.orchestrator.teardown()
    logging.getLogger(__name__).info("application_shutdown")
