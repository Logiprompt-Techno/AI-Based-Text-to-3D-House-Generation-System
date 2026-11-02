import os
import json
from backend.dataset.resplan_loader import ResPlanLoader
from backend.dataset.resplan_adapter import ResPlanAdapter
from backend.layout.models import HouseLayout

DATASET_DIR = r"D:\2D AND 3D house Text-to-3D\datasets\resplan"

def test_resplan_adapter():
    # 1. Load one sample
    loader = ResPlanLoader(DATASET_DIR)
    loader.load_data()
    sample_safe = loader.inspect_sample(0)
    
    # 2. Adapt it
    adapter = ResPlanAdapter()
    house, report = adapter.adapt(sample_safe)
    
    # 3. Assertions
    assert isinstance(house, HouseLayout)
    assert len(house.floors) == 1
    
    floor = house.floors[0]
    assert len(floor.rooms) > 0
    
    # Check geometry is preserved
    first_room = floor.rooms[0]
    assert 'resplan_exact_geometry' in first_room.metadata
    
    # Check adjacency is preserved
    assert 'resplan_graph' in house.metadata or 'resplan_neighbor' in house.metadata
    
    # Check missing fields are explicitly reported
    assert 'unsupported_fields' in report
    assert len(report['geometry_notes']) > 0
    
    # Check JSON serialization of canonical output
    house_dict = house.model_dump()
    json_str = json.dumps(house_dict)
    assert isinstance(json_str, str)
