"""
Pytest configuration and fixtures
"""
import pytest
import sys
from unittest.mock import Mock, patch, MagicMock

# Mock TensorFlow to prevent import issues on unsupported CPUs
sys.modules['tensorflow'] = MagicMock()


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


@pytest.fixture(scope="session", autouse=True)
def setup_mocks(mock_model):
    """Set up all mocks before any imports"""
    # Patch before importing app
    with patch("app.model.T5CodeGenerator") as mock_class:
        mock_class.return_value = mock_model
        
        # Now import and patch the app
        from app import main
        main.code_generator = mock_model
        
        yield


@pytest.fixture
def client():
    """Create test client"""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)

