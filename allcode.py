# auth_routes.py
from fastapi import APIRouter, status, Depends
from database import Session, engine
from schemas import SignUpModel, LoginModel
from pizza_models import User
from fastapi.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder

auth_router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

session = Session(bind=engine)


@auth_router.get('/')
async def hello(Authorize: AuthJWT =Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    return {"message": "This is auth routers"}


@auth_router.post('/signup', response_model=SignUpModel, status_code=status.HTTP_201_CREATED)
async def signup(user: SignUpModel):
    db_email = session.query(User).filter(User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User with the username already exists"
                            )
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


@auth_router.post('/login', status_code=200)
async def login(user: LoginModel, Authorize: AuthJWT = Depends()):
    db_user = session.query(User).filter(User.username == user.username).first()

    if db_user and check_password_hash(db_user.password, user.password):
        access_token = Authorize.create_access_token(subject=db_user.username)
        refresh_token = Authorize.create_refresh_token(subject=db_user.username)

        response = {
            "access": access_token,
            "refresh": refresh_token
        }

        return jsonable_encoder(response)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid Username or Password"
                        )


@auth_router.get('/refresh')
async def refresh_token(Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required(refresh=True)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Please provide valid refresh token'
                            )
    
    current_user=Authorize.get_jwt_subject()

    access_token=Authorize.create_access_token(subject=current_user)

    return jsonable_encoder({'access':access_token})











# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("sqlite:///pizza_delivery.db", echo=True)

Base = declarative_base()


Session = sessionmaker(bind=engine)

# Usage Example
if __name__ == "__main__":
    # Initialize a session
    session = Session()

    # Your application logic goes here

    # Close the session when done
    session.close()










# main.py
import os
from fastapi import FastAPI
from auth_routes import auth_router
from order_routes import order_router
from fastapi_jwt_auth import AuthJWT
from schemas import Settings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app's address
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@AuthJWT.load_config
def get_config():
    
    return Settings()
    
app.include_router(auth_router)
app.include_router(order_router)










# order_routes.py
from fastapi import APIRouter, Depends, status
from fastapi_jwt_auth import AuthJWT
from pizza_models import User, Order
from schemas import OrderModel, OrderStatusModel
from fastapi.exceptions import HTTPException
from database import engine, Session
from fastapi.encoders import jsonable_encoder


order_router = APIRouter(
    prefix='/orders',
    tags=['orders']
)

session = Session(bind=engine)


@order_router.get('/')
async def hello(Autherize:AuthJWT=Depends()):
    try:
        Autherize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    return {"message": "This is order routers"}


@order_router.post("/order", status_code=status.HTTP_201_CREATED)
async def place_an_order(order:OrderModel, Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            details="Invalid Details"
        )
    
    current_user=Authorize.get_jwt_subject()
    user=session.query(User).filter(User.username==current_user).first()

    new_order=Order(
        pizza_size=order.pizza_size,
        quantity=order.quantity
    )

    new_order.user=user

    session.add(new_order)
    session.commit()

    response={
        "pizza_size":new_order.pizza_size,
        "id":new_order.id,
        "quantity":new_order.quantity,
        "order_status":new_order.order_status
    }

    return jsonable_encoder(response)


@order_router.get("/orders")
async def all_orders_list(Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    
    current_user=AuthJWT.get_jwt_subject()

    user=session.query(User).filter(User.username==current_user).first()

    if user.is_staff:
        orders=session.query(Order).all()

        return jsonable_encoder(orders)
    raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not SuperUser"
        )


@order_router.get("/orders/{id}")
async def get_order_by_id(id:int, Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    
    user=Authorize.get_jwt_subject()
    current_user=session.query(User).filter(User.username==user).first()

    if current_user.is_staff:
        order=session.query(Order).filter(Order.id==id).first()

        return jsonable_encoder(order)
    
    raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user not alowed to carry this request"
        )


