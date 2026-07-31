from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from dotenv import load_dotenv

from routes import incidents, reports, health, decisions
from services.rabbitmq_service import init_rabbitmq, close_rabbitmq
from database import init_db

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Nostromus Backend...")
    logger.info("Initializing database...")
    init_db()
    await init_rabbitmq()
    yield
    logger.info("Shutting down Nostromus Backend...")
    await close_rabbitmq()

app = FastAPI(
    title="Nostromus Backend API",
    description="Event-driven incident response system with AI",
    version="0.1.0",
    lifespan=lifespan
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router, tags=["Health"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["Incidents"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(decisions.router, tags=["Decisions"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Nostromus Backend API",
        "version": "0.1.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
