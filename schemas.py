from pydantic import BaseModel, condecimal
from pydantic.typing import Optional, Union, List
from datetime import datetime
from pydantic.typing import Annotated

class Settings(BaseModel):
    authjwt_secret_key : str = '27f46e5b1b4208c4973a00ee240f2136817913b96a1401b4da7b74676f89a173'



class _BaseUser(BaseModel):
    username: str
    name: str
    lastname: str
    email: str
    phone_number: str
    address: str


class CreateUser(_BaseUser):
    password: str

    class Config:
        orm_mode = True
        schema_extra = {
            'example': {
                'username': 'john',
                'name': 'john',
                'lastname': 'john',
                'email': 'john@gmail.com',
                'password': 'password',
                'phone_number': '+3400600523',
                'address': 'Rr. Kosovareve',
                'is_active': True
            }
        }


class User(_BaseUser):
    time_joined : Annotated[datetime, None] = None
    is_active: Optional[bool]


class LoginForm(BaseModel):
    username: str
    password: str

    class Config:
        orm_mode = True
        schema_extra = {
            'example': {
                'username': 'john',
                'password': 'password',
            }
        }


class _BaseRestaurant(BaseModel):
    username: str
    name: str
    email: str | None
    phone_number: str | None
    address: str | None

    @classmethod
    async def restaurant_object(cls, results, fields=None, response_type='object'):
        response = [] if response_type == 'list' else {}
        for result in results:
            item = {}
            if fields is not None:
                for field in fields:
                    if field in results.__dict__():
                        response[field] = results[field]

        return response


class GetRestaurant(_BaseRestaurant):
    id : int
    is_active: Annotated[bool , None] = True


class CreateRestaurant(_BaseRestaurant):
    password: str
    is_administrator: bool
    is_staff: bool

    class Config:
        orm_mode = True
        schema_extra = {
            'example': {
                'username': 'pizzerie',
                'name': 'Pizzerie Luna',
                'phone_number': '+34000 000 000',
                'email': 'john@gmail.com',
                'password': 'password',
                'address': "7724 Glenlake Drive",
                'is_administrator': False,
                'is_staff': True
            }
        }

class _BaseCategory(BaseModel):
    category_name : str

class Category(_BaseCategory):
    id : int


class LoginRestaurant(BaseModel):
    username: str
    password: str

    class Config:
        orm_mode = True
        schema_extra = {
            'example': {
                'username': 'pizzerie',
                'password': 'password',
            }
        }


class _BaseOrderItem(BaseModel):
    quantity : int
    comment : str


class CreateOrderItem(_BaseOrderItem):
    pass

class OrderItem(_BaseOrderItem):
    id : int




class CreateOrders(BaseModel):
    restaurant_id : int
    delivery_address : str
    comment : str
    list_orders : Union[List[CreateOrderItem], None] = None

    class Config:
        orm_mode = True
        schema_extra = {
            'example' : {
                'restaurant_id' : 2,
                'delivery_address' : "1960 W CHELSEA AVE STE 2006R",
                'comment' : "Can you please pack them on letter",
                'list_orders' : [
                    {
                        "food_item_id" : 3,
                        "quantity" : 1,
                        "comment" : "Without mayoneese",
                    },
                    {
                        "food_item_id" : 5,
                        "quantity" : 2,
                        "comment" : "Without mayoneese",
                    },
                ],
            }
        }





class UpdateOrderStatus(BaseModel):
    order_status: Optional[str] = 'PENDING'
    class Config:
        orm_mode = True
        schema_extra = {
            'example' : {
                'order_status' : "CANCEL"
            }
        }





class _BaseFoodItem(BaseModel):
    name : str
    description : str
    ingredients : str
    price : Annotated[condecimal(decimal_places=2) , None] = 0

class GetFoodItem(_BaseFoodItem):
    id : int
    is_active: Optional[bool] = None
    category_id : int
    category : Category

class CreateFoodItem(_BaseFoodItem):
    ingredients: list = []
    category_id : int

    class Config:
        orm_mode = True
        schema_extra = {
            'example': {
                'name': 'margarita',
                'description': 'Margherita pizza is known for its ingredients representing the colours of the Italian flag. These ingredients include red tomato sauce, white mozzarella and fresh green basil.',
                'ingredients': ['tomato sauce', 'fresh mozzarella cheese', 'basil leaves', 'Parmesan cheese'],
                'category_name': 'pizza',
                'price': 6.99,
                'is_active': True,
            }
        }

class UpdateFoodItem(BaseModel):
    name: Annotated[str, None] = None
    description: Annotated[str, None] = None
    ingredients: Annotated[str, None] = None
    price: Annotated[condecimal(decimal_places=2), None] = None
    ingredients: Annotated[list, None] = None
    category_id : Annotated[int, None] = None
    is_active: Optional[bool] = None

class _BaseOrderItem(BaseModel):
    quantity : str
    comment : str


class OrderItem(_BaseOrderItem):
    id : int
    food_item_id : int



class _BaseOrders(BaseModel):
    order_status : str
    order_time : Optional[datetime] = None
    estimated_time : Optional[datetime] = None
    delivery_address : str
    comment : str













class CreateCategory(BaseModel):
    category_name: str

    class Config:
        orm_mode = True
        schema_extra = {
            'example': {
                'category_name': 'Pizzerie'
            }
        }

class GetCategories(Category):
    id : int
    category_name : str

class GetRestaurantModel(GetRestaurant):
    food_items : List[GetFoodItem]



class GetOrders(_BaseOrders):
    id : int
    restaurant_name : str
    restaurant_id : int
    list_orders : List[OrderItem]