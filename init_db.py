from database import engine, Base
from pizza_models import User, Order


Base.metadata.create_all(bind=engine)
