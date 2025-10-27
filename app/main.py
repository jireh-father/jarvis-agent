"""
Jarvis 챗봇 에이전트 메인 서버
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

# FastAPI 앱 생성
app = FastAPI(
    title="Jarvis Chat Agent",
    description="웹 검색 기능을 가진 AI 챗봇 에이전트",
    version="1.0.0"
)

# 정적 파일 마운트
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/icons", StaticFiles(directory="icons"), name="icons")

# 템플릿 설정
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """메인 페이지"""
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}


# 라우터 임포트 및 등록
from app.routes import chat
app.include_router(chat.router)

