from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class LocationBase(BaseModel):
    name: str
    is_published: bool = True


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    is_published: Optional[bool] = None


class Location(LocationBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
