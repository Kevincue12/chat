import os
from sqlmodel import create_engine, Session

def get_engine():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise Exception("No está configurada la variable DATABASE_URL")

    # asegurar ssl
    if "sslmode" not in url:
        url = url + ("&sslmode=require" if "?" in url else "?sslmode=require")

    return create_engine(url, echo=False)

engine = get_engine()

def get_db_session():
    return Session(engine)
