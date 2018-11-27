from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, PrimaryKeyConstraint
from sqlalchemy import (
    Integer, String, DateTime, Text, Float, Boolean)
from sqlalchemy.orm import relationship

DeclarativeBase = declarative_base()


class Business(DeclarativeBase):
    __tablename__ = 'businesses'
    business_id = Column(String(22), primary_key=True, index=True)
    business_name = Column(Text, index=True)
    neighborhood = Column(Text())
    city = Column(Text())
    state = Column(Text())
    postal_code = Column(String(7))
    latitude = Column(Float())
    longitude = Column(Float())
    stars = Column(Float())
    review_count = Column(Integer())
    is_open = Column(Boolean())
    photos = relationship('Photo', backref='businesses')


class Photo(DeclarativeBase):
    __tablename__ = 'photos'
    photo_id = Column(String(22), primary_key=True, index=True)
    business_id = Column(String(22), ForeignKey('businesses.business_id'),
                         index=True)
    label = Column(Text())


class Category(DeclarativeBase):
    __tablename__ = 'business_category'
    business_id = Column(String(22), ForeignKey('businesses.business_id'),
                         primary_key=True, index=True)
    category_name = Column(String(35), primary_key=True, index=True)
    __table_args__ = (
        PrimaryKeyConstraint('business_id', 'category_name'),
        {},
    )
