from fastapi import FastAPI,status
from course_app.db.models import Category, UserProfile, Course, RefreshToken
from course_app.db.schema import CategorySchema, UserProfileSchema, CourseSchema
from typing import List, Optional
from course_app.db.database import SessionLocal, engine
from fastapi import Depends, HTTPException

from sqlalchemy.orm import Session
from passlib.context import CryptContext
import redis.asyncio as redis
from contextlib import asynccontextmanager
from fastapi_limiter import FastAPILimiter
from course_app.api.endpoints import auth, courses, category
from sqladmin import Admin, ModelView
from course_app.admin.setup import setup_admin
import uvicorn
from starlette.middleware.sessions import SessionMiddleware
from course_app.config import SECRET_KEY

async def init_redis():
    return redis.from_url('redis://localhost', encoding='utf-8', decode_responses=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = await init_redis()
    await FastAPILimiter.init(redis)
    yield
    await redis.close()


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



course_app = FastAPI(title='Store API', lifespan=lifespan)
course_app.add_middleware(SessionMiddleware, secret_key="SECRET_KEY")
setup_admin(course_app)

admin = Admin(course_app, engine)

course_app.include_router(auth.auth_router)
course_app.include_router(category.category_router)
course_app.include_router(courses.course_router)

# if __name__ == "__main__":
#     uvicorn.run(course_app, host="127.0.0.1", port=80000)