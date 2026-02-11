from fastapi import FastAPI
from backend.app.db.base import Base
from backend.app.db.session import engine
from backend.app.models.product import Product
from backend.app.api import products
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from backend.app.db.session import SessionLocal
from backend.app.models.product import Product
from backend.app.api import voice
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory="backend/app/frontend/static"),
    name="static"
)

Base.metadata.create_all(bind=engine)

app.include_router(products.router, prefix="/api")
app.include_router(voice.router)

@app.get("/")
def root():
    return {"message": "Backend is running"}

@app.get("/ui", response_class=HTMLResponse)
def frontend(request: Request):
    db = SessionLocal()
    products = db.query(Product).all()
    db.close()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "products": products
        }
    )

templates = Jinja2Templates(directory="backend/app/frontend/templates")