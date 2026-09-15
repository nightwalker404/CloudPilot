from app.core import get_logger, setup_logging, get_settings
from app.core.mongodb import connect_to_mongo, close_mongo_connection
from ollama import Client
from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from app.routers import api_router
from fastapi.middleware.cors import CORSMiddleware

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up application...")
    setup_logging()

    settings = get_settings()

    await connect_to_mongo()
    logger.info("Connected to MongoDB")
    
    client = Client(host=settings.llm_base_url)
    logger.info(f"Connected to LLM at {settings.llm_base_url}")
    
    # Store in app state for use in routes
    app.state.llm_client = client
    app.state.settings = settings
    
    yield
    
    logger.info("Shutting down application...")
    await close_mongo_connection()
    logger.info("Application shut down successfully")

app = FastAPI(lifespan=lifespan)
        

app.include_router(api_router)


@app.get("/health")
async def home():
    return {"status": "healthy"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        app=app,
        host=settings.app_host,
        port=settings.app_port,
        log_level="info"
    )
