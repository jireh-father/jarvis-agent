"""
LangGraph 에이전트 워크플로우
"""
import os
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from app.services.llm import GeminiLLM
from app.services.search import create_search_tool


class AgentState(TypedDict):
    """에이전트 상태 정의"""
    messages: Annotated[Sequence[BaseMessage], "대화 메시지 리스트"]
    user_query: str
    final_response: str


class AgentError(Exception):
    """에이전트 관련 에러"""
    pass


class LangGraphAgent:
    """LangGraph 에이전트 클래스"""
    
    def __init__(
        self, 
        google_api_key: str = None, 
        exa_api_key: str = None,
        model_name: str = "gemini-2.0-flash-exp"
    ):
        """
        LangGraph 에이전트 초기화
        
        Args:
            google_api_key: Google API 키
            exa_api_key: Exa API 키
            model_name: 사용할 모델 이름
        """
        # API 키 설정
        self.google_api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
        self.exa_api_key = exa_api_key or os.getenv("EXA_API_KEY")
        
        if not self.google_api_key:
            raise ValueError("Google API key is required")
        if not self.exa_api_key:
            raise ValueError("Exa API key is required")
        
        # LLM 초기화
        self.llm_service = GeminiLLM(api_key=self.google_api_key, model_name=model_name)
        self.llm = self.llm_service.llm
        
        # 검색 도구 생성
        self.tools = [create_search_tool(api_key=self.exa_api_key)]
        
        # LLM에 도구 바인딩
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # 워크플로우 생성
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
    
    def _build_workflow(self) -> StateGraph:
        """
        LangGraph 워크플로우 구축
        
        Returns:
            StateGraph 객체
        """
        # StateGraph 정의
        workflow = StateGraph(AgentState)
        
        # 노드 추가
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", ToolNode(self.tools))
        workflow.add_node("generate_response", self._generate_response_node)
        
        # 시작 노드 설정
        workflow.set_entry_point("agent")
        
        # 조건부 엣지 추가 (에이전트 -> 도구 호출 또는 응답 생성)
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": "generate_response"
            }
        )
        
        # 도구 실행 후 다시 에이전트로
        workflow.add_edge("tools", "agent")
        
        # 응답 생성 후 종료
        workflow.add_edge("generate_response", END)
        
        return workflow
    
    def _agent_node(self, state: AgentState) -> AgentState:
        """
        에이전트 노드: LLM에 질문 전달 및 도구 호출 여부 결정
        
        Args:
            state: 현재 상태
            
        Returns:
            업데이트된 상태
        """
        messages = state["messages"]
        
        # LLM 호출
        response = self.llm_with_tools.invoke(messages)
        
        # 메시지 리스트에 응답 추가
        return {
            "messages": messages + [response],
            "user_query": state.get("user_query", ""),
            "final_response": state.get("final_response", "")
        }
    
    def _should_continue(self, state: AgentState) -> str:
        """
        조건부 라우팅 로직: 검색 필요 여부 판단
        
        Args:
            state: 현재 상태
            
        Returns:
            "continue" (도구 호출 필요) 또는 "end" (응답 생성)
        """
        messages = state["messages"]
        last_message = messages[-1]
        
        # 도구 호출이 있으면 continue, 없으면 end
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue"
        return "end"
    
    def _generate_response_node(self, state: AgentState) -> AgentState:
        """
        최종 응답 생성 노드
        
        Args:
            state: 현재 상태
            
        Returns:
            업데이트된 상태 (final_response 포함)
        """
        messages = state["messages"]
        
        # 마지막 메시지에서 응답 추출
        last_message = messages[-1]
        
        if isinstance(last_message, AIMessage):
            final_response = last_message.content
        else:
            final_response = "응답을 생성할 수 없습니다."
        
        return {
            "messages": messages,
            "user_query": state.get("user_query", ""),
            "final_response": final_response
        }
    
    def run(self, user_query: str) -> str:
        """
        에이전트 실행
        
        Args:
            user_query: 사용자 질문
            
        Returns:
            최종 응답
            
        Raises:
            ValueError: 쿼리가 비어있을 때
            AgentError: 에이전트 실행 실패 시
        """
        if not user_query or not user_query.strip():
            raise ValueError("Query cannot be empty")
        
        try:
            # 시스템 프롬프트 설정
            system_prompt = """당신은 도움이 되는 AI 어시스턴트입니다.
            
사용자의 질문에 답변할 때 다음 가이드라인을 따르세요:

1. 최신 정보가 필요한 질문(뉴스, 날씨, 실시간 데이터 등)은 웹 검색 도구를 사용하세요.
2. 일반적인 지식 질문은 직접 답변하세요.
3. 답변은 명확하고 간결하게 작성하세요.
4. 한국어로 답변하세요.
"""
            
            # 초기 상태 설정
            initial_state = {
                "messages": [
                    HumanMessage(content=system_prompt),
                    HumanMessage(content=user_query)
                ],
                "user_query": user_query,
                "final_response": ""
            }
            
            # 워크플로우 실행
            result = self.app.invoke(initial_state)
            
            return result.get("final_response", "응답을 생성할 수 없습니다.")
            
        except ValueError as e:
            raise e
        except Exception as e:
            raise AgentError(f"Failed to run agent: {str(e)}")


def create_agent(
    google_api_key: str = None, 
    exa_api_key: str = None,
    model_name: str = "gemini-2.0-flash-exp"
) -> LangGraphAgent:
    """
    LangGraph 에이전트 생성 헬퍼 함수
    
    Args:
        google_api_key: Google API 키
        exa_api_key: Exa API 키
        model_name: 사용할 모델 이름
        
    Returns:
        LangGraphAgent 인스턴스
    """
    return LangGraphAgent(
        google_api_key=google_api_key,
        exa_api_key=exa_api_key,
        model_name=model_name
    )

