from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.base import PublishedBaseModel
import datetime


class Post(PublishedBaseModel):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256), nullable=False)
    text = Column(Text, nullable=False)
    pub_date = Column(DateTime, nullable=False, default=datetime.datetime.now)
    image = Column(String(256), nullable=True)

    # Внешние ключи
    author_id = Column(Integer, nullable=False)  # Убрали ForeignKey("users.id")
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    # Связи (убрали author)
    location = relationship("Location", back_populates="posts")
    category = relationship("Category", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")