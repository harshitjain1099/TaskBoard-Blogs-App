from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import MEDIUMTEXT, LONGTEXT
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship 


class Users(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key = True, index = True)
    email = Column(String, unique = True)
    username = Column(String, unique = True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default = True)
    role = Column(String)
    phone_number = Column(String)
   


class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key = True, index = True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean,default = False)
    owner_id = Column(Integer, ForeignKey("users.id"))


class Blog(Base):
    __tablename__ = "blogs"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    summary = Column(MEDIUMTEXT)  
    content = Column(LONGTEXT, nullable=False)  
    published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    author = relationship("Users", backref="blogs")


class Support(Base):
    __tablename__ = "support"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255))
    subject = Column(String(255),nullable=False)  
    message = Column(MEDIUMTEXT, nullable=False) 
   



