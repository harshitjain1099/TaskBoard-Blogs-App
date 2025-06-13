from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from .auth import get_current_user
from langchain_community.tools import DuckDuckGoSearchRun
from typing import Annotated
from sqlalchemy.orm import Session
from database import SectionLocal



router = APIRouter(
    prefix="/agent",
    tags=["agent"]
)



def get_db():
    db = SectionLocal()
    try:
        yield db
    finally:
        db.close()



db_dependency = Annotated[Session, Depends(get_db)]
templates = Jinja2Templates(directory="templates")
search_tool = DuckDuckGoSearchRun()





@router.get("/ai-search-page")
async def render_ai_agent(request: Request):
    user = await get_current_user(request.cookies.get("access_token"))
    if user is None:
        
        return templates.TemplateResponse("home.html", {"request": request})
    
    return templates.TemplateResponse("ai-agent.html", {"request": request, "user": user})



@router.post("/agent-search")
async def ai_search(request: Request, query: str = Form(...)):
    user = await get_current_user(request.cookies.get("access_token"))
    if user is None:
        
        return templates.TemplateResponse("home.html", {"request": request})
    
    
    result = search_tool.invoke(query)
    return templates.TemplateResponse("ai-agent.html", {
        "request": request,
        "query": query,
        "result": result,
        "user": user
    })
