from pydantic import BaseModel
from typing import Optional, Any
import datetime

class DesignBase(BaseModel):
    name: str
    prompt: str
    requirements_json: Optional[Any] = None
    layout_json: Optional[Any] = None
    floorplan_json: Optional[Any] = None
    house3d_json: Optional[Any] = None

class DesignCreate(DesignBase):
    pass

class DesignUpdate(BaseModel):
    name: Optional[str] = None
    prompt: Optional[str] = None
    requirements_json: Optional[Any] = None
    layout_json: Optional[Any] = None
    floorplan_json: Optional[Any] = None
    house3d_json: Optional[Any] = None

class DesignResponse(DesignBase):
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {
        "from_attributes": True
    }
