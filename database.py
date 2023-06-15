from sqlalchemy import create_engine, URL
import os
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import DBAPIError

url_object = URL.create(
    "postgresql",
    username="postgres",
    password="1234",  # plain (unescaped) text
    host="localhost",
    database="pizza_delivery",
)

# database_str = 'postgresql://' + os.environ.get('DB_HOST') + ":" + os.environ.get('DB_USER_PASSWORD') + "@" + os.environ.get('DB_HOST') + "/" + os.environ.get("DB_NaDB_NAMEm")
engine = create_engine(url_object,
                       echo=True
                       )

try:
    engine.connect()
    print('Connection with DB is active and working')

except DBAPIError as e:
    print("Connection Error :", str(e))

    try:
        engine.dispose()
        engine = create_engine(url_object,
                               echo=True
                               )
        engine.connect()

    except DBAPIError as e:
        print("Reconnection Error :", str(e))



Base = declarative_base()

Session = sessionmaker()

