from fastapi import status, Query, Path, APIRouter, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from app.database import Session, engine
from app.models import Restaurant
from pydantic.typing import Annotated, Union, List
from sqlalchemy.orm import joinedload



session = Session(bind=engine)


def check_authorization(Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    return Authorize.get_jwt_subject()


def handle_refresh_token( Authorize : AuthJWT=Depends() ):
    try:
        Authorize.jwt_refresh_token_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Please provide a valid refresh_token"
                            )
    current_user = Authorize.get_jwt_subject()


def check_shop_authorization(Authorize:AuthJWT):
    check_authorization(Authorize)
    username = Authorize.get_jwt_subject()
    shop_user = session.query(Restaurant).filter_by(username=username).first()
    if not shop_user.is_staff or not shop_user.is_administrator:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not a staff or administrator")
    return shop_user


def from_query_to_object(result, include_fields=None, exclude_fields=None):
    if exclude_fields is not False:
        return jsonable_encoder(result, exclude=exclude_fields)
    elif exclude_fields is not False:
        return jsonable_encoder(result, include=include_fields)
    else:
        return jsonable_encoder(result)

def from_query_to_list(results, include_fields=None, exclude_fields=None):
    if exclude_fields is not False:
        return [ jsonable_encoder(result, exclude=exclude_fields) for result in results ]
    elif exclude_fields is not False:
        return [ jsonable_encoder(result, include=include_fields)for result in results ]
    else:
        return [ jsonable_encoder(result) for result in results]

