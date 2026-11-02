from typing import Dict, Any, Tuple, List
from backend.layout.models import HouseLayout, FloorLayout, Room, RoomType

class ResPlanAdapter:
    def __init__(self):
        # Map ResPlan room types to our canonical RoomType enum
        self.ROOM_TYPE_MAP = {
            'living': RoomType.living,
            'kitchen': RoomType.kitchen,
            'bedroom': RoomType.bedroom,
            'bathroom': RoomType.bathroom,
            'balcony': RoomType.balcony,
            'parking': RoomType.parking,
        }
        
    def adapt(self, sample: Dict[str, Any]) -> Tuple[HouseLayout, Dict[str, Any]]:
        """
        Attempts to map a JSON-safe ResPlan sample into the canonical HouseLayout.
        Returns:
            (HouseLayout, report)
        """
        report = {
            'unsupported_fields': [],
            'geometry_notes': [],
            'adjacency_notes': [],
            'mapped_rooms': 0
        }
        
        # ResPlan is typically single-story per sample unless otherwise specified.
        floor = FloorLayout(floor_number=0, width=0, depth=0, rooms=[])
        
        # Keep track of min/max coordinates to compute overall building width/depth
        min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')
        
        room_counter = 0
        
        for key, value in sample.items():
            if key in ['id', 'area', 'net_area', 'wall_depth', 'neighbor', 'graph']:
                # Metadata / Adjacency handled separately or placed in House metadata
                continue
                
            # If it's a room/element geometry, value is a dict with type and coordinates
            if isinstance(value, dict) and 'type' in value and 'coordinates' in value:
                room_type = self.ROOM_TYPE_MAP.get(key, RoomType.other)
                
                # ResPlan has exact polygonal coordinates.
                # Canonical representation only supports rectangular bounding boxes (x, y, width, depth).
                # We calculate the bounding box and preserve exact geometry in metadata.
                coords = value['coordinates']
                
                # Flatten coords to find min/max
                all_x = []
                all_y = []
                if value['type'] == 'Polygon':
                    for point in coords[0]:
                        all_x.append(point[0])
                        all_y.append(point[1])
                elif value['type'] == 'MultiPolygon':
                    for poly in coords:
                        for point in poly[0]:
                            all_x.append(point[0])
                            all_y.append(point[1])
                            
                if not all_x or not all_y:
                    continue
                    
                rx_min, ry_min = min(all_x), min(all_y)
                rx_max, ry_max = max(all_x), max(all_y)
                
                width = rx_max - rx_min
                depth = ry_max - ry_min
                
                # Update global bounds
                min_x = min(min_x, rx_min)
                min_y = min(min_y, ry_min)
                max_x = max(max_x, rx_max)
                max_y = max(max_y, ry_max)
                
                room = Room(
                    id=f"{key}_{room_counter}",
                    name=key,
                    room_type=room_type,
                    floor=0,
                    x=rx_min,
                    y=ry_min,
                    width=width,
                    depth=depth,
                    metadata={
                        "resplan_exact_geometry": value  # Preserving source geometry
                    }
                )
                floor.rooms.append(room)
                room_counter += 1
                report['mapped_rooms'] += 1
                
                if room_type == RoomType.other:
                    report['unsupported_fields'].append(f"Room type '{key}' mapped to 'other'")
            else:
                report['unsupported_fields'].append(f"Unrecognized data format for key '{key}'")
                
        # Overall dimensions
        b_width = (max_x - min_x) if max_x >= min_x else 0
        b_depth = (max_y - min_y) if max_y >= min_y else 0
        floor.width = b_width
        floor.depth = b_depth
        
        # Build metadata from adjacency and sample metadata
        house_meta = {}
        if 'graph' in sample:
            house_meta['resplan_graph'] = sample['graph']
            report['adjacency_notes'].append("NetworkX graph preserved in metadata.")
        if 'neighbor' in sample:
            house_meta['resplan_neighbor'] = sample['neighbor']
            
        if 'id' in sample: house_meta['resplan_id'] = sample['id']
        if 'area' in sample: house_meta['resplan_area'] = sample['area']
        if 'net_area' in sample: house_meta['resplan_net_area'] = sample['net_area']
        if 'wall_depth' in sample: house_meta['resplan_wall_depth'] = sample['wall_depth']
        
        report['geometry_notes'].append(
            "Canonical layout requires (x,y,width,depth). ResPlan uses arbitrary Polygons. "
            "Polygons were approximated to bounding boxes. Exact geometries stored in room metadata."
        )

        house = HouseLayout(
            floors=[floor],
            building_width=b_width,
            building_depth=b_depth,
            metadata=house_meta
        )
        
        return house, report
