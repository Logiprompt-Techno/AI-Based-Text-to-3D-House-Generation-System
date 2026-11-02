from typing import List, Dict, Set
from .models import Room, HouseLayout, RoomType

def rects_overlap(x1: float, y1: float, w1: float, d1: float, x2: float, y2: float, w2: float, d2: float, eps: float = 1e-5) -> bool:
    """
    Checks if two rectangles have a positive-area intersection.
    Touching edges (e.g. x1+w1 == x2) do NOT count as overlap.
    """
    if x1 >= x2 + w2 - eps or x2 >= x1 + w1 - eps:
        return False
    if y1 >= y2 + d2 - eps or y2 >= y1 + d1 - eps:
        return False
    return True

def rects_touch(r1: Room, r2: Room, eps: float = 1e-5) -> bool:
    """
    Checks if two rectangles share a boundary segment (touch).
    """
    if r1.floor != r2.floor:
        return False
        
    x_overlap = not (r1.x >= r2.x + r2.width - eps or r2.x >= r1.x + r1.width - eps)
    y_overlap = not (r1.y >= r2.y + r2.depth - eps or r2.y >= r1.y + r1.depth - eps)
    
    touches_left_right = (abs(r1.x + r1.width - r2.x) < eps or abs(r2.x + r2.width - r1.x) < eps) and y_overlap
    touches_top_bottom = (abs(r1.y + r1.depth - r2.y) < eps or abs(r2.y + r2.depth - r1.y) < eps) and x_overlap
    
    return touches_left_right or touches_top_bottom

def build_adjacency_graph(floor_rooms: List[Room]) -> Dict[str, List[str]]:
    graph = {r.id: [] for r in floor_rooms}
    for i in range(len(floor_rooms)):
        for j in range(i + 1, len(floor_rooms)):
            if rects_touch(floor_rooms[i], floor_rooms[j]):
                graph[floor_rooms[i].id].append(floor_rooms[j].id)
                graph[floor_rooms[j].id].append(floor_rooms[i].id)
    return graph

def find_reachable(start_id: str, graph: Dict[str, List[str]]) -> Set[str]:
    visited = set()
    queue = [start_id]
    while queue:
        curr = queue.pop(0)
        if curr not in visited:
            visited.add(curr)
            queue.extend([n for n in graph.get(curr, []) if n not in visited])
    return visited

def count_bedrooms(layout: HouseLayout) -> int:
    return sum(1 for f in layout.floors for r in f.rooms if r.room_type in (RoomType.master_bedroom, RoomType.bedroom))

def count_bathrooms(layout: HouseLayout) -> int:
    return sum(1 for f in layout.floors for r in f.rooms if r.room_type == RoomType.bathroom)

def count_balconies(layout: HouseLayout) -> int:
    return sum(1 for f in layout.floors for r in f.rooms if r.room_type == RoomType.balcony)

def count_terraces(layout: HouseLayout) -> int:
    return sum(1 for f in layout.floors for r in f.rooms if r.room_type == RoomType.terrace)

def count_parking_capacity(layout: HouseLayout) -> int:
    capacity = 0
    for f in layout.floors:
        for r in f.rooms:
            if r.room_type == RoomType.parking:
                capacity += r.metadata.get("capacity", 0)
    return capacity

