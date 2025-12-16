from fastapi import APIRouter, HTTPException, status, Depends
from fastapi_limiter.depends import RateLimiter
from jose import jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from course_app.db.database import SessionLocal
from typing import Optional
from course_app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from course_app.db.schema import UserProfileSchema
from course_app.db.models import UserProfile, RefreshToken
from sqlalchemy.orm import Session



auth_router = APIRouter(prefix='/auth', tags=['Auth'])

oauth_schema2 = OAuth2PasswordBearer(tokenUrl='/auth/login/')
password_context = CryptContext(schemes=['bcrypt'], deprecated="auto")


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict, expire_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    exp_schema = datetime.utcnow() + (expire_delta if expire_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({'exp': exp_schema})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data:dict):
    return create_access_token(data, expire_delta=timedelta(REFRESH_TOKEN_EXPIRE_DAYS))

def verify_password(plain_password, hashed_password):
    return password_context.verify(plain_password, hashed_password)

def get_hash_password(password):
    return password_context.hash(password)

@auth_router.post('/register', response_model=UserProfileSchema)
async def register_user(user:UserProfileSchema, db: Session = Depends(get_db)):
    db_user = db.query(UserProfile).filter(UserProfile.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=404, detail='Mynday adam bar')
    new_hash_password = get_hash_password(user.password)
    new_user = UserProfile(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        age=user.age,
        phone_number=user.phone_number,
        profile_picture=user.profile_picture,
        role=user.role,
        hashed_password=new_hash_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {'success': '200 ok'}


@auth_router.post('/login/', dependencies=[Depends(RateLimiter(times=3,seconds=30))])
async def login_user(form_data:OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserProfile).filter(UserProfile.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Tuura emes maalymat')
    access_token = create_access_token({'sub': user.username})
    refresh_token = create_refresh_token({'sub': user.username})
    token_db = RefreshToken(token=refresh_token, user_id=user.id)
    db.add(token_db)
    db.commit()
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


@auth_router.post('/logout')
async def logout_user(refresh_token:str, db: Session = Depends(get_db)):
    token_db = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if not token_db:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Tuura emes maalymat')
    db.delete(token_db)
    db.commit()
    return {'message': 'Вышли'}


@auth_router.post('/refresh')
async def refresh(refresh_token: str, db: Session = Depends(get_db)):
    token_entry = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if not token_entry:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Tuura emes maalymat')
    new_access =create_access_token({'sub': token_entry.user_id})
    return {'access': new_access, 'token_type': 'bearer'}