@order_router.get("/user/orders")
async def get_user_orders(Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    user=Authorize.get_jwt_subject()

    current_user=session.query(User).filter(User.username==user).first()

    return jsonable_encoder(current_user.orders)


@order_router.get('/user/order/{id}/')
async def get_specific_order(id:int, Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    
    subject=Authorize.get_jwt_subject()

    currenr_user=session.query(User).filter(User.username==subject).first()

    orders=currenr_user.orders

    for o in orders:
        if o.id==id:
            return jsonable_encoder(o)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No such order id"
        )


@order_router.put('/order/update/{id}/')
async def update_order(id:int, order=OrderModel, Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    
    order_to_update=session.query(Order).filter(Order.id==id).first()

    order_to_update.quantity=order.quantity
    order_to_update.pizza_size=order.pizza_size

    session.commit()

    response={
            "id":order_to_update.id,
            "quantity":order_to_update.quantity,
            "pizza_size":order_to_update.pizza_size,
            "order_status":order_to_update.order_status
        }

    return jsonable_encoder(response)


@order_router.put('/order/status/update/{id}/')
async def update_order_status(id:int, order=OrderStatusModel, Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    
    username=Authorize.get_jwt_subject()

    current_user=session.query(User).filter(User.username==username).first()

    if current_user.is_staff:
        order_to_update=session.query(Order).filter(Order.id==id).first()
        order_to_update.order_status=order.order_status

        session.commit()

        response={
            "id":order_to_update.id,
            "quantity":order_to_update.quantity,
            "pizza_size":order_to_update.pizza_size,
            "order_status":order_to_update.order_status
        }

        return jsonable_encoder(response)


@order_router.delete('/order/delete/{id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_by_id(id:int, Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    
    order_to_delete=session.query(Order).filter(Order.id==id).first()

    if not order_to_delete:
        raise HTTPException(status_code=404, detail="Order not found")  # ✅ Added check

    session.delete(order_to_delete)

    session.commit()

    return order_to_delete










# pizza_models.py
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey
from database import Base, engine
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from sqlalchemy_utils.types import ChoiceType


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True)
    email = Column(String(80), unique=True)
    password = Column(Text, nullable=True)
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    orders = relationship('Order', back_populates='user')

    def __repr__(self):
        return f"Order {self.id}"


class Order(Base):

    ORDER_STATUSES = (
        ('PENDING', 'pending'),
        ('In-Transit', 'in-transit'),
        ('DELIVERED', 'delivered')
    )

    PIZZA_SIZES = (
        ('SMALL', 'SMALL'),
        ('MEDIUM', 'MEDIUM'),
        ('LARGE', 'LARGE'),
        ('EXTRA LARGE', 'EXTRA LARGE')
    )

    __tablename__='orders'
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)
    order_status = Column(ChoiceType(choices=ORDER_STATUSES), default='PENDING')
    pizza_size = Column(ChoiceType(choices=PIZZA_SIZES), default='SMALL')
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='orders')

    def __repr__(self):
        return {self.id}


# Ensure the table is created
Base.metadata.create_all(bind=engine)










# requirements.txt


# annotated-types==0.7.0
# anyio==4.8.0
# click==8.1.8
# colorama==0.4.6
# dnspython==2.7.0
# email_validator==2.2.0
# fastapi==0.115.7
# fastapi-jwt-auth==0.5.0
# greenlet==3.1.1
# h11==0.14.0
# idna==3.10
# MarkupSafe==3.0.2
# psycopg2-binary==2.9.10
# pydantic==1.10.9
# PyJWT==1.7.1
# python-dotenv==1.0.1
# sniffio==1.3.1
# SQLAlchemy==2.0.37
# SQLAlchemy-Utils==0.41.2
# starlette==0.45.3
# typing_extensions==4.12.2
# uvicorn==0.34.0
# Werkzeug==3.1.3










# schemas.py
import secrets

from pydantic import BaseModel, EmailStr, BaseSettings
# from pydantic.v1 import BaseSettings
from sqlalchemy import Column, Text, Boolean, Integer, String
from typing import Optional


class SignUpModel(BaseModel):
    id: Optional[int] = None
    username: str
    email: EmailStr
    password: str
    is_staff: Optional[bool] = False
    is_active: Optional[bool] = True

    model_config = {
        'from_attributes': True,
        'json_schema_extra': {
            'example': {
                'username': "johndoe",
                'email': "johndoe@gmail.com",
                'password': "password",
                'is_staff': False,
                'is_active': True
            }
        }
    }


class Settings(BaseSettings):
    # fastapijwt_token_secret: str = secrets.token_hex(32)
    AUTHJWT_SECRET_KEY: str ='a6a70eee80cae464d690b215d7754b25681cc5bfa07e28695df5a6203c3af233'
    authjwt_algorithm: str = "HS256"  # JWT algorithm
    authjwt_access_token_expires: int = 3600  # Token expiration time in seconds (1 hour)


class LoginModel(BaseModel):
    username: str
    password: str


class OrderModel(BaseModel):
    id:Optional[int]=None
    quantity:int
    order_status:Optional[str]="PENDING"
    pizza_size:Optional[str]="SMALL"
    user_id:Optional[int]

    class Config:
        orm_model=True
        schema_extra={
            "example":{
                "quantity":2,
                "pizza_size":"LARGE"
            }
        }


class OrderStatusModel(BaseModel):
    order_status:Optional[str]="PENDING"

    class Config:
        orm_model=True
        schema_extra={
            "example":{
                "order_status":"PENDING"
            }
        }










