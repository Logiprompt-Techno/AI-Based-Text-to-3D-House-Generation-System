from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from ..layout.models import RoomType

class Wall(BaseModel):
    id: str
    x1: float
    y1: float
    x2: float
    y2: float
    thickness: float
    is_exterior: bool

class OpeningType(str):
    door = "door"
    window = "window"
    entrance = "entrance"

class Opening(BaseModel):
    id: str
    opening_type: str
    host_wall_id: str
    x: float
    y: float
    width: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RoomBoundary(BaseModel):
    room_id: str
    room_type: RoomType
    x: float
    y: float
    width: float
    depth: float

class Label(BaseModel):
    room_id: str
    text: str
    x: float
    y: float

class Dimension(BaseModel):
    room_id: str
    text: str
    x: float
    y: float

class ExternalSpace(BaseModel):
    room_id: str
    space_type: RoomType
    x: float
    y: float
    width: float
    depth: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

class FloorPlanFloor(BaseModel):
    floor_number: int
    walls: List[Wall] = Field(default_factory=list)
    openings: List[Opening] = Field(default_factory=list)
    room_boundaries: List[RoomBoundary] = Field(default_factory=list)
    labels: List[Label] = Field(default_factory=list)
    dimensions: List[Dimension] = Field(default_factory=list)
    external_spaces: List[ExternalSpace] = Field(default_factory=list)

class FloorPlan(BaseModel):
    plot_width: float
    plot_depth: float
    building_width: float
    building_depth: float
    floors: List[FloorPlanFloor] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
