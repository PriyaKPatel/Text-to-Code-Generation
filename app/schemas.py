"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class CodeRequest(BaseModel):
    """Request schema for code generation"""
    prompt: str = Field(
        ..., 
        min_length=5,
        max_length=500,
        description="Natural language description of the code to generate",
        example="create a function to sort a list in ascending order"
    )
    max_length: int = Field(
        default=150,
        ge=50,
        le=500,
        description="Maximum length of generated code"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature (higher = more creative)"
    )
    
    @validator('prompt')
    def validate_prompt(cls, v):
        """Validate prompt is not empty after stripping"""
        if not v.strip():
            raise ValueError("Prompt cannot be empty")
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "prompt": "create a function to reverse a string",
                "max_length": 150,
                "temperature": 0.7
            }
        }

class CodeResponse(BaseModel):
    """Response schema for code generation"""
    code: str = Field(
        ...,
        description="Generated Python code"
    )
    latency: float = Field(
        ...,
        description="Generation time in seconds"
    )
    timestamp: str = Field(
        ...,
        description="Generation timestamp (ISO format)"
    )
    prompt: Optional[str] = Field(
        None,
        description="Original prompt (echo)"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "code": "def reverse_string(s):\n    return s[::-1]",
                "latency": 0.345,
                "timestamp": "2025-01-15T10:30:00.000Z",
                "prompt": "create a function to reverse a string"
            }
        }

class HealthResponse(BaseModel):
    """Health check response schema"""
    status: str = Field(
        ...,
        description="Service status (healthy/unhealthy)"
    )
    model_loaded: bool = Field(
        ...,
        description="Whether the model is loaded"
    )
    timestamp: str = Field(
        ...,
        description="Health check timestamp (ISO format)"
    )
    version: str = Field(
        ...,
        description="API version"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if unhealthy"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "model_loaded": True,
                "timestamp": "2025-01-15T10:30:00.000Z",
                "version": "1.0.0"
            }
        }

class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str = Field(
        ...,
        description="Error message"
    )
    status_code: int = Field(
        ...,
        description="HTTP status code"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Error timestamp"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "detail": "Model not loaded",
                "status_code": 503,
                "timestamp": "2025-01-15T10:30:00.000Z"
            }
        }
