"""
SportsLot Optimizer — FastAPI backend entry point.
AI-powered revenue optimization for sports turf bookings.
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# ── Logging ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("sportslot")


# ── Lifespan — create tables on startup ─────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    from backend.app.database.connection import engine, Base
    # Import all models so Base.metadata knows about them
    import backend.app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created / verified")
    yield
    logger.info("Shutting down SportsLot Optimizer")


# ── App ──────────────────────────────────────────────────────────────────
app = FastAPI(
    title="SportsLot Optimizer",
    description="AI-powered agent for filling vacant sports turf slots and maximizing revenue.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow all origins for hackathon dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health endpoint ──────────────────────────────────────────────────────
@app.get("/api/health", tags=["Health"])
def health():
    ai_mode = os.getenv("AI_MODE", "mock")
    return {
        "status": "healthy",
        "service": "SportsLot Optimizer",
        "ai_mode": ai_mode,
    }


# ── Mount route modules ─────────────────────────────────────────────────
from backend.app.routes.slots import router as slots_router
from backend.app.routes.customers import router as customers_router
from backend.app.routes.bookings import router as bookings_router
from backend.app.routes.agent import router as agent_router

app.include_router(slots_router)
app.include_router(customers_router)
app.include_router(bookings_router)
app.include_router(agent_router)
