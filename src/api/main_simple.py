"""Minimal API for Railway deployment"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from dotenv import load_dotenv

# Load environment variables
if os.getenv("ENVIRONMENT") != "production":
    load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Jenosize API",
    description="Basic article generator",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "jenosize-api",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "service": "Jenosize API",
        "status": "running",
        "message": "Basic deployment successful!"
    }

# Test endpoint
@app.post("/generate")
async def generate_test():
    return {
        "content": "Test article generated successfully!",
        "success": True,
        "note": "This is a minimal version for testing Railway deployment"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)