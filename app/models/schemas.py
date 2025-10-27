"""
데이터 모델 스키마
"""
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """채팅 요청 스키마"""
    message: str = Field(..., min_length=1, description="사용자 메시지")


class ChatResponse(BaseModel):
    """채팅 응답 스키마"""
    response: str = Field(..., description="에이전트 응답")

