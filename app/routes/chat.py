"""
채팅 라우터
"""
import os
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
from app.models.schemas import ChatRequest, ChatResponse
from app.services.llm import GeminiLLM, LLMError

# 환경 변수 로드
load_dotenv()

router = APIRouter(prefix="/api", tags=["chat"])

# Gemini LLM 인스턴스 초기화
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")
    gemini_llm = GeminiLLM(api_key=api_key)
except Exception as e:
    print(f"Warning: Failed to initialize Gemini LLM: {e}")
    gemini_llm = None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    채팅 엔드포인트
    Gemini LLM을 사용하여 응답을 생성합니다.
    """
    # Gemini LLM이 초기화되지 않은 경우
    if gemini_llm is None:
        raise HTTPException(
            status_code=500,
            detail="LLM service is not available. Please check GOOGLE_API_KEY environment variable."
        )
    
    try:
        # Gemini LLM을 사용하여 응답 생성
        response_text = gemini_llm.generate_text(request.message)
        return ChatResponse(response=response_text)
    
    except ValueError as e:
        # 입력 검증 오류
        raise HTTPException(status_code=400, detail=str(e))
    
    except LLMError as e:
        # LLM API 호출 오류
        raise HTTPException(status_code=500, detail=f"LLM service error: {str(e)}")
    
    except Exception as e:
        # 기타 예상치 못한 오류
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

