import os

from app.routers.auth_routes import auth_router
from app.routers.orders_router import order_router
from app.routers.shop_router import shop_router
from app.routers.core_router import core_router
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
import inspect, re
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.openapi.utils import get_openapi

app = FastAPI()

app.include_router(auth_router)
app.include_router(order_router)
app.include_router(shop_router)
app.include_router(core_router)


class Settings(BaseModel):
    authjwt_secret_key : str = os.environ.get("SECRET_TOKEN_KEY")


@AuthJWT.load_config
def get_settings():
    return Settings()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title = "My Auth API",
        version = "1.0",
        description = "An API with an Authorize Button",
        routes = app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Enter: **'Bearer &lt;JWT&gt;'**, where JWT is the access token"
        }
    }

    # Get all routes where jwt_optional() or jwt_required
    api_router = [route for route in app.routes if isinstance(route, APIRoute)]

    for route in api_router:
        path = getattr(route, "path")
        endpoint = getattr(route,"endpoint")
        methods = [method.lower() for method in getattr(route, "methods")]

        for method in methods:
            # access_token
            if (
                re.search("jwt_required", inspect.getsource(endpoint)) or
                re.search("fresh_jwt_required", inspect.getsource(endpoint)) or
                re.search("jwt_optional", inspect.getsource(endpoint))
            ):
                openapi_schema["paths"][path][method]["security"] = [
                    {
                        "Bearer Auth": []
                    }
                ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi