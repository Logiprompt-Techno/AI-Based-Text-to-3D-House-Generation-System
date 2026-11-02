from enum import Enum
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class RoomType(str, Enum):
    living = "living"
    family_living = "family_living"
    dining = "dining"
    kitchen = "kitchen"
    master_bedroom = "master_bedroom"
    bedroom = "bedroom"
    bathroom = "bathroom"
    staircase = "staircase"
    corridor = "corridor"
    balcony = "balcony"
    terrace = "terrace"
    parking = "parking"
    utility = "utility"
    prayer_room = "prayer_room"
    home_office = "home_office"
    servant_room = "servant_room"
    main_entrance = "main_entrance"
    other = "other"

class Room(BaseModel):
    id: str
    name: str
    room_type: RoomType
    floor: int
    x: float
    y: float
    width: float
    depth: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

class FloorLayout(BaseModel):
    floor_number: int
    width: float
    depth: float
    rooms: List[Room] = Field(default_factory=list)

class HouseLayout(BaseModel):
    floors: List[FloorLayout] = Field(default_factory=list)
    plot_width: Optional[float] = None
    plot_depth: Optional[float] = None
    building_width: float
    building_depth: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
