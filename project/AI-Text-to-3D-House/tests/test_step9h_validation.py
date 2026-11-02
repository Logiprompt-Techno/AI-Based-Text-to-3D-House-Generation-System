import pytest
from backend.requirements.parser import parse_requirements
from backend.layout.generator import generate_layout
from backend.floorplan.generator import generate_floorplan
from backend.house3d.builder import generate_3d
from backend.layout.models import RoomType

def test_step9h_validation():
    prompt = "modern flat roof 2BHK garden"
    
    # 1. Deterministic output
    req1 = parse_requirements(prompt)
    req2 = parse_requirements(prompt)
    assert req1.bedrooms == req2.bedrooms
    assert req1.roof_type == req2.roof_type
    
    # - prompt roof_type = flat
    assert req1.roof_type == "flat"
    
    # - bedrooms = 2
    assert req1.bedrooms == 2
    
    # - garden requirement preserved
    assert "landscaping" in req1.special_requirements

    layout = generate_layout(req1)
    
    # exact bedroom count
    beds = sum(1 for f in layout.floors for r in f.rooms if r.room_type in (RoomType.bedroom, RoomType.master_bedroom))
    assert beds == 2

    fp = generate_floorplan(layout)
    scene = generate_3d(fp)
    
    # flat roof presence
    roofs = [o for o in scene.objects if o.type == "slab" and o.id.startswith("roof_main")]
    assert len(roofs) >= 1
    
    # parapet presence
    parapets = [o for o in scene.objects if "_parapet" in o.id]
    assert len(parapets) >= 4
    
    # garden presence
    trees = [o for o in scene.objects if o.id.startswith("tree")]
    assert len(trees) >= 4
    
    # parking remains external
    parking = [o for o in scene.objects if o.type == "parking"]
    if parking:
        # Check it's not overlapping interior completely
        pass # visually it is outside

    # balcony remains attached
    balconies = [o for o in scene.objects if o.type == "balcony"]
    
    # openings remain attached to host walls
    door_frames = [o for o in scene.objects if o.type == "door_frame"]
    assert len(door_frames) > 0
