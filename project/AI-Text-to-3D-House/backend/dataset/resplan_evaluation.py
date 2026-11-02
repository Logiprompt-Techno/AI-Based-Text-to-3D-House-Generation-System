import os
import json
from datetime import datetime
from collections import Counter
from backend.dataset.resplan_loader import ResPlanLoader
from backend.dataset.resplan_adapter import ResPlanAdapter
from backend.layout.generator import generate_layout
from backend.requirements.models import RequirementOutput
from backend.layout.models import RoomType

def evaluate_resplan_vs_generator(dataset_dir: str, report_out: str, sample_size: int = 100):
    loader = ResPlanLoader(dataset_dir)
    loader.load_splits()
    loader.load_data()
    adapter = ResPlanAdapter()

    resplan_metrics = {
        'room_type_counts': Counter(),
        'total_rooms': [],
        'total_area': [],
        'room_connections': []
    }

    # Evaluate ResPlan subset
    test_ids = loader.test_ids[:sample_size] if loader.test_ids else list(range(min(sample_size, loader.sample_count)))
    
    # test_ids are actually integers representing the original dataset IDs, but loader.inspect_sample takes an array index.
    # To be safe, we'll just evaluate the first `sample_size` elements in the dataset as a representative sample.
    sample_indices = list(range(min(sample_size, loader.sample_count)))
    
    valid_samples = 0
    for idx in sample_indices:
        try:
            sample_safe = loader.inspect_sample(idx)
            house, _ = adapter.adapt(sample_safe)
            
            # Count rooms
            total_r = 0
            for f in house.floors:
                total_r += len(f.rooms)
                for r in f.rooms:
                    resplan_metrics['room_type_counts'][r.room_type.value] += 1
            resplan_metrics['total_rooms'].append(total_r)
            
            # Area (from metadata)
            if 'resplan_area' in house.metadata:
                resplan_metrics['total_area'].append(house.metadata['resplan_area'])
                
            # Connections
            if 'resplan_graph' in house.metadata:
                edges = house.metadata['resplan_graph'].get('edges', [])
                resplan_metrics['room_connections'].append(len(edges))
                
            valid_samples += 1
        except Exception:
            pass

    # Evaluate Generator
    gen_metrics = {
        'room_type_counts': Counter(),
        'total_rooms': [],
        'total_area': [],
        'room_connections': []
    }
    
    # We create some deterministic requirements
    reqs = [
        RequirementOutput(bedrooms=1, bathrooms=1, floors=1, parking_spaces=1),
        RequirementOutput(bedrooms=2, bathrooms=1, floors=1, parking_spaces=1, balconies=1),
        RequirementOutput(bedrooms=3, bathrooms=2, floors=2, parking_spaces=2, balconies=1),
        RequirementOutput(bedrooms=4, bathrooms=3, floors=2, parking_spaces=2, balconies=2, terraces=1),
        RequirementOutput(bedrooms=2, bathrooms=2, floors=1, special_requirements=["home office", "utility room"])
    ]
    
    for req in reqs:
        house = generate_layout(req)
        total_r = 0
        for f in house.floors:
            total_r += len(f.rooms)
            for r in f.rooms:
                gen_metrics['room_type_counts'][r.room_type.value] += 1
        gen_metrics['total_rooms'].append(total_r)
        
        # Generator computes width and depth
        area = house.building_width * house.building_depth * len(house.floors)
        gen_metrics['total_area'].append(area)
        
        # Generator adjacency (based on adjacent_to metadata)
        conns = 0
        for f in house.floors:
            for r in f.rooms:
                adj = r.metadata.get('adjacent_to', [])
                conns += len(adj)
        # Undirected edges would be half, but let's just count total adjacency declarations
        gen_metrics['room_connections'].append(conns // 2)

    def avg(lst): return sum(lst) / len(lst) if lst else 0.0

    report = {
        "timestamp": datetime.now().isoformat(),
        "resplan_samples_evaluated": valid_samples,
        "generator_samples_evaluated": len(reqs),
        "metrics": {
            "resplan": {
                "room_type_distribution": dict(resplan_metrics['room_type_counts']),
                "avg_rooms_per_layout": avg(resplan_metrics['total_rooms']),
                "avg_area": avg(resplan_metrics['total_area']),
                "avg_connections_per_layout": avg(resplan_metrics['room_connections'])
            },
            "generator": {
                "room_type_distribution": dict(gen_metrics['room_type_counts']),
                "avg_rooms_per_layout": avg(gen_metrics['total_rooms']),
                "avg_area": avg(gen_metrics['total_area']),
                "avg_connections_per_layout": avg(gen_metrics['room_connections'])
            }
        },
        "limitations": [
            "ResPlan geometry uses exact polygons, Generator uses rectangular bounding boxes.",
            "Area in ResPlan is reported by dataset; Area in Generator is building_width * building_depth.",
            "Connections in ResPlan use topological graph edges; Generator uses metadata tags.",
            "Unavailable metrics: 3D features, roof shapes, detailed interior objects."
        ]
    }
    
    os.makedirs(os.path.dirname(report_out), exist_ok=True)
    with open(report_out, 'w') as f:
        json.dump(report, f, indent=4)
        
    return report

if __name__ == "__main__":
    DATASET_DIR = r"D:\2D AND 3D house Text-to-3D\datasets\resplan"
    REPORT_OUT = r"D:\2D AND 3D house Text-to-3D\project\AI-Text-to-3D-House\docs\resplan_evaluation_report.json"
    evaluate_resplan_vs_generator(DATASET_DIR, REPORT_OUT)
