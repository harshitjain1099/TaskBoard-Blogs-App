from fastapi import APIRouter, Depends, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Annotated
from starlette import status

from models import Support
from database import SectionLocal

router = APIRouter(
    prefix="/support",
    tags=["support"]
)

templates = Jinja2Templates(directory="templates")


class SupportRequest(BaseModel):
    full_name: str
    email: str
    subject: str
    message: str


def get_db():
    db = SectionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/contact-submit")
async def contact_submit(
    request: Request,
    db: db_dependency,
    name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...)
):
    try:
        create_support_request = Support(
            full_name=name,
            email=email,
            subject=subject,
            message=message
        )
        db.add(create_support_request)
        db.commit()
        db.refresh(create_support_request)

        # Redirect to home page after success
        return RedirectResponse(url="/todos/home", status_code=status.HTTP_303_SEE_OTHER)


    except Exception as e:
        db.rollback()
      
        return templates.TemplateResponse(
            "contect.html",  
            {
                "request": request,
                "error": f"Error submitting form: {str(e)}",
                "name": name,
                "email": email,
                "subject": subject,
                "message": message,
            },
            status_code=400,
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def support_apply(
    db: db_dependency,
    supportRequest: SupportRequest
):
    try:
        create_support_request = Support(
            full_name=supportRequest.full_name,
            email=supportRequest.email,
            subject=supportRequest.subject,
            message=supportRequest.message
        )
        db.add(create_support_request)
        db.commit()
        db.refresh(create_support_request)
        return {"message": "Support request submitted successfully."}
    except Exception as e:
        db.rollback()
        return {"error": f"Error submitting API support request: {str(e)}"}
