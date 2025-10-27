# 시스템 아키텍처

## 시스템 아키텍처

```mermaid
flowchart TB
    subgraph Client["클라이언트 계층"]
        WebBrowser[웹 브라우저]
    end

    subgraph Frontend["프론트엔드 계층"]
        ChatUI[채팅 인터페이스]
        HTTPClient[HTTP 클라이언트]
    end

    subgraph Backend["백엔드 계층"]
        FastAPI[FastAPI 서버<br/>Port: 8000]
        APIEndpoint["/api/chat 엔드포인트"]
        
        subgraph Agent["에이전트 계층"]
            LangGraph[LangGraph<br/>워크플로우 엔진]
            AgentLogic[에이전트 로직]
        end
    end

    subgraph External["외부 서비스"]
        GeminiAPI[Google Gemini API<br/>LLM 서비스]
        ExaAPI[Exa Search API<br/>웹 검색 서비스]
    end

    WebBrowser --> ChatUI
    ChatUI --> HTTPClient
    HTTPClient -->|POST /api/chat| APIEndpoint
    APIEndpoint --> FastAPI
    FastAPI --> LangGraph
    LangGraph --> AgentLogic
    AgentLogic -->|질문 분석| GeminiAPI
    AgentLogic -->|검색 필요시| ExaAPI
    ExaAPI -->|검색 결과| AgentLogic
    AgentLogic -->|응답 생성| GeminiAPI
    GeminiAPI -->|최종 답변| LangGraph
    LangGraph --> FastAPI
    FastAPI --> HTTPClient
    HTTPClient --> ChatUI
    ChatUI --> WebBrowser
```

## 모듈화 및 컴포넌트

```mermaid
flowchart TB
    subgraph FrontendModule["프론트엔드 모듈"]
        UIComponent[UI 컴포넌트]
        MessageHandler[메시지 핸들러]
        APIClient[API 클라이언트]
    end

    subgraph BackendModule["백엔드 모듈"]
        ServerModule[서버 모듈<br/>FastAPI]
        RouterModule[라우터 모듈<br/>/api/chat]
        
        subgraph AgentModule["에이전트 모듈"]
            WorkflowEngine[워크플로우 엔진<br/>LangGraph]
            DecisionNode[의사결정 노드]
            SearchTool[검색 도구]
            LLMInterface[LLM 인터페이스]
        end
        
        ConfigModule[설정 모듈<br/>환경변수 관리]
        ErrorHandler[에러 핸들러]
    end

    subgraph ToolModule["도구 모듈"]
        ExaTool[Exa 검색 도구]
        GeminiTool[Gemini LLM 도구]
    end

    UIComponent --> MessageHandler
    MessageHandler --> APIClient
    APIClient --> RouterModule
    RouterModule --> ServerModule
    ServerModule --> WorkflowEngine
    WorkflowEngine --> DecisionNode
    DecisionNode --> SearchTool
    DecisionNode --> LLMInterface
    SearchTool --> ExaTool
    LLMInterface --> GeminiTool
    ConfigModule -.-> ServerModule
    ConfigModule -.-> ExaTool
    ConfigModule -.-> GeminiTool
    ErrorHandler -.-> ServerModule
    ErrorHandler -.-> WorkflowEngine
```

## API 및 인터페이스

```mermaid
sequenceDiagram
    participant User as 사용자
    participant UI as 채팅 UI
    participant API as FastAPI<br/>/api/chat
    participant Agent as LangGraph<br/>Agent
    participant LLM as Gemini LLM
    participant Search as Exa Search

    User->>UI: 질문 입력 및 전송
    UI->>API: POST /api/chat<br/>{message: "질문"}
    
    API->>Agent: 워크플로우 시작
    Agent->>LLM: 질문 분석 요청
    
    alt 검색 필요
        LLM-->>Agent: tool_call: search
        Agent->>Search: 검색 쿼리 실행
        Search-->>Agent: 검색 결과 반환
        Agent->>LLM: 검색 결과 + 질문
        LLM-->>Agent: 최종 응답
    else 검색 불필요
        LLM-->>Agent: 직접 응답
    end
    
    Agent-->>API: 응답 완료
    API-->>UI: {response: "답변"}
    UI-->>User: 답변 표시
```

### API 명세

```mermaid
flowchart LR
    subgraph Request["요청"]
        ReqMethod[Method: POST]
        ReqEndpoint[Endpoint: /api/chat]
        ReqBody[Body:<br/>{<br/> message: string<br/>}]
    end

    subgraph Response["응답"]
        ResStatus[Status: 200 OK]
        ResBody[Body:<br/>{<br/> response: string<br/>}]
    end

    subgraph ErrorResponse["에러 응답"]
        ErrStatus[Status: 500]
        ErrBody[Body:<br/>{<br/> detail: string<br/>}]
    end

    Request --> Response
    Request -.-> ErrorResponse
```

## 시스템 외부 환경과의 관계

```mermaid
flowchart TB
    subgraph System["웹검색 챗봇 시스템"]
        Frontend[프론트엔드<br/>HTML/CSS/JS]
        Backend[백엔드<br/>FastAPI + LangGraph]
    end

    subgraph ExternalServices["외부 API 서비스"]
        Gemini[Google Gemini API<br/>- 질문 분석<br/>- 응답 생성<br/>- 도구 호출 결정]
        Exa[Exa Search API<br/>- 웹 검색<br/>- 실시간 정보 수집]
    end

    subgraph Environment["실행 환경"]
        EnvVars[환경 변수<br/>.env 파일]
        LocalServer[로컬 서버<br/>Port 8000]
    end

    subgraph UserEnvironment["사용자 환경"]
        Browser[웹 브라우저<br/>Chrome/Firefox/Safari 등]
        Network[네트워크<br/>HTTP/HTTPS]
    end

    subgraph Dependencies["시스템 의존성"]
        Python[Python 3.11]
        Libraries[라이브러리<br/>- FastAPI<br/>- LangGraph<br/>- Exa SDK<br/>- Google AI SDK]
    end

    Browser -->|HTTP 요청| Frontend
    Frontend -->|내부 통신| Backend
    Backend -->|API 호출| Gemini
    Backend -->|API 호출| Exa
    Backend -.->|읽기| EnvVars
    Backend -.->|실행| LocalServer
    Backend -.->|의존| Python
    Backend -.->|의존| Libraries
    Network -.->|연결| Browser
    Network -.->|연결| ExternalServices

    style Gemini fill:#fbbc04
    style Exa fill:#4285f4
    style EnvVars fill:#34a853
    style Python fill:#ea4335
```

### 외부 의존성

```mermaid
mindmap
  root((웹검색 챗봇))
    외부 API
      Google Gemini API
        API 키 필요
        LLM 기능 제공
        도구 호출 지원
      Exa Search API
        API 키 필요
        웹 검색 기능
        실시간 정보
    실행 환경
      Python 3.11
      로컬 서버
        Port 8000
      환경 변수
        EXA_API_KEY
        GEMINI_API_KEY
    시스템 라이브러리
      FastAPI
        웹 서버
      LangGraph
        에이전트 워크플로우
      Exa SDK
        검색 도구
      Google AI SDK
        LLM 연동
    사용자 환경
      웹 브라우저
      인터넷 연결
```

