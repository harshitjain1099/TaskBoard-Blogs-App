from fastapi import FastAPI,Request, status
import models
from database import engine
from routers import auth,todos,admin,user,blogs,support,search,account,agent
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from routers import agent
app = FastAPI()

models.Base.metadata.create_all(bind = engine)

app.mount("/static", StaticFiles(directory= 'static'),name = "static")


@app.get("/")
def test(request : Request):
    return RedirectResponse(url="/todos/home", status_code=status.HTTP_302_FOUND)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(user.router)
app.include_router(blogs.router)
app.include_router(support.router)
app.include_router(search.router)
app.include_router(account.router)
app.include_router(agent.router)



