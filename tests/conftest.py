"""
Pytest configuration and fixtures for FastAPI tests
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for making HTTP requests to the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Reset activities to a clean state before each test.
    Preserves the original activities dict and restores it after the test.
    """
    # Store original state
    original_activities = deepcopy(activities)
    
    # Yield control to the test
    yield
    
    # Restore original state after test
    activities.clear()
    activities.update(original_activities)
