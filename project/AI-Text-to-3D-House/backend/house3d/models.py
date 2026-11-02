from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class Vector3(BaseModel):
    x: float
    y: float
    z: float

class Dimension3D(BaseModel):
    width: float   # X axis
    depth: float   # Y axis
    height: float  # Z axis

class Object3D(BaseModel):
    id: str
    type: str # 'wall', 'slab', 'roof', 'door', 'window', 'staircase', 'parking', 'balcony'
    role: str # 'exterior', 'interior', 'main_entrance', etc.
    position: Vector3
    dimensions: Dimension3D
    material: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Camera3D(BaseModel):
    target: Vector3
    position: Vector3
    fov: float
    lens: float

class Lighting3D(BaseModel):
    sun_position: Vector3
    sun_energy: float
    ambient_energy: float

class Scene3D(BaseModel):
    objects: List[Object3D] = Field(default_factory=list)
    camera: Optional[Camera3D] = None
    lighting: Optional[Lighting3D] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
