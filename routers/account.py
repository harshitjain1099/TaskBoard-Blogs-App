from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from models import Users
from database import SectionLocal
from .auth import get_current_user, bcrypt_context 
from jose import JWTError

router = APIRouter(
    prefix="/account",
    tags=["account"]
)

templates = Jinja2Templates(directory="templates")

def get_db():
    db = SectionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


async def get_user_from_cookie(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        user_data = await get_current_user(token)
        user = db.query(Users).filter(Users.id == user_data["id"]).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")








def redirect_to_login():
    return RedirectResponse(url="/auth/login-page", status_code=status.HTTP_303_SEE_OTHER)







@router.get("/my-account")
async def my_account_page(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return redirect_to_login()
    try:
        user_data = await get_current_user(token)
        user = db.query(Users).filter(Users.id == user_data.get("id")).first()
        if not user:
            return redirect_to_login()
        return templates.TemplateResponse("account.html", {"request": request, "user": user})
    except Exception:
        return redirect_to_login()









@router.get("/my-account/edit", response_class=HTMLResponse)
async def edit_account_form(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return redirect_to_login()
    user_data = await get_current_user(token)
    db_user = db.query(Users).filter(Users.id == user_data.get("id")).first()
    if not db_user:
        return redirect_to_login()
    return templates.TemplateResponse("edit_account.html", {"request": request, "user": db_user})









@router.post("/my-account/edit")
async def update_account_details(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    role: str = Form(...),
    phone_number: str = Form(...),
    db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")
    if not token:
        return redirect_to_login()
    user_data = await get_current_user(token)
    db_user = db.query(Users).filter(Users.id == user_data.get("id")).first()
    if not db_user:
        return redirect_to_login()

    db_user.username = username
    db_user.email = email
    db_user.first_name = first_name
    db_user.last_name = last_name
    db_user.role = role
    db_user.phone_number = phone_number
    db.commit()
    return RedirectResponse(url="/account/my-account", status_code=status.HTTP_303_SEE_OTHER)








@router.get("/my-account/change-password")
async def change_password_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return redirect_to_login()
    user = await get_current_user(token)
    return templates.TemplateResponse("change_password.html", {"request": request, "user": user})








@router.post("/my-account/change-password")
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")
    if not token:
        return redirect_to_login()
    user = await get_current_user(token)
    db_user = db.query(Users).filter(Users.id == user["id"]).first()

    if not bcrypt_context.verify(current_password, db_user.hashed_password):
        return templates.TemplateResponse("change_password.html", {
            "request": request,
            "error": "Current password is incorrect",
            "user": user
        })

    if new_password != confirm_password:
        return templates.TemplateResponse("change_password.html", {
            "request": request,
            "error": "New passwords do not match",
            "user": user
        })

    db_user.hashed_password = bcrypt_context.hash(new_password)
    db.commit()

    return templates.TemplateResponse("change_password.html", {
        "request": request,
        "message": "Password successfully changed",
        "user": user
    })
