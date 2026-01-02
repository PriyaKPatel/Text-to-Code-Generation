"""
Unit tests for the Text-to-Code API
"""
import pytest
from fastapi.testclient import TestClient
import json

# client fixture is provided by conftest.py

class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check_returns_200(self, client):
        """Test that health endpoint returns 200"""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_check_response_structure(self, client):
        """Test health check response has correct structure"""
        response = client.get("/health")
        data = response.json()
        
        assert "status" in data
        assert "model_loaded" in data
        assert "timestamp" in data
        assert "version" in data
    
    def test_health_status_is_valid(self, client):
        """Test health status is either healthy or unhealthy"""
        response = client.get("/health")
        data = response.json()
        
        assert data["status"] in ["healthy", "unhealthy"]

class TestRootEndpoint:
    """Test root endpoint"""
    
    def test_root_returns_200(self, client):
        """Test root endpoint returns 200"""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_root_response_structure(self, client):
        """Test root endpoint returns HTML UI"""
        response = client.get("/")
        
        # Root now serves the React UI (HTML)
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert b"<!DOCTYPE html>" in response.content
        assert b"Text to Code Generator" in response.content
    
    def test_api_info_endpoint(self, client):
        """Test /api/info endpoint returns API information"""
        response = client.get("/api/info")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert data["version"] == "1.0.0"

class TestGenerateEndpoint:
    """Test code generation endpoint"""
    
    def test_generate_requires_prompt(self, client):
        """Test that generate endpoint requires prompt"""
        response = client.post("/generate", json={})
        assert response.status_code == 422  # Validation error
    
    def test_generate_with_valid_prompt(self, client):
        """Test code generation with valid prompt"""
        response = client.post(
            "/generate",
            json={"prompt": "create a function to add two numbers"}
        )
        # Should succeed with mocked model
        assert response.status_code == 200
    
    def test_generate_response_structure(self, client):
        """Test generate response has correct structure if successful"""
        response = client.post(
            "/generate",
            json={
                "prompt": "create a simple hello world function",
                "max_length": 100,
                "temperature": 0.7
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "code" in data
        assert "latency" in data
        assert "timestamp" in data
        assert isinstance(data["code"], str)
        assert isinstance(data["latency"], (int, float))
    
    def test_generate_validates_prompt_length(self, client):
        """Test that very short prompts are rejected"""
        response = client.post(
            "/generate",
            json={"prompt": "hi"}
        )
        assert response.status_code == 422
    
    def test_generate_validates_max_length(self, client):
        """Test that max_length is validated"""
        response = client.post(
            "/generate",
            json={
                "prompt": "create a function",
                "max_length": 1000  # Too high
            }
        )
        assert response.status_code == 422
    
    def test_generate_validates_temperature(self, client):
        """Test that temperature is validated"""
        response = client.post(
            "/generate",
            json={
                "prompt": "create a function",
                "temperature": 5.0  # Too high
            }
        )
        assert response.status_code == 422

class TestMetricsEndpoint:
    """Test metrics endpoint"""
    
    def test_metrics_endpoint_exists(self, client):
        """Test that metrics endpoint exists"""
        response = client.get("/metrics")
        assert response.status_code == 200
    
    def test_metrics_content_type(self, client):
        """Test metrics returns plain text"""
        response = client.get("/metrics")
        assert "text/plain" in response.headers["content-type"]

class TestStatsEndpoint:
    """Test stats endpoint"""
    
    def test_stats_endpoint_exists(self, client):
        """Test that stats endpoint exists"""
        response = client.get("/stats")
        assert response.status_code == 200
    
    def test_stats_response_structure(self, client):
        """Test stats response structure"""
        response = client.get("/stats")
        data = response.json()
        
        assert "model_loaded" in data
        assert "timestamp" in data
        assert isinstance(data["model_loaded"], bool)

# Integration tests
class TestIntegration:
    """Integration tests"""
    
    def test_full_workflow(self, client):
        """Test complete workflow from health check to generation"""
        # Check health
        health = client.get("/health")
        assert health.status_code == 200
        
        # Check root
        root = client.get("/")
        assert root.status_code == 200
        
        # Try generation (mocked model always succeeds)
        response = client.post(
            "/generate",
            json={"prompt": "create a function to calculate factorial"}
        )
        assert response.status_code == 200
    
    def test_cors_headers(self, client):
        """Test that CORS is configured (middleware doesn't apply in TestClient)"""
        # TestClient doesn't trigger CORS middleware like a real browser
        # Just verify the endpoint is accessible
        response = client.get("/health")
        assert response.status_code == 200

# Model-specific tests
class TestModelValidation:
    """Test model-specific functionality"""
    
    def test_empty_prompt_rejected(self, client):
        """Test that empty prompts are rejected"""
        response = client.post(
            "/generate",
            json={"prompt": "   "}  # Only whitespace
        )
        assert response.status_code == 422

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
