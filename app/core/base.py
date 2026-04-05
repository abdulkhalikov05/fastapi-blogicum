from sqlalchemy import Column, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class PublishedBaseModel(Base):
    __abstract__ = True
    
    is_published = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)