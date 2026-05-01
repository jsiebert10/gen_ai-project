from config import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.career import router as career_router
from routes.health import router as health_router
from routes.match import router as match_router
from routes.profile import router as profile_router
from routes.visa import router as visa_router

app = FastAPI(
    title="International Student AI Consultant",
    description="Multi-agent backend for education and career pathway guidance.",
    version="0.1.0",
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health_router, prefix="/api")
app.include_router(profile_router, prefix="/api")
app.include_router(match_router, prefix="/api")
app.include_router(visa_router, prefix="/api")
app.include_router(career_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "International Student AI Consultant API is running."}
