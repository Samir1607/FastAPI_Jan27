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
        return f"<User {self.username}"


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
    order_status = Column(ChoiceType(choices=ORDER_STATUSES), default='pending')
    pizza_size = Column(ChoiceType(choices=PIZZA_SIZES), default='SMALL')
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='orders')

    def __repr__(self):
        return {self.id}


# Ensure the table is created
Base.metadata.create_all(bind=engine)
