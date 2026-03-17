from sqlalchemy import Column, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base  # database.py теперь будет в core


class PublishedBaseModel(Base):
    __abstract__ = True
    
    is_published = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
