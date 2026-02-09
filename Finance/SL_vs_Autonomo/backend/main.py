"""
Simulador Fiscal España — FastAPI Backend
==========================================
API for Spanish tax calculations comparing Employee, Autónomo, and SL regimes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router

app = FastAPI(
    title="Simulador Fiscal España",
    description="API for Spanish tax regime comparison: Employee vs Autónomo vs SL",
    version="2.0.0",
)

# CORS for frontend dev server and production
# Note: Cannot use allow_credentials=True with wildcard origins
import os
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,https://fiscal.xelia.es").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
async def root():
    return {
        "name": "Simulador Fiscal España",
        "version": "2.0.0",
        "endpoints": [
            "POST /api/employee",
            "POST /api/autonomo",
            "POST /api/sl",
            "POST /api/sl/optimal-salary",
            "POST /api/compare",
            "POST /api/compare/crossover",
            "POST /api/investment",
            "POST /api/investment/compare",
            "POST /api/investment/sensitivity",
            "GET /api/regions",
            "GET /api/presets",
        ],
    }
