from .base import *
from sqlalchemy import or_
from app.schemas import GetRestaurant, GetCategories, GetFoodItem, GetRestaurantModel
from app.models import Restaurant, FoodItem, FoodCategory

core_router = APIRouter(
    prefix='',
    tags=['core']
)

@core_router.get('/shops', response_model = List[GetRestaurant])
async def list_restaurants(Authorize:AuthJWT=Depends()):
    user = check_authorization(Authorize)
    restaurants = session.query(Restaurant).all()
    restaurant_list = from_query_to_list(restaurants, exclude_fields={'password', 'is_staff', 'is_administrator', 'food_items'})
    return restaurant_list

@core_router.get('/shop/{id}', response_model=GetRestaurantModel)
async def get_shop(id: int, Authorize:AuthJWT=Depends()):
    user = check_authorization(Authorize)
    result = session.query(Restaurant).options(joinedload(Restaurant.food_items)).first()
    response = from_query_to_object(result, exclude_fields={'password', 'is_staff', "is_administrator", 'food_items'})
    food_items = from_query_to_list(result.food_items)
    response['food_items'] = food_items
    return response

@core_router.get('/categories', response_model=List[GetCategories])
async def list_categories(Authorize:AuthJWT=Depends()):
    user = check_authorization(Authorize)
    categories = session.query(FoodCategory).all()
    list_categories = from_query_to_list(categories)
    return list_categories





@core_router.get('/food/{id}', response_model = GetFoodItem)
async def get_food_item(id: int, Authorize:AuthJWT=Depends()):
    user = check_authorization(Authorize)
    query = session.get(FoodItem, id)
    response = from_query_to_object(query)
    return response


@core_router.get('/foods', response_model = List[GetFoodItem])
async def get_food_item(
        q : Annotated[Union[str, float, int ,None], Query(title='Query by name, price, category')] =None,
        Authorize:AuthJWT=Depends()):
    user = check_authorization(Authorize)

    if q is None: # Paginate
        query = session.query(FoodItem).all()
    elif isinstance(q, str):
        query = session.query(FoodItem).filter(or_(FoodItem.name.ilike(f'%{q}%'), FoodItem.description.ilike(f'%{q}%'))).all()
    elif isinstance(q, float) or isinstance(q, int):
        query = session.query(FoodItem).filter(FoodItem.price==q).all()
    response = from_query_to_list(query)

    return response






