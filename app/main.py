from app.core import get_logger, setup_logging
from ollama import Client
from app.core import get_settings
from app.prompts import load_prompt
from app.tools import TOOLS_MAP, TOOLS_SCHEMA

from .tools import dispatcher

from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from app.routers import router as app_router

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up application...")
    setup_logging()

    settings = get_settings()

    client = Client(host=settings.llm_base_url)
    logger.info(f"Connected to LLM at {settings.llm_base_url}")
    
    # Store in app state for use in routes
    app.state.llm_client = client
    app.state.settings = settings
    
    yield
    
    logger.info("Shutting down application...")
    logger.info("Application shut down successfully")

app = FastAPI(lifespan=lifespan)
        

app.include_router(app_router.router)


@app.get("/health")
async def home():
    return {"status": "healthy"}

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        app=app,
        host=settings.app_host,
        port=settings.app_port,
        log_level="info"
    )
