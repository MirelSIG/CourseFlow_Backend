from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = None
SessionLocal = None

def init_db(database_uri: str):
    global engine, SessionLocal
    engine = create_engine(database_uri, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
