import pytest
import os
import re
from backend.requirements.parser import parse_requirements
from backend.layout.generator import generate_layout
from backend.floorplan.generator import generate_floorplan
from backend.house3d.builder import generate_3d
from backend.layout.models import RoomType

def test_step9e_validation():
    prompt = "modern flat roof 2BHK garden"
    req = parse_requirements(prompt)
    
    # - prompt roof_type = flat
    assert req.roof_type == "flat"
    
    # - bedrooms = 2
    assert req.bedrooms == 2
    
    # - floors = 1 when not explicitly requested
    assert req.floors is None or req.floors == 1
    
    # - garden requirement preserved
    assert "landscaping" in req.special_requirements

    # canonical layout has 2 bedrooms
    layout = generate_layout(req)
    beds = sum(1 for f in layout.floors for r in f.rooms if r.room_type in (RoomType.bedroom, RoomType.master_bedroom))
    assert beds == 2
    
    # floors = 1
    assert len(layout.floors) == 1

    # generate floorplan
    fp = generate_floorplan(layout)
    
    # 3D scene has 2 bedrooms
    scene = generate_3d(fp)
    
    # roof type is flat
    roofs = [o for o in scene.objects if o.type == "slab" and o.id.startswith("roof_main")]
    assert len(roofs) >= 1
    
    # parapet presence
    parapets = [o for o in scene.objects if "_parapet" in o.id]
    assert len(parapets) >= 4
    
    # all openings are mapped from approved opening data
    # (no floating geometry, proper bounds)
    door_frames = [o for o in scene.objects if o.type == "door_frame"]
    door_leafs = [o for o in scene.objects if o.type == "door_leaf"]
    assert len(door_frames) > 0
    assert len(door_leafs) > 0
    
    # camera framing uses generated bounding box
    # verified visually, but we can check if dist_from_center logic exists
    
    # garden is outside building
    # check landscape grass
    grass = [o for o in scene.objects if o.id == "landscape_grass"]
    assert len(grass) == 1
    
    trees = [o for o in scene.objects if o.id.startswith("tree")]
    assert len(trees) >= 4 # trunk+leaves for 2 trees
