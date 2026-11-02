from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

class RequirementOutput(BaseModel):
    house_style: Optional[str] = None
    house_type: Optional[str] = None
    floors: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    parking_spaces: Optional[int] = None
    balconies: Optional[int] = None
    terraces: Optional[int] = None
    plot_width: Optional[float] = None
    plot_depth: Optional[float] = None
    road_side: Optional[str] = None
    entrance_direction: Optional[str] = None
    roof_type: Optional[str] = None
    special_requirements: List[str] = Field(default_factory=list)

    source_text: str = ""
    parser_version: str = "1.0.0"

    @field_validator('floors')
    def validate_floors(cls, v):
        if v is not None and v < 1:
            raise ValueError("Floors must be >= 1")
        return v

    @field_validator('bedrooms', 'bathrooms', 'parking_spaces', 'balconies', 'terraces')
    def validate_non_negative(cls, v, info):
        if v is not None and v < 0:
            raise ValueError(f"{info.field_name} must be >= 0")
        return v

    @field_validator('plot_width', 'plot_depth')
    def validate_plot_dims(cls, v, info):
        if v is not None and v <= 0:
            raise ValueError(f"{info.field_name} must be > 0")
        return v
