import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from psycopg_pool import AsyncConnectionPool

load_dotenv()

def get_database_url(async_driver=False):
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME")
    
    if all([db_user, db_password, db_host, db_name]):
        if async_driver:
            # LangGraph/psycopg_pool usually expects postgresql:// but some might want +psycopg
            return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    return None

def get_engine():
    url = get_database_url()
    if not url:
        raise ValueError("Database configuration is missing. Provide DB_USER, DB_PASSWORD, DB_HOST, DB_NAME.")
    
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

def get_async_pool(max_size=20) -> AsyncConnectionPool:
    """
    Creates an AsyncConnectionPool for use with libraries like LangGraph or direct psycopg.
    """
    url = get_database_url(async_driver=True)
    if not url:
        # Fallback for local development if not configured
        url = "postgresql://local:local@localhost:5432/lumi"
    
    return AsyncConnectionPool(
        conninfo=url,
        max_size=max_size,
        kwargs={"autocommit": True, "prepare_threshold": 0},
        open=False,
        check=AsyncConnectionPool.check_connection,
    )

engine = None

def get_session_local():
    global engine
    if engine is None:
        engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

def SessionLocal():
    return get_session_local()()

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
