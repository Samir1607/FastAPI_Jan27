from pydantic import BaseModel, EmailStr
from typing import Optional
from pydantic import BaseSettings

class SignUpModel(BaseModel):
    id: Optional[int] = None
    username: str
    email: EmailStr
    password: str
    is_staff: Optional[bool] = False
    is_active: Optional[bool] = True

    class Config:
        schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "johndoe@gmail.com",
                "password": "password",
                "is_staff": False,
                "is_active": True
            }
        }

class LoginModel(BaseModel):
    username: str
    password: str

class OrderModel(BaseModel):
    id: Optional[int] = None
    quantity: int
    order_status: Optional[str] = "PENDING"
    pizza_size: Optional[str] = "SMALL"
    user_id: Optional[int]

    class Config:
        schema_extra = {
            "example": {
                "quantity": 2,
                "pizza_size": "LARGE"
            }
        }

class OrderStatusModel(BaseModel):
    order_status: Optional[str] = "PENDING"

    class Config:
        schema_extra = {
            "example": {
                "order_status": "PENDING"
            }
        }

class Settings(BaseSettings):
    AUTHJWT_SECRET_KEY: str = 'a6a70eee80cae464d690b215d7754b25681cc5bfa07e28695df5a6203c3af233'
    authjwt_algorithm: str = "HS256"
    authjwt_access_token_expires: int = 3600
