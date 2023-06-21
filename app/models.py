import datetime
from .database import Base
from sqlalchemy import Table, Column, Integer, String, Text, Boolean, ForeignKey, DateTime, DECIMAL
from sqlalchemy_utils.types import ChoiceType
from sqlalchemy.orm import relationship

class Restaurant(Base):
    __tablename__ = 'restaurant'
    id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True, nullable=False)
    password = Column(Text())
    name = Column(String(25), unique=True)
    email = Column(String(80), unique=True)
    address = Column(String(25))
    phone_number = Column(String(20), unique=True)
    is_administrator = Column(Boolean, default=True)
    is_staff = Column(Boolean, default=True)
    food_items = relationship('FoodItem', back_populates='restaurant', lazy='joined')

    def __repr__(self):
        return self.username


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True)
    name = Column(String(20), nullable=True)
    lastname = Column(String(20), nullable=True)
    email = Column(String(80), unique=True)
    password = Column(Text())
    is_active = Column(Boolean, default=True)
    phone_number = Column(String(20), nullable=False)
    address = Column(String(25))
    time_joined = Column(DateTime, default=datetime.datetime.utcnow())
    orders = relationship('Orders', back_populates='user', lazy='joined')

    def __repr__(self):
        return f"<User {self.username}"


class FoodCategory(Base):
    __tablename__ = "food_category"
    id = Column(Integer, primary_key=True)
    category_name = Column(String(10))

class FoodItem(Base):
    __tablename__ = "fooditem"
    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)
    description = Column(String(100))
    ingredients = Column(String(100))
    price = Column(DECIMAL(precision=8, scale=2))
    is_active = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey('food_category.id'))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    category = relationship('FoodCategory', lazy='joined')
    restaurant = relationship('Restaurant', back_populates='food_items')
    order = relationship('OrderItem', back_populates='food_item')

    def __repr__(self):
        return self.name

    @classmethod
    def from_query_to_list(cls, results):
        return [
            {
                'id' : result.id,
                'name' : result.name,
                'description' : result.description,
                'ingredients' : result.ingredients,
                'price' : result.price,
                'category' : result.result.category,
                'restaurant' : result.restaurant,
            }
            for result in results if result.is_active is True
        ]

class Orders(Base):
    ORDER_STATUSES = (
        ('PENDING', 'pending'),
        ('IN-TRANSIT', 'in-transit'),
        ('DELIVERED', 'delivered')
    )
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    order_status = Column(ChoiceType(choices = ORDER_STATUSES), default='PENDING')
    order_time = Column(DateTime, default=datetime.datetime.utcnow())
    estimated_time = Column(DateTime, nullable=True)
    delivery_address = Column(String(100), default=False)
    comment = Column(String(300))
    user_id = Column(Integer, ForeignKey('users.id'))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    orders_list = relationship('OrderItem', back_populates='orders')
    user = relationship('User', back_populates='orders', lazy='joined')

    def __repr__(self):
        return f"<Order : {self.id}>"



class OrderItem(Base):
    __tablename__ = 'order_item'
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)
    comment = Column(String(20))
    food_item_id = Column(Integer, ForeignKey('fooditem.id'))
    orders_id = Column(Integer, ForeignKey('orders.id'))
    food_item = relationship('FoodItem', back_populates='order', lazy='joined')
    orders = relationship('Orders', back_populates='orders_list')

    def __repr__(self):
        return f"<Order Item : {self.id}>"


