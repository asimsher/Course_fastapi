from course_app.db.models import Course
from course_app.db.schema import CourseSchema
from course_app.db.database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, APIRouter, status
from typing import Optional, List

course_router = APIRouter(prefix='/courses', tags=['Courses'])


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@course_router.post('/', response_model=CourseSchema)
async def create_course(course:CourseSchema, db: Session = Depends(get_db)):
    db_course = Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@course_router.get('/course/', response_model=List[CourseSchema])
async def list_courses(db: Session = Depends(get_db)):
    return db.query(Course).all()

@course_router.get('/', response_model=CourseSchema)
async def detail_courses(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Course not Found')
    return course


@course_router.put('/', response_model=CourseSchema)
async def update_course(course_id: int, course_data: CourseSchema, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Course not Found')

    for course_key, course_value in course_data.dict().items():
        setattr(course, course_key, course_value)

    db.commit()
    db.refresh(course)
    return course

@course_router.delete('/{course_id/')
async def delete_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Course not Found')
    db.delete(course)
    db.commit()
    return {'message': 'This course id deleted'}