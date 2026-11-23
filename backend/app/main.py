import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth import router as auth_router
from app.routes.datasets import router as datasets_router
from app.routes.documents import router as documents_router
from app.routes.analysis import router as analysis_router
from app.routes.data_sources import router as data_sources_router

app = FastAPI(
    title="AI Data Analysis API",
    description="AI-powered data analysis application",
    version="1.0.0"
)

# Explicit CORS Origins for local React development and production
DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

env_cors = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]

# Prohibit wildcard "*" when allow_credentials=True
allowed_origins = list(dict.fromkeys(DEFAULT_CORS_ORIGINS + env_cors))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
)

@app.get("/")
def home():
    return {"message": "Welcome to AI-Database Analysis"}

app.include_router(auth_router)
app.include_router(datasets_router)
app.include_router(documents_router)
app.include_router(analysis_router)
app.include_router(data_sources_router)