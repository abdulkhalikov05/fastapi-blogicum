from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.base import PublishedBaseModel


class Location(PublishedBaseModel):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), nullable=False)

    # Связи
    posts = relationship("Post", back_populates="location")
