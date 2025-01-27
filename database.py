from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import create_engine
# from sqlalchemy.orm import declarative_base, sessionmaker
#
#
# engine = create_engine("postgresql://samir:Sairam2025@localhost/pizza_delivery",
#                        echo=True
#                        )
# Use SQLite instead of PostgreSQL
engine = create_engine("sqlite:///pizza_delivery.db", echo=True)
#
# Base = declarative_base()
#
# Session = sessionmaker()
# Base class for the ORM models
Base = declarative_base()

# Create a session factory
Session = sessionmaker(bind=engine)

# Create a database file on first run
# Base.metadata.create_all(bind=engine)

# Usage Example
if __name__ == "__main__":
    # Initialize a session
    session = Session()

    # Your application logic goes here

    # Close the session when done
    session.close()
