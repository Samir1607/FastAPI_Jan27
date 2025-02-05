from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder
from database import Session
from schemas import SignUpModel, LoginModel
from pizza_models import User

auth_router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

session = Session()

@auth_router.get('/')
async def hello(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return {"message": "This is auth routers"}

@auth_router.post('/signup', response_model=SignUpModel, status_code=status.HTTP_201_CREATED)
async def signup(user: SignUpModel):
    db_email = session.query(User).filter(User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")
    
    new_user = User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password),
        is_active=user.is_active,
        is_staff=user.is_staff
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return jsonable_encoder(new_user)

@auth_router.post('/login', status_code=status.HTTP_200_OK)
async def login(user: LoginModel, Authorize: AuthJWT = Depends()):
    db_user = session.query(User).filter(User.username == user.username).first()
    if db_user and check_password_hash(db_user.password, user.password):
        access_token = Authorize.create_access_token(subject=db_user.username)
        refresh_token = Authorize.create_refresh_token(subject=db_user.username)
        return jsonable_encoder({"access": access_token, "refresh": refresh_token})
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")

@auth_router.get('/refresh')
async def refresh_token(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required(refresh=True)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    current_user = Authorize.get_jwt_subject()
    access_token = Authorize.create_access_token(subject=current_user)

    return jsonable_encoder({'access': access_token})
