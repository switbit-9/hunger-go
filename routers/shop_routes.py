from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from fastapi import status, Query, Path
from schemas import CreateFoodItem, GetFoodItem, CreateCategory, GetOrders, UpdateFoodItem
from models import Restaurant, User, FoodItem, FoodCategory, Orders
from database import Session, engine
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import joinedload
from typing import Annotated
from .base import check_shop_authorization, session, from_query_to_list, from_query_to_object


shop_router = APIRouter(
    prefix='/shop',
    tags = ['shop']
)


@shop_router.post('/create-food/')
def create_food_item(
        item : CreateFoodItem,
        Authorize : AuthJWT = Depends()
):
    shop_user = check_shop_authorization(Authorize)
    category = session.query(FoodCategory).filter_by(id=item.category_id).first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT,
                            detail=f"{item.category_name} not found")

    add_menu = FoodItem(
        name = item.name,
        description = item.description,
        ingredients = str(", ".join(item.ingredients)), # Convert list to string
        price = item.price,
        category_id = category.id,
        restaurant_id = shop_user.id
    )
    session.add(add_menu)
    session.commit()
    session.refresh(add_menu)

    return jsonable_encoder(add_menu)

#UPDATE only one field
@shop_router.patch('/update-food/{id}')
def update_food_item(
        id : int,
        item : UpdateFoodItem,
        Authorize : AuthJWT=Depends()
):
    shop_user = check_shop_authorization(Authorize)
    db_item = session.get(FoodItem, id)
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"This item {item.name} doesn't exist")
    item_data = item.dict(exclude_unset=True)
    for key, value in item_data.items():
        setattr(db_item, key, value)
    session.commit()
    session.refresh(db_item)
    return jsonable_encoder(db_item)


@shop_router.delete('delete-food/{id}')
def delete_item(
        id : int,
        Authorize : AuthJWT = Depends()
):
    shop_user = check_shop_authorization(Authorize)
    db_item = session.query(FoodItem).filter(FoodItem.id == id).first()
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if db_item.restaurant_id != shop_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    session.delete(db_item)
    session.commit()
    return {"operation" : 'success'}



@shop_router.post('/add-category/', status_code=status.HTTP_201_CREATED)
def add_category(
        category : CreateCategory,
        Authorize:AuthJWT=Depends()
):
    shop_user = check_shop_authorization(Authorize)
    check_category = session.query(FoodCategory).filter_by(category_name=category.category_name).first()
    if check_category is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"{category.name} exists.")
    new_category = FoodCategory(
        category_name = category.category_name
    )
    session.add(new_category)
    session.commit()
    session.refresh(new_category)
    return jsonable_encoder(new_category)


#LIST ALL ORDER or FILTER BY order_status
@shop_router.get('/orders')
async def list_orders(
        q: Annotated[str | None, Query(max_length=20, title="Filter by pending/in-transit/delivered fields")] = None,
        Authorize : AuthJWT=Depends()
):
    shop_user = check_shop_authorization(Authorize)
    if q is not None:
        results = session.query(Orders).options(joinedload(Orders.user)).options(joinedload(Orders.restaurant)).filter(Orders.restaurant_id == shop_user.id).filter(Orders.order_status==q).all()
    else:
        results = session.query(Orders).options(joinedload(Orders.user)).filter(Orders.restaurant_id == shop_user.id).all()
    response = {
        'restaurant' : from_query_to_object(shop_user, exclude_fields={'password'}),
        'orders' : [],
    }
    for result in results:
        order = from_query_to_object(result, exclude_fields={'user'})
        user = from_query_to_object(result.user, exclude_fields={'password'})
        order['user'] = user
        response['orders'].append(order)

    return response



#Fetch Order by ID
@shop_router.get('/orders/{id}')
async def list_orders(
        id: Annotated[int, Path(title="Order ID")],
        Authorize:AuthJWT=Depends()
):
    shop = check_shop_authorization(Authorize)

    results = session.query(Orders).options(joinedload(Orders.user)).filter(Orders.restaurant_id == shop.id).filter(Orders.id==id).all()

    response = from_query_to_list(results)

    return response