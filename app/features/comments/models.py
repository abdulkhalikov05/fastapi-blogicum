from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.base import PublishedBaseModel


class Comment(PublishedBaseModel):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)

    # Внешние ключи
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    author_id = Column(Integer, nullable=False)

    # Связи
    post = relationship("Post", back_populates="comments")

    def __repr__(self):
        return f"<Comment {self.id} on post {self.post_id}>"