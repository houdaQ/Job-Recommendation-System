import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import database as db
from app.routers import jobs, recommend

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.load_jobs()
    yield

app = FastAPI(
    title="Job Recommendation System",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)
app.include_router(recommend.router)

@app.get("/")
async def root():
    return {"status": "ok", "message": "API running 🚀"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "jobs_indexed": len(db.list_jobs()),
        "version": "1.0.0",
    }