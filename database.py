from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("sqlite:///pizza_delivery.db", echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)

# Ensure the tables are created
Base.metadata.create_all(bind=engine)
