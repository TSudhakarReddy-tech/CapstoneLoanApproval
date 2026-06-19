"""FastAPI application setup."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.api.routes import applications

app = FastAPI(
    title="Loan Approval API",
    description="AI-driven loan approval automation system",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "loan-approval-api"}


# Include route modules
app.include_router(applications.router, prefix="/api", tags=["applications"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Loan Approval API",
        "version": "0.1.0",
        "docs": "/docs",
    }
