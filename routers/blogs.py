from fastapi import APIRouter, Depends, HTTPException, status, Path, Request
from typing import Annotated, Optional
from models import Blog, Users
from sqlalchemy.orm import Session
from database import SectionLocal
from pydantic import BaseModel, Field
from .auth import get_current_user
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc

router = APIRouter(
    prefix="/blogs",
    tags=["blogs"]
)

def get_db():
    db = SectionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
templates = Jinja2Templates(directory="templates")

class BlogRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    summary: Optional[str] = None
    content: str = Field(..., min_length=1)
    published: Optional[bool] = False

def redirect_to_login():
    redirect_response = RedirectResponse("/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response

# Render logged-in user's blogs
@router.get("/myblog-page")
async def render_todo_page(request: Request, db: db_dependency):
    try: 
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()

        blogs = db.query(Blog).filter(Blog.author_id == user.get("id")).order_by(desc(Blog.created_at)).all()
        return templates.TemplateResponse("blog.html", {"request": request, "blogs": blogs, "user": user})
    except:
        return redirect_to_login()

# Render all blogs except current user
@router.get("/other-blogs")
async def get_all_blogs(request: Request, db: db_dependency):
    try:
        token = request.cookies.get("access_token")
        user = None

        if not token:
           
            blogs = db.query(Blog).filter(Blog.published == True).order_by(desc(Blog.created_at)).all()
        else:
            user = await get_current_user(token)
            if user is None:
               
                blogs = db.query(Blog).filter(Blog.published == True).order_by(desc(Blog.created_at)).all()
            else:
                blogs = db.query(Blog).filter(Blog.author_id != user.get("id") and Blog.published == True).order_by(desc(Blog.created_at)).all()

        return templates.TemplateResponse("all-blogs.html", {
            "request": request,
            "blogs": blogs,
            "user": user 
        })
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": str(e)
        })

# Single blog by any user
@router.get("/other-blog/{id}")
async def get_single_blog(id: int, request: Request, db: db_dependency):
    try:
        token = request.cookies.get("access_token")
        user = None

        blog = db.query(Blog).filter(Blog.id == id).first()
        if not blog:
            raise HTTPException(status_code=404, detail="Blog not found")

        author = db.query(Users).filter(Users.id == blog.author_id).first()

        if token:
            user = await get_current_user(token)

        return templates.TemplateResponse("all-single-blogs.html", {
            "request": request,
            "blog": blog,
            "author": author,
            "user": user
        })
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": f"Error retrieving blog: {str(e)}"
        })

# Single blog by logged-in user
@router.get("/blog/{blog_id}")
async def render_single_blog(request: Request, blog_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()

        blog = db.query(Blog).filter(Blog.id == blog_id, Blog.author_id == user.get("id")).first()

        if blog is None:
            return templates.TemplateResponse("blog.html", {
                "request": request,
                "blogs": db.query(Blog).filter(Blog.author_id == user.get("id")).order_by(desc(Blog.created_at)).all(),
                "user": user
            })

        return templates.TemplateResponse("single-blog.html", {
            "request": request,
            "blog": blog,
            "user": user
        })
    except Exception as e:
        print("Error in full blog route:", e)
        return redirect_to_login()

# Add blog page
@router.get('/add-blog-page')
async def render_add_blog(request: Request):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse("add-blog.html", {"request": request, "user": user})
    except:
        return redirect_to_login()

# Edit blog page
@router.get("/edit-blog-page/{blog_id}")
async def render_edit_blog(request: Request, blog_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()

        blog = db.query(Blog).filter(Blog.id == blog_id).first()
        return templates.TemplateResponse("edit-blog.html", {"request": request, "blog": blog, "user": user})
    except:
        return redirect_to_login()

# API: Get all blogs of user (JSON)
@router.get("/", status_code=status.HTTP_200_OK)
async def Read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")
    return db.query(Blog).filter(Blog.author_id == user.get("id")).order_by(desc(Blog.created_at)).all()

# API: Get single blog of user (JSON)
@router.get("/blog/{blog_id}", status_code=status.HTTP_200_OK)
async def read_blog(user: user_dependency, db: db_dependency, blog_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")

    blog_model = db.query(Blog).filter(Blog.id == blog_id).filter(Blog.author_id == user.get("id")).first()
    if blog_model is not None:
        return blog_model
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")

# Create blog
@router.post("/blog", status_code=status.HTTP_201_CREATED)
async def create_blog(user: user_dependency, db: db_dependency, blog_request: BlogRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")

    blog_model = Blog(**blog_request.dict(), author_id=user.get("id"))
    db.add(blog_model)
    db.commit()

# Update blog
@router.put("/blog/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_blog(user: user_dependency, db: db_dependency, blog_request: BlogRequest, blog_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")

    blog_model = db.query(Blog).filter(Blog.id == blog_id).filter(Blog.author_id == user.get("id")).first()
    if blog_model is None:
        raise HTTPException(status_code=404, detail="Blog not found")

    blog_model.title = blog_request.title
    blog_model.summary = blog_request.summary
    blog_model.content = blog_request.content
    blog_model.published = blog_request.published
    db.commit()

# Delete blog
@router.delete("/blog/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blog(user: user_dependency, db: db_dependency, blog_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")

    blog_model = db.query(Blog).filter(Blog.id == blog_id).filter(Blog.author_id == user.get("id")).first()
    if blog_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")

    db.delete(blog_model)
    db.commit()

# Public API: Get single blog by ID
@router.get("/all-single-blogs/{id}")
async def get_single_blog(id: int, db: db_dependency):
    try:
        blog = db.query(Blog).filter(Blog.id == id).first()
        if not blog:
            raise HTTPException(status_code=404, detail="Blog not found")
        return blog
    except Exception as e:
        print(f"Error fetching blog with id {id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
