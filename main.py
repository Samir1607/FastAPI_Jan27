import os
from fastapi import FastAPI
from auth_routes import auth_router
from order_routes import order_router
from fastapi_jwt_auth import AuthJWT
from schemas import Settings


app = FastAPI()


@AuthJWT.load_config
def get_config():
    # return{
    #
    #     "jwt_secret_key": os.environ["AUTHJWT_SECRET_KEY"],
    #
    #     "jwt_algorithm": "HS256"
    #
    # }
    return Settings()
    # print( {
    #     'authjwt_secret_key': Settings().fastapijwt_token_secret,
    #     'authjwt_algorithm': Settings().authjwt_algorithm,
    #     'authjwt_access_token_expires': Settings().authjwt_access_token_expires
    # })

app.include_router(auth_router)
app.include_router(order_router)
