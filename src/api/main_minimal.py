"""Main API application - Minimal version for Railway deployment"""
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file (development only)
if os.getenv("ENVIRONMENT") != "production":
    load_dotenv()

try:
    from src.api.schemas import ArticleRequest, ArticleResponse, ArticleMetadata
    from src.api.security import (
        rate_limiter, input_sanitizer, security_headers, request_validator,
        audit_logger, get_client_ip, APIKeyAuth
    )
    from src.model.generator import JenosizeTrendGenerator
    from src.model.config import ModelConfig
except ImportError as e:
    logger.error(f"Import error: {e}")
    # Fallback imports or minimal functionality

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Jenosize Trend Articles Generator API",
    description="Generate high-quality business trend articles using AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize security
api_keys = os.getenv("API_KEYS", "").split(",") if os.getenv("API_KEYS") else []
api_key_auth = APIKeyAuth(api_keys) if api_keys else APIKeyAuth()

# Initialize basic generator (no ML dependencies for now)
logger.info("Initializing basic content generator...")
config = ModelConfig()
generator = JenosizeTrendGenerator(config, skip_connection_test=True)  # Skip test for faster startup
style_generator = None  # Disabled temporarily for Railway deployment
logger.info("Basic generator initialized successfully")

# Security middleware
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Add security headers and rate limiting"""
    
    # Get client info
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Log request
    audit_logger.log_request(request, client_ip, user_agent)
    
    # Rate limiting
    if not rate_limiter.is_allowed(client_ip):
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded", "retry_after": 60}
        )
    
    # Input validation
    if not request_validator.is_safe_request(request):
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid request format"}
        )
    
    # Process request
    response = await call_next(request)
    
    # Add security headers
    security_headers.add_headers(response)
    
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    """Comprehensive health check with detailed metrics"""
    
    # Basic service status
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "jenosize-api",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }
    
    # Generator status
    health_status["generators"] = {
        "basic_generator": generator is not None,
        "style_generator": style_generator is not None,
        "claude_available": bool(os.getenv("CLAUDE_API_KEY")),
        "openai_available": bool(os.getenv("OPENAI_API_KEY"))
    }
    
    # System resources (basic) - disabled for minimal deployment
    health_status["system"] = {"status": "metrics_unavailable"}
    
    return health_status

# Root endpoint
@app.get("/")
async def root():
    """API information and status"""
    return {
        "service": "Jenosize Trend Articles Generator API",
        "version": "1.0.0",
        "status": "running",
        "features": [
            "Claude 3 Haiku AI generation",
            "OpenAI GPT fallback",
            "Enterprise security",
            "Health monitoring"
        ],
        "endpoints": {
            "health": "/health",
            "generate": "/generate",
            "docs": "/docs"
        }
    }

# Article generation endpoint
@app.post("/generate", response_model=ArticleResponse)
async def generate_article(
    request: ArticleRequest,
    auth: dict = Depends(api_key_auth.verify_api_key)
):
    """Generate a trend article using AI"""
    
    try:
        # Sanitize input
        sanitized_request = input_sanitizer.sanitize_request(request)
        
        # Use style-aware generator if available, otherwise basic generator
        active_generator = style_generator if style_generator else generator
        
        # Generate article
        logger.info(f"Generating article for topic: {sanitized_request.topic}")
        article_result = active_generator.generate_article(
            topic=sanitized_request.topic,
            category=sanitized_request.category,
            industry=sanitized_request.industry,
            target_audience=sanitized_request.target_audience,
            tone=sanitized_request.tone,
            length=sanitized_request.content_length,
            include_statistics=sanitized_request.include_statistics,
            include_case_studies=sanitized_request.include_case_studies,
            seo_keywords=sanitized_request.seo_keywords,
            call_to_action_type=sanitized_request.call_to_action_type,
            data_sources=sanitized_request.data_sources,
            company_context=sanitized_request.company_context
        )
        
        if not article_result or not article_result.get('content'):
            raise HTTPException(status_code=500, detail="Failed to generate article content")
        
        # Create metadata
        metadata = ArticleMetadata(
            generator_used="style_aware" if style_generator else "basic",
            processing_time=article_result.get('processing_time', 0),
            word_count=len(article_result['content'].split()),
            style_matches=article_result.get('style_matches', []),
            quality_score=article_result.get('quality_score', 0.0),
            model_used=article_result.get('model_used', 'unknown')
        )
        
        # Log successful generation
        audit_logger.log_generation(sanitized_request, metadata)
        
        return ArticleResponse(
            content=article_result['content'],
            metadata=metadata,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Article generation failed: {str(e)}")
        
        # Log error
        audit_logger.log_error(request, str(e))
        
        raise HTTPException(
            status_code=500,
            detail=f"Article generation failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)