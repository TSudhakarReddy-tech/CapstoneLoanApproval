#!/usr/bin/env python3
"""FastAPI server for loan approval system with 4-agent workflow."""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.api.routes import applications

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="Loan Approval API",
    description="AI-driven loan approval system with multi-agent workflow",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(applications.router, prefix="/api", tags=["applications"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "loan-approval-api",
        "agents": ["profile_agent", "financial_agent", "decision_agent", "compliance_agent"]
    }

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Loan Approval API",
        "version": "1.0.0",
        "docs": "/docs",
        "agents": 4
    }

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="error"
    )
