"""
Pytest configuration and fixtures
"""
import pytest
from unittest.mock import Mock


@pytest.fixture(scope="session")
def mock_model():
    """Create a mock model for testing"""
    model = Mock()
    model.is_loaded.return_value = True
    model.generate.return_value = "def example_function(x, y):\n    return x + y"
    model.get_model_info.return_value = {
        "loaded": True,
        "device": "cpu",
        "backend": "PyTorch",
        "model_type": "T5ForConditionalGeneration",
        "model_path": "./models",
        "parameters": "220.34M"
    }
    return model


@pytest.fixture
def client(mock_model):
    """Create test client with mocked model"""
    # Import app modules
    from fastapi.testclient import TestClient
    from app import main
    
    # Directly set the global code_generator to our mock
    main.code_generator = mock_model
    
    # Create test client
    return TestClient(main.app)

