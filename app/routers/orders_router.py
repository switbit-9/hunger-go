from .base import *
from app.schemas import User, GetOrders, OrderItem
from app.schemas import CreateOrders, UpdateOrderStatus
from fastapi.exceptions import HTTPException
from app.models import Orders, User, OrderItem



order_router = APIRouter(
    prefix='/order',
    tags=['orders']
)



@order_router.post('/place-order', status_code=status.HTTP_201_CREATED)
async def place_new_order(
        order : CreateOrders,
        Authorize:AuthJWT=Depends()
):
    current_user = check_authorization(Authorize)
    user = session.query(User).filter_by(username=current_user).first()
    new_order = Orders(
        delivery_address = order.delivery_address,
        comment = order.comment,
        user_id = user.id,
        restaurant_id = order.restaurant_id,
    )

    order_items = [
        OrderItem(
        quantity=o.quantity,
        comment = o.comment,
        food_item_id = o.food_item_id
        )
        for o in order.list_orders
    ]
    new_order.list_orders = order_items
    # new_order.user = user
    session.add(new_order)
    session.commit()
    session.refresh(new_order)
    return jsonable_encoder(new_order)


@order_router.get('/order/{id}')
async def get_order(id:int, Authorize:AuthJWT=Depends()):
    check_authorization(Authorize)
    current_user = Authorize.get_jwt_subject()
    order = session.query(Orders).filter(Orders.id==id).first()
    if order is None:
        return {}
    return jsonable_encoder(order)


@order_router.get('/my-orders')
async def user_orders(
        q : Annotated[Union[str, int, None], Query(title="Filter by time, price")] =None,
        Authorize:AuthJWT=Depends()
):
    current_user = check_authorization(Authorize)
    if q is None:
        query = session.query(User).filter_by(username=current_user).options(joinedload(User.orders)).first()

    user = from_query_to_object(query, exclude_fields={'password', 'orders'})
    orders = from_query_to_list(query.orders, exclude_fields={'user_id'})
    user['orders'] = orders
    return user


#UPDATE ORDER
@order_router.put('order/update-order/{id}')
async def update_order(
        id: int,
       new_order : GetOrders,
        Authorize:AuthJWT=Depends()
):
    current_user = check_authorization(Authorize)
    user = session.query(User).filter_by(username=current_user).first()
    order = session.query(Orders).filter(Orders.id == id).first()
    if user.id != order.user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="This order don't exists")
    #ONLY CANCEL ORDERS
    if new_order.order_status == 'CANCELED':
        order.order_status = new_order.order_status
    order.quantity = new_order.quantity
    order.delivery_address = new_order.delivery_address
    order.comment = new_order.comment
    session.add(order)
    session.commit()
    session.refresh(order)

    return {
        "message" : "success" ,
        "order" : jsonable_encoder(order)
    }


# UPDATE ORDER : Users can update order_status == CANCEL
@order_router.patch('/update-order-status/{id}')
async def update_order_status(
        id:int,
        order_status: UpdateOrderStatus,
        Authorize:AuthJWT=Depends()
):
    username = check_authorization(Authorize)
    user = session.query(User).filter_by(username=username).first()
    if not user.is_staff or user.is_administrator or order_status=='CANCEL':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Should be staff to modify order status rather than cancel")

    order = session.query(Orders).filter_by(id=id).first()
    order.order_status = order_status.order_status
    session.commit()
    session.refresh(order)
    return {
             'message': 'success',
             'order' : jsonable_encoder(order)
             }


# DELETE ORDER
@order_router.delete('/delete/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
        id : Annotated[int, Path(title="Order ID to delete")],
        Authorize:AuthJWT=Depends()
):
    check_authorization(Authorize)
    username = Authorize.get_jwt_subject()
    user = session.query(User).filter_by(username=username).first()
    order = session.query(Orders).filter_by(id=id).first()
    if user.id != order.user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Not authorized to delete this order'
                            )

    session.delete(order)
    session.commit()
    return {'message' : 'success'}
