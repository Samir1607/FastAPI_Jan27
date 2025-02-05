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


# Route to check if orders are accessible (for debugging)
@order_router.get('/')
async def hello(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    return {"message": "This is the order router"}


# Route to place an order
@order_router.post("/order", status_code=status.HTTP_201_CREATED)
async def place_an_order(order: OrderModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_order = Order(
        pizza_size=order.pizza_size,
        quantity=order.quantity
    )
    new_order.user = user

    session.add(new_order)
    session.commit()

    return jsonable_encoder({
        "pizza_size": new_order.pizza_size,
        "id": new_order.id,
        "quantity": new_order.quantity,
        "order_status": new_order.order_status
    })


# Route to list all orders (for staff only)
@order_router.get("/orders")
async def all_orders_list(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if not user or not user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be an admin to view all orders"
        )
    
    orders = session.query(Order).all()
    return jsonable_encoder(orders)


# Route to get an order by ID (for staff only)
@order_router.get("/orders/{id}")
async def get_order_by_id(id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if not user or not user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be an admin to view orders"
        )
    
    order = session.query(Order).filter(Order.id == id).first()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    return jsonable_encoder(order)


# Route to get orders for the current user
@order_router.get("/user/orders")
async def get_user_orders(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return jsonable_encoder(user.orders)


# Route to get a specific order for the current user
@order_router.get('/user/order/{id}/')
async def get_specific_order(id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check if order exists for this user
    order = next((o for o in user.orders if o.id == id), None)

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    return jsonable_encoder(order)


# Route to update an order (only by the user who placed it)
@order_router.put('/order/update/{id}/')
async def update_order(id: int, order: OrderModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    
    order_to_update = session.query(Order).filter(Order.id == id).first()

    if not order_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    order_to_update.quantity = order.quantity
    order_to_update.pizza_size = order.pizza_size

    session.commit()

    return jsonable_encoder({
        "id": order_to_update.id,
        "quantity": order_to_update.quantity,
        "pizza_size": order_to_update.pizza_size,
        "order_status": order_to_update.order_status
    })


# Route to update the status of an order (only for staff)
@order_router.put('/order/status/update/{id}/')
async def update_order_status(id: int, order: OrderStatusModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if not user or not user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be an admin to update order status"
        )

    order_to_update = session.query(Order).filter(Order.id == id).first()

    if not order_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    order_to_update.order_status = order.order_status

    session.commit()

    return jsonable_encoder({
        "id": order_to_update.id,
        "quantity": order_to_update.quantity,
        "pizza_size": order_to_update.pizza_size,
        "order_status": order_to_update.order_status
    })


# Route to delete an order by ID (only by staff or the user who placed the order)
@order_router.delete('/order/delete/{id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_by_id(id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    order_to_delete = session.query(Order).filter(Order.id == id).first()

    if not order_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if order_to_delete.user != user and not user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this order"
        )

    session.delete(order_to_delete)
    session.commit()

    return jsonable_encoder({"message": "Order deleted successfully"})
