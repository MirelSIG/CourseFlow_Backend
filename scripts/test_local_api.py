"""
Script to test CourseFlow API endpoints locally
"""
import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, "/Users/mirelvolcan/CourseFlow")

# Mock environment for testing
os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.main import app
from app.api.deps import get_db

# Create in-memory SQLite database
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_endpoints():
    """Test main endpoints"""
    print("Testing CourseFlow API Endpoints\n" + "="*50)
    
    # Test health check (GET /courses)
    print("\n1. GET /api/v1/courses (Health Check)")
    response = client.get("/api/v1/courses/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    # Test register user
    print("\n2. POST /api/v1/users (Register User)")
    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User",
        "role": "user"
    }
    response = client.post("/api/v1/users/", json=user_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    user_id = response.json().get("id")
    
    # Test login
    print("\n3. POST /api/v1/auth/login (Login)")
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    token = response.json().get("access_token")
    
    # Test create course
    print("\n4. POST /api/v1/courses (Create Course)")
    course_data = {
        "name": "Python Advanced",
        "description": "Advanced Python course",
        "start_date": "2026-06-01",
        "end_date": "2026-07-01",
        "capacity": 30
    }
    response = client.post("/api/v1/courses/", json=course_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    course_id = response.json().get("id")
    
    # Test list courses
    print("\n5. GET /api/v1/courses (List Courses)")
    response = client.get("/api/v1/courses/")
    print(f"   Status: {response.status_code}")
    print(f"   Response count: {len(response.json())}")
    assert response.status_code == 200
    
    # Test create application
    print("\n6. POST /api/v1/applications (Create Application)")
    app_data = {"user_id": user_id, "course_id": course_id}
    response = client.post("/api/v1/applications/", json=app_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    
    # Test list applications
    print("\n7. GET /api/v1/applications (List Applications)")
    response = client.get("/api/v1/applications/")
    print(f"   Status: {response.status_code}")
    print(f"   Response count: {len(response.json())}")
    assert response.status_code == 200
    
    print("\n" + "="*50)
    print("✅ All tests passed!")

if __name__ == "__main__":
    test_endpoints()
