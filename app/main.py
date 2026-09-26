from fastapi import FastAPI
from app.logging_config import configure_logging
from app.api import api_router

configure_logging()

app = FastAPI(title="AutoPilot AI", version="0.1.0")
app.include_router(api_router)