from fastapi import FastAPI
from app.database.db import Base, engine
from app.models import User, Tasks  # registers models with Base before create_all
from app.routers import auth, tasks

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Test Skills API", version="1.0.0")

app.include_router(auth.router)
app.include_router(tasks.router)
