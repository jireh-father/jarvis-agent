"""
채팅 라우터
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    채팅 엔드포인트
    현재는 더미 응답을 반환합니다.
    """
    # 더미 응답 생성
    dummy_responses = [
        "안녕하세요! 저는 Jarvis입니다. 무엇을 도와드릴까요?",
        "네, 알겠습니다. 더 자세히 말씀해 주시겠어요?",
        "흥미로운 질문이네요! 제가 검색해보고 답변드리겠습니다.",
        "그에 대한 정보를 찾았습니다. 요약해드리겠습니다.",
    ]
    
    # 메시지 길이에 따라 다른 더미 응답 반환
    response_index = len(request.message) % len(dummy_responses)
    
    return ChatResponse(response=dummy_responses[response_index])

