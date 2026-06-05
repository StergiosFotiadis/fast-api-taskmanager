from fastapi import FastAPI
from app.database.db import Base, engine
from app.models import User, Tasks, Category  # registers models with Base before create_all
from app.routers import auth, tasks
from app.routers.categories import router as categories_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Test Skills API", version="1.0.0")

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(categories_router)
