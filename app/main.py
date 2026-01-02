"""
FastAPI Application for Text-to-Code Generation
Includes monitoring, logging, and health checks
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from contextlib import asynccontextmanager
import time
import logging
import json
from datetime import datetime
from typing import Optional
import os

from .model import T5CodeGenerator
from .schemas import CodeRequest, CodeResponse, HealthResponse

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'text_to_code_requests_total', 
    'Total number of code generation requests',
    ['status']
)
REQUEST_LATENCY = Histogram(
    'text_to_code_latency_seconds', 
    'Request latency in seconds',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)
ACTIVE_REQUESTS = Gauge(
    'text_to_code_active_requests',
    'Number of active requests'
)
MODEL_LOAD_STATUS = Gauge(
    'text_to_code_model_loaded',
    'Model load status (1=loaded, 0=not loaded)'
)

# Global model instance
code_generator: Optional[T5CodeGenerator] = None

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup
    logger.info("Starting up Text-to-Code API...")
    try:
        global code_generator
        if code_generator is None:
            logger.info("Initializing T5 Code Generator...")
            code_generator = T5CodeGenerator()
            MODEL_LOAD_STATUS.set(1 if code_generator.is_loaded() else 0)
            logger.info("Model initialized successfully")
        logger.info("Startup complete")
    except Exception as e:
        logger.error(f"Failed to initialize model: {str(e)}")
        MODEL_LOAD_STATUS.set(0)
    
    yield
    
    # Shutdown
    logger.info("Shutting down Text-to-Code API...")

# Initialize FastAPI app
app = FastAPI(
    title="Text-to-Code Generation API",
    description="Generate Python code from natural language descriptions using fine-tuned T5 model",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

def get_model():
    """Get the code generator model (initialized during startup)"""
    global code_generator
    if code_generator is None:
        raise RuntimeError("Model not initialized. Please check startup logs.")
    return code_generator

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing"""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add custom header with processing time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"Status: {response.status_code} Time: {process_time:.3f}s"
        )
        
        return response
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        raise

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Text-to-Code Generation API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring
    Returns model status and system health
    """
    try:
        model = get_model()
        is_healthy = model.is_loaded()
        
        return HealthResponse(
            status="healthy" if is_healthy else "unhealthy",
            model_loaded=is_healthy,
            timestamp=datetime.utcnow().isoformat(),
            version="1.0.0"
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            model_loaded=False,
            timestamp=datetime.utcnow().isoformat(),
            version="1.0.0",
            error=str(e)
        )

@app.post("/generate", response_model=CodeResponse, tags=["Code Generation"])
async def generate_code(request: CodeRequest):
    """
    Generate Python code from natural language description
    
    Parameters:
    - prompt: Natural language description of the code to generate
    - max_length: Maximum length of generated code (default: 150)
    - temperature: Sampling temperature (default: 0.7)
    
    Returns:
    - code: Generated Python code
    - latency: Generation time in seconds
    - timestamp: Generation timestamp
    """
    start_time = time.time()
    ACTIVE_REQUESTS.inc()
    
    try:
        # Get model
        try:
            model = get_model()
        except RuntimeError as e:
            # Model not initialized yet (happens during tests or startup failures)
            REQUEST_COUNT.labels(status='error').inc()
            raise HTTPException(
                status_code=503,
                detail="Model not initialized. Please try again later."
            )
        
        if not model.is_loaded():
            REQUEST_COUNT.labels(status='error').inc()
            raise HTTPException(
                status_code=503, 
                detail="Model not loaded. Please try again later."
            )
        
        # Generate code
        logger.info(f"Generating code for prompt: {request.prompt[:50]}...")
        
        generated_code = model.generate(
            prompt=request.prompt,
            max_length=request.max_length,
            temperature=request.temperature
        )
        
        # Calculate latency
        latency = time.time() - start_time
        
        # Update metrics
        REQUEST_LATENCY.observe(latency)
        REQUEST_COUNT.labels(status='success').inc()
        
        # Log successful generation
        logger.info(
            json.dumps({
                "event": "code_generation",
                "status": "success",
                "prompt_length": len(request.prompt),
                "code_length": len(generated_code),
                "latency": round(latency, 3),
                "timestamp": datetime.utcnow().isoformat()
            })
        )
        
        return CodeResponse(
            code=generated_code,
            latency=round(latency, 3),
            timestamp=datetime.utcnow().isoformat(),
            prompt=request.prompt
        )
        
    except HTTPException:
        raise
    except Exception as e:
        REQUEST_COUNT.labels(status='error').inc()
        logger.error(
            json.dumps({
                "event": "code_generation",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
        )
        raise HTTPException(status_code=500, detail=f"Code generation failed: {str(e)}")
    
    finally:
        ACTIVE_REQUESTS.dec()

@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """
    Prometheus metrics endpoint
    Returns metrics in Prometheus format
    """
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )

@app.get("/stats", tags=["Monitoring"])
async def stats():
    """
    Get API statistics
    """
    try:
        model = get_model()
        model_loaded = model.is_loaded()
    except:
        model_loaded = False
    
    return {
        "model_loaded": model_loaded,
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
