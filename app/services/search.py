"""
Exa Search 서비스
"""
import os
from typing import Optional, List, Dict, Any
from exa_py import Exa
from langchain_core.tools import Tool


class SearchError(Exception):
    """검색 관련 에러"""
    pass


class ExaSearch:
    """Exa Search 클래스"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Exa Search 초기화
        
        Args:
            api_key: Exa API 키 (None인 경우 환경 변수에서 가져옴)
        
        Raises:
            ValueError: API 키가 제공되지 않았을 때
        """
        self.api_key = api_key or os.getenv("EXA_API_KEY")
        
        if not self.api_key:
            raise ValueError("API key is required. Provide api_key parameter or set EXA_API_KEY environment variable.")
        
        try:
            self.client = Exa(api_key=self.api_key)
        except Exception as e:
            raise SearchError(f"Failed to initialize Exa Search: {str(e)}")
    
    def search(
        self, 
        query: str, 
        num_results: int = 5,
        use_autoprompt: bool = True,
        text_contents_options: bool = True
    ) -> List[Dict[str, Any]]:
        """
        웹 검색 수행
        
        Args:
            query: 검색 쿼리
            num_results: 반환할 검색 결과 수 (기본값: 5)
            use_autoprompt: Exa의 자동 프롬프트 최적화 사용 여부 (기본값: True)
            text_contents_options: 텍스트 콘텐츠 포함 여부 (기본값: True)
            
        Returns:
            검색 결과 리스트 (각 결과는 dict 형태)
            
        Raises:
            ValueError: 쿼리가 비어있을 때
            SearchError: API 호출 실패 시
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        try:
            # Exa Search API 호출
            search_response = self.client.search_and_contents(
                query=query,
                num_results=num_results,
                use_autoprompt=use_autoprompt,
                text={"max_characters": 1000} if text_contents_options else False
            )
            
            # 검색 결과 파싱 및 포맷팅
            results = self._format_results(search_response)
            
            return results
            
        except ValueError as e:
            # ValueError는 그대로 전달
            raise e
        except Exception as e:
            raise SearchError(f"Failed to search: {str(e)}")
    
    def _format_results(self, search_response) -> List[Dict[str, Any]]:
        """
        검색 결과 파싱 및 포맷팅
        
        Args:
            search_response: Exa API 응답 객체
            
        Returns:
            포맷팅된 검색 결과 리스트
        """
        formatted_results = []
        
        if not hasattr(search_response, 'results'):
            return formatted_results
        
        for result in search_response.results:
            formatted_result = {
                "title": getattr(result, 'title', 'No title'),
                "url": getattr(result, 'url', ''),
                "text": getattr(result, 'text', '')[:500] if hasattr(result, 'text') else '',  # 500자로 제한
                "score": getattr(result, 'score', 0.0),
                "published_date": getattr(result, 'published_date', None)
            }
            formatted_results.append(formatted_result)
        
        return formatted_results
    
    def format_results_for_llm(self, results: List[Dict[str, Any]]) -> str:
        """
        검색 결과를 LLM에 전달할 수 있는 텍스트 형식으로 포맷팅
        
        Args:
            results: 검색 결과 리스트
            
        Returns:
            포맷팅된 텍스트
        """
        if not results:
            return "검색 결과가 없습니다."
        
        formatted_text = "검색 결과:\n\n"
        
        for i, result in enumerate(results, 1):
            formatted_text += f"{i}. {result['title']}\n"
            formatted_text += f"   URL: {result['url']}\n"
            if result['text']:
                formatted_text += f"   내용: {result['text']}\n"
            formatted_text += "\n"
        
        return formatted_text


def create_search_tool(api_key: Optional[str] = None) -> Tool:
    """
    Exa Search를 LangChain Tool 형식으로 생성
    
    Args:
        api_key: Exa API 키 (None인 경우 환경 변수에서 가져옴)
        
    Returns:
        LangChain Tool 객체
    """
    search_instance = ExaSearch(api_key=api_key)
    
    def search_wrapper(query: str) -> str:
        """
        검색 래퍼 함수
        
        Args:
            query: 검색 쿼리
            
        Returns:
            포맷팅된 검색 결과 텍스트
        """
        try:
            results = search_instance.search(query=query, num_results=5)
            return search_instance.format_results_for_llm(results)
        except Exception as e:
            return f"검색 중 오류가 발생했습니다: {str(e)}"
    
    return Tool(
        name="web_search",
        description="웹에서 최신 정보를 검색할 때 사용합니다. 실시간 정보, 뉴스, 날씨, 이벤트 등이 필요할 때 유용합니다.",
        func=search_wrapper
    )

