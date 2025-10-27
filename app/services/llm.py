"""
Gemini LLM 서비스
"""
import os
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI


class LLMError(Exception):
    """LLM 관련 에러"""
    pass


class GeminiLLM:
    """Gemini LLM 클래스"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        """
        Gemini LLM 초기화
        
        Args:
            api_key: Google API 키 (None인 경우 환경 변수에서 가져옴)
            model_name: 사용할 모델 이름 (기본값: gemini-2.5-flash)
        
        Raises:
            ValueError: API 키가 제공되지 않았을 때
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError("API key is required. Provide api_key parameter or set GOOGLE_API_KEY environment variable.")
        
        self.model_name = model_name
        
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.api_key,
                temperature=0.7,
                max_output_tokens=2048
            )
        except Exception as e:
            raise LLMError(f"Failed to initialize Gemini LLM: {str(e)}")
    
    def generate_text(self, prompt: str) -> str:
        """
        텍스트 생성
        
        Args:
            prompt: 입력 프롬프트
            
        Returns:
            생성된 텍스트
            
        Raises:
            ValueError: 프롬프트가 비어있을 때
            LLMError: API 호출 실패 시
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            raise LLMError(f"Failed to generate text: {str(e)}")

