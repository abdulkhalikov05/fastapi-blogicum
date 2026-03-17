from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.base import PublishedBaseModel


class Category(PublishedBaseModel):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    slug = Column(String(50), unique=True, nullable=False)

    # Связи
    posts = relationship("Post", back_populates="category")
