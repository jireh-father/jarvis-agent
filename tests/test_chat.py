"""
채팅 엔드포인트 테스트
"""
import pytest
from fastapi.testclient import TestClient


def test_chat_endpoint_exists():
    """채팅 엔드포인트 존재 확인"""
    from app.main import app
    client = TestClient(app)
    
    response = client.post("/api/chat", json={"message": "테스트 메시지"})
    assert response.status_code == 200


def test_chat_endpoint_returns_response():
    """채팅 엔드포인트가 응답을 반환하는지 확인"""
    from app.main import app
    client = TestClient(app)
    
    response = client.post("/api/chat", json={"message": "안녕하세요"})
    assert response.status_code == 200
    
    data = response.json()
    assert "response" in data
    assert isinstance(data["response"], str)
    assert len(data["response"]) > 0


def test_chat_endpoint_with_empty_message():
    """빈 메시지로 요청 시 에러 처리"""
    from app.main import app
    client = TestClient(app)
    
    response = client.post("/api/chat", json={"message": ""})
    # 빈 메시지는 Pydantic validation error
    assert response.status_code == 422


def test_chat_endpoint_invalid_request():
    """잘못된 요청 처리"""
    from app.main import app
    client = TestClient(app)
    
    response = client.post("/api/chat", json={})
    assert response.status_code == 422  # Validation error

