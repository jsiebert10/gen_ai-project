from config import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.health import router as health_router

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


@app.get("/")
def root():
    return {"message": "International Student AI Consultant API is running."}
