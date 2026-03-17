from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.base import PublishedBaseModel


class Comment(PublishedBaseModel):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)

    # Внешние ключи
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)

    # Связи
    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
