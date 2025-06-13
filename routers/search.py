from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from typing import Annotated, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from models import Blog, Users
from database import SectionLocal
from .auth import get_current_user



router = APIRouter(
    prefix="/search",
    tags=["search"]
)

class Item(BaseModel):
    id: int
    name: str


def get_db():
    db = SectionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


user_dependency = Annotated[dict, Depends(get_current_user)]

templates = Jinja2Templates(directory="templates")



@router.get("/")
async def search_blogs(
    request: Request,
    db: db_dependency,
    query: Optional[str] = Query(None, description="Search query string"),
):
    try:
        token = request.cookies.get("access_token")
        print("Token:", token)  

        user = None
        if token:
            user = await get_current_user(token)
            print("User:", user)  

        if not query or not query.strip():
            if user:
                blogs = db.query(Blog).all()
            else:
                blogs = db.query(Blog).all()
        else:
            if user:
                blogs = (
                    db.query(Blog)
                    .filter(Blog.title.ilike(f"%{query.strip()}%"))
                    .limit(50)
                    .all()
                )
            else:
                blogs = (
                    db.query(Blog)
                    .filter(Blog.title.ilike(f"%{query.strip()}%"))
                    .limit(50)
                    .all()
                )
        print(f"Found {len(blogs)} blogs")

        return templates.TemplateResponse(
            "search.html",
            {
                "request": request,
                "blogs": blogs,
                "query": query,
                "user": user,
            },
        )
    except Exception as e:
        print("Error:", e)
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": f"Error during blog search: {str(e)}",
            },
        )




# Search endpoint
@router.get("/search")
def search_blogs(db:db_dependency, query: str):
    blogs = db.query(Blog).filter(Blog.title.ilike(f"%{query}%")).all()
    return [{"title": b.title,"summary": b.summary, "content": b.content} for b in blogs]
