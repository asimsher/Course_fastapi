from course_app.db.models import Category
from course_app.db.schema import CategorySchema
from course_app.db.database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, APIRouter
from typing import Optional, List



category_router = APIRouter(prefix='/category', tags=['Categories'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@category_router.post('/category/create', response_model=CategorySchema)
async def create_category(category: CategorySchema, db: Session = Depends(get_db)):
    db_category = Category(category_name=category.category_name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@category_router.get('/', response_model=List[CategorySchema])
async def list_category(db: Session = Depends(get_db)):
    db_category = db.query(Category).all()
    return db_category



@category_router.get('/', response_model=CategorySchema)
async def derail_category(category_id: int, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail='Mynday maalymat jok')
    return db_category


@category_router.put('/')
async def put_category(category_id:int, date_category:CategorySchema, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    db_category.category_name = date_category.category_name
    db.commit()
    db.refresh()
    return db_category


@category_router.delete('/{category_id}')
async def deleted_category(category_id:int, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail='Mynday ID jok')
    db.delete(db_category)
    db.commit()
    return {'deleted 200 ok'}