def validate_layout(layout: HouseLayout, req=None) -> bool:
    if not layout.floors:
        raise ValueError("House must have at least one floor.")
        
    staircases = []
    
    for floor in layout.floors:
        if floor.floor_number < 1:
            raise ValueError(f"Invalid floor number: {floor.floor_number}")
        if floor.width <= 0 or floor.depth <= 0:
            raise ValueError(f"Floor {floor.floor_number} has non-positive dimensions.")
            
        graph = build_adjacency_graph(floor.rooms)
        rooms_by_type = {}
        for room in floor.rooms:
            rooms_by_type.setdefault(room.room_type.value, []).append(room)
            
            if room.floor != floor.floor_number:
                raise ValueError(f"Room {room.id} claims floor {room.floor} but is on {floor.floor_number}.")
            if room.width <= 0 or room.depth <= 0:
                raise ValueError(f"Room {room.id} has non-positive dimensions.")
            if room.x < 0 or room.y < 0:
                raise ValueError(f"Room {room.id} has negative coordinates.")
            
            is_external = room.room_type in (RoomType.parking, RoomType.balcony, RoomType.terrace)
            if not is_external:
                if room.x + room.width > layout.building_width or room.y + room.depth > layout.building_depth:
                    raise ValueError(f"Room {room.id} extends outside the building footprint.")
            else:
                # External room inside plot
                if layout.plot_width and layout.plot_depth:
                    if room.x + room.width > layout.plot_width or room.y + room.depth > layout.plot_depth:
                        raise ValueError(f"External room {room.id} extends outside plot footprint.")
                
            # Verify Metadata Adjacency geometrically
            for adj_type in room.metadata.get("adjacent_to", []):
                # We need to find at least one room of adj_type that actually touches this room
                actual_adj_ids = graph[room.id]
                actual_adj_types = [r.room_type.value for r in floor.rooms if r.id in actual_adj_ids]
                if adj_type not in actual_adj_types:
                    raise ValueError(f"Metadata conflict: {room.id} claims adjacency to {adj_type}, but no such geometric contact exists.")
                    
            for j in range(floor.rooms.index(room) + 1, len(floor.rooms)):
                other = floor.rooms[j]
                if rects_overlap(room.x, room.y, room.width, room.depth, other.x, other.y, other.width, other.depth):
                    raise ValueError(f"Room {room.id} overlaps with {other.id}.")

        # Floor-specific circulation checks
        if floor.floor_number == 1:
            living_rooms = rooms_by_type.get(RoomType.living.value, [])
            if living_rooms:
                living = living_rooms[0]
                reachable = find_reachable(living.id, graph)
                
                # Living should reach corridor or private rooms
                private_types = [RoomType.master_bedroom.value, RoomType.bedroom.value, RoomType.bathroom.value, RoomType.corridor.value, RoomType.staircase.value]
                reached_types = [r.room_type.value for r in floor.rooms if r.id in reachable]
                
                for pt in private_types:
                    if rooms_by_type.get(pt) and pt not in reached_types:
                        raise ValueError(f"Ground floor connectivity failed: {pt} is completely isolated from Living room.")
        else:
            upper_stairs = rooms_by_type.get(RoomType.staircase.value, [])
            if upper_stairs:
                stair = upper_stairs[0]
                reachable = find_reachable(stair.id, graph)
                
                private_types = [RoomType.bedroom.value, RoomType.bathroom.value, RoomType.corridor.value]
                reached_types = [r.room_type.value for r in floor.rooms if r.id in reachable]
                
                for pt in private_types:
                    if rooms_by_type.get(pt) and pt not in reached_types:
                        raise ValueError(f"Upper floor connectivity failed: {pt} is completely isolated from Staircase.")
                        
        staircase = rooms_by_type.get(RoomType.staircase.value)
        if staircase:
            staircases.append(staircase[0])
            
        # Balcony touches building check
        balconies = rooms_by_type.get(RoomType.balcony.value, [])
        for balc in balconies:
            # Must geometrically touch at least one interior room
            actual_adj_ids = graph[balc.id]
            interior_adjs = [r for r in floor.rooms if r.id in actual_adj_ids and r.room_type != RoomType.balcony]
            if not interior_adjs:
                raise ValueError(f"Balcony {balc.id} floats and does not touch any interior room facade.")
                
    # Multi-floor staircase alignment
    if len(staircases) > 1:
        s0 = staircases[0]
        for s1 in staircases[1:]:
            if s0.x != s1.x or s0.y != s1.y or s0.width != s1.width or s0.depth != s1.depth:
                raise ValueError(f"Staircase alignment mismatch between floors.")

    if req is not None:
        if req.floors is not None and len(layout.floors) != req.floors:
            raise ValueError(f"Expected {req.floors} floors, got {len(layout.floors)}")
        
        beds = count_bedrooms(layout)
        if req.bedrooms is not None and beds != req.bedrooms:
            raise ValueError(f"Expected {req.bedrooms} bedrooms, got {beds}")
            
        baths = count_bathrooms(layout)
        if req.bathrooms is not None and baths != req.bathrooms:
            raise ValueError(f"Expected {req.bathrooms} bathrooms, got {baths}")
            
        balconies = count_balconies(layout)
        if req.balconies is not None and balconies != req.balconies:
            raise ValueError(f"Expected {req.balconies} balconies, got {balconies}")
            
        terraces = count_terraces(layout)
        if req.terraces is not None and terraces != req.terraces:
            raise ValueError(f"Expected {req.terraces} terraces, got {terraces}")
            
        parking = count_parking_capacity(layout)
        if req.parking_spaces is not None:
            parking_rooms = [r for f in layout.floors for r in f.rooms if r.room_type == RoomType.parking]
            if req.parking_spaces == 0 and len(parking_rooms) > 0:
                raise ValueError("Expected 0 parking spaces, but found parking rooms.")
            if req.parking_spaces > 0 and parking != req.parking_spaces:
                raise ValueError(f"Expected {req.parking_spaces} parking capacity, got {parking}")

        if req.floors and req.floors > 1:
            st = sum(1 for f in layout.floors for r in f.rooms if r.room_type == RoomType.staircase)
            if st == 0:
                raise ValueError("Expected a staircase for multi-floor house, got none.")

    return True
