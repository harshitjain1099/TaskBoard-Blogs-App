from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker



DATABASE_URL = "mysql+pymysql://root:nokia7.2@127.0.0.1:3306/todoapplicationdatabase"


engine = create_engine(DATABASE_URL)

SectionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

Base = declarative_base()
