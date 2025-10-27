"""
FastAPI 기본 서버 테스트
"""
import pytest
from fastapi.testclient import TestClient


def test_create_app():
    """앱 생성 테스트"""
    from app.main import app
    assert app is not None
    assert app.title == "Jarvis Chat Agent"


def test_root_endpoint():
    """루트 엔드포인트 테스트"""
    from app.main import app
    client = TestClient(app)
    
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_health_check():
    """헬스 체크 엔드포인트 테스트"""
    from app.main import app
    client = TestClient(app)
    
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

