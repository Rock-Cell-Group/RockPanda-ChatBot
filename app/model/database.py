from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# all被用來在模塊級別暴露接口
# all是對於模塊公開接口的一種約定，比起下劃線，all提供了暴露接口用的“白名單”。一些不以下劃線開頭的變量（比如從其他地方import 到當前模塊的成員）可以同樣被排除出去。
__all__ = ["get_db", "engine"]

# Define your MySQL database URL with SSL parameters
SQLALCHEMY_DATABASE_URL = f'{settings.DATABASE_URL}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
