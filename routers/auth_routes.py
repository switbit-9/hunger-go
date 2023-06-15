import datetime
from fastapi import APIRouter, status, Depends
from schemas import CreateRestaurant, LoginRestaurant, CreateUser, LoginForm
from models import User, Restaurant
from database import Session, engine
from fastapi.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder
from .shop_routes import shop_router
from .base import check_authorization, handle_refresh_token, session

auth_router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

@auth_router.post('/sign_up', response_model=CreateUser, status_code=status.HTTP_201_CREATED)
async def sign_up_user(
        user : CreateUser
):
    db_email = session.query(User).filter(User.email==user.email).first()
    if db_email is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail="User with that email already exists")
    db_username = session.query(User).filter(User.username==user.username).first()
    if db_username is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail="User with that username already exists")

    new_user = User(
        username = user.username.lower(),
        name = user.name,
        lastname = user.lastname,
        email = user.email,
        password = generate_password_hash(user.password),
        phone_number = user.phone_number,
        address = user.address,
        is_active= user.is_active,
    )
    session.add(new_user)
    session.commit()
    session.refresh()
    return new_user


@auth_router.post('/login', status_code=status.HTTP_200_OK)
def login(
        user : LoginForm,
        Autherize : AuthJWT=Depends()
):
    db_user = session.query(User).filter_by(username=user.username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail="Wrong username")
    if not check_password_hash(db_user.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail= "Wrong Password")

    access_token = Autherize.create_access_token(subject=db_user.username, expires_time=datetime.timedelta(days=1))
    refresh_token = Autherize.create_refresh_token(subject=db_user.username)

    response = {
        "access_token" : access_token,
        "refresh_token" : refresh_token
    }

    return jsonable_encoder(response)


@auth_router.get('/refresh-token')
async def refresh_token( Autherize : AuthJWT = Depends() ):
    current_user = handle_refresh_token( Autherize )
    access_token = Autherize.create_access_token(subject=current_user, expires_time=datetime.timedelta(days=1))
    return jsonable_encoder({'access_token' : access_token})



@auth_router.post('/shop/sign-up', status_code=status.HTTP_201_CREATED)
async def sign_up_restaurant(
        shop : CreateRestaurant
):
    db_email = session.query(Restaurant).filter_by(email=shop.email).first()
    if db_email is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail="Restaurant registered this email already exists")
    db_username = session.query(Restaurant).filter(Restaurant.username==shop.username).first()
    if db_username is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail="Restaurant with this username already exists")

    new_shop = Restaurant(
        username = shop.username.lower(),
        email = shop.email,
        name = shop.name,
        address = shop.address,
        phone_number = shop.phone_number,
        password = generate_password_hash(shop.password),
        is_staff= shop.is_staff,
        is_administrator = shop.is_administrator
    )
    session.add(new_shop)
    session.commit()
    session.refresh(new_shop)
    return jsonable_encoder(new_shop, exclude={'password'})


@auth_router.post('/shop/login', status_code=status.HTTP_200_OK)
async def login_restaurant(
        shop : LoginRestaurant,
        Autherize : AuthJWT=Depends()
):
    db_shop = session.query(Restaurant).filter_by(username=shop.username).first()
    if db_shop is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Wrong username")
    if not check_password_hash(db_shop.password, shop.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Wrong Password")

    access_token = Autherize.create_access_token(subject=db_shop.username, expires_time=datetime.timedelta(days=1))
    refresh_token = Autherize.create_refresh_token(subject=db_shop.username)

    response = {
        "access_token": access_token,
        "refresh_token": refresh_token
    }
    return response