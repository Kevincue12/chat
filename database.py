from dotenv import load_dotenv
import os
from sqlmodel import create_engine, Session

load_dotenv()  # Cargar variables .env

def get_engine():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise Exception("No está configurada la variable DATABASE_URL")
    engine = create_engine(url, echo=False)
    return engine

def get_db_session():
    engine = get_engine()
    return Session(engine)
