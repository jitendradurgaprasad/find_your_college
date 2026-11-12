from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database.session import engine, Base
from app.api.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize all database tables on startup
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent College Discovery & Fact Intelligence Platform backend.",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permits Next.js frontend on any port/domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "tagline": "Discover colleges. Explore opportunities. Make informed decisions.",
        "documentation": "/docs",
        "status": "OPERATIONAL"
    }

@app.get("/health")
def health_check():
    return {"status": "HEALTHY", "version": settings.VERSION}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
