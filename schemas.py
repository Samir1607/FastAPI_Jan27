import secrets

from pydantic import BaseModel, EmailStr, BaseSettings
# from pydantic.v1 import BaseSettings
from sqlalchemy import Column, Text, Boolean, Integer, String
from typing import Optional


# class SignUpModel(BaseModel):
#     id : Optional[int]
#     username : str
#     email : str
#     password : str
#     is_staff : Optional[bool]
#     is_active : Optional[bool]
#
#     class Config:
#         orm_mode = True
#         schema_extra = {
#             'example':{
#                 'username':"johndoe",
#                 'email':"johndoe@gmail.com",
#                 'password':"password",
#                 'is_staff':False,
#                 'is_active':True
#             }
#         }

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
