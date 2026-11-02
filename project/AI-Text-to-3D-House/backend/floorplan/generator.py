from typing import List, Optional
import uuid
from ..layout.models import HouseLayout, RoomType
from .models import (
    FloorPlan, FloorPlanFloor, Wall, RoomBoundary, Label,
    Dimension, Opening, OpeningType, ExternalSpace
)
from .geometry import extract_walls, get_shared_boundary, find_exterior_wall_segment, find_all_exterior_wall_segments, eps

WALL_THICKNESS = 0.20
DOOR_WIDTH = 0.90
WINDOW_WIDTH = 1.20

def generate_floorplan(layout: HouseLayout) -> FloorPlan:
    fp = FloorPlan(
        plot_width=layout.plot_width or layout.building_width,
        plot_depth=layout.plot_depth or layout.building_depth,
        building_width=layout.building_width,
        building_depth=layout.building_depth,
        metadata={**(layout.metadata if layout.metadata else {}), "generated_from_layout": True}
    )
    
    for f in layout.floors:
        fp_floor = FloorPlanFloor(floor_number=f.floor_number)
        
        # 1. Walls
        rooms_for_walls = [r for r in f.rooms if r.room_type != RoomType.main_entrance]
        raw_walls = extract_walls(rooms_for_walls, layout.building_width, layout.building_depth)
        for idx, rw in enumerate(raw_walls):
            fp_floor.walls.append(Wall(
                id=f"wall_f{f.floor_number}_{idx}",
                x1=rw["x1"],
                y1=rw["y1"],
                x2=rw["x2"],
                y2=rw["y2"],
                thickness=WALL_THICKNESS,
                is_exterior=rw["is_exterior"]
            ))
            
        def find_host_wall(is_vertical: bool, fixed: float, start: float, end: float) -> str:
            for w in fp_floor.walls:
                if is_vertical and abs(w.x1 - w.x2) < eps and abs(w.x1 - fixed) < eps:
                    if w.y1 <= start + eps and w.y2 >= end - eps:
                        return w.id
                elif not is_vertical and abs(w.y1 - w.y2) < eps and abs(w.y1 - fixed) < eps:
                    if w.x1 <= start + eps and w.x2 >= end - eps:
                        return w.id
            return "unknown_wall"

        door_count = 0
        window_count = 0
        
        # 2. Rooms, Labels, Dimensions, External Spaces
        for r in f.rooms:
            if r.room_type == RoomType.main_entrance:
                continue
                
            is_external = r.room_type in (RoomType.parking, RoomType.balcony, RoomType.terrace)
            
            if is_external:
                fp_floor.external_spaces.append(ExternalSpace(
                    room_id=r.id,
                    space_type=r.room_type,
                    x=r.x,
                    y=r.y,
                    width=r.width,
                    depth=r.depth,
                    metadata=r.metadata
                ))
            else:
                fp_floor.room_boundaries.append(RoomBoundary(
                    room_id=r.id,
                    room_type=r.room_type,
                    x=r.x,
                    y=r.y,
                    width=r.width,
                    depth=r.depth
                ))
                
            # Label
            label_text = r.name
            if r.room_type == RoomType.parking and "capacity" in r.metadata:
                label_text += f"\n{r.metadata['capacity']} Cars"
                
            fp_floor.labels.append(Label(
                room_id=r.id,
                text=label_text,
                x=r.x + r.width / 2.0,
                y=r.y + r.depth / 2.0
            ))
            
            # Dimension
            fp_floor.dimensions.append(Dimension(
                room_id=r.id,
                text=f"{r.width}m x {r.depth}m",
                x=r.x + r.width / 2.0,
                y=r.y + r.depth / 2.0 + 0.5
            ))
            
        # 3. Doors (Internal Openings)
        # We only place doors based on explicit geometric adjacency + metadata intent
        # For determinism, we sort rooms to ensure reproducible door pairs
        processed_pairs = set()
        
        for r1 in f.rooms:
            if r1.room_type in (RoomType.parking, RoomType.terrace, RoomType.main_entrance):
                continue
                
            for adj_type in r1.metadata.get("adjacent_to", []):
                # Find the geometric neighbor matching this type
                for r2 in f.rooms:
                    if r2.room_type.value == adj_type and r2.id != r1.id:
                        if r2.room_type == RoomType.main_entrance:
                            continue
                        pair_id = tuple(sorted([r1.id, r2.id]))
                        if pair_id in processed_pairs:
                            continue
                            
                        boundary = get_shared_boundary(r1, r2)
                        if boundary:
                            processed_pairs.add(pair_id)
                            # Place door exactly in the middle of the shared boundary
                            b_len = boundary["end"] - boundary["start"]
                            if b_len >= DOOR_WIDTH:
                                mid = boundary["start"] + b_len / 2.0
                                is_vert = boundary["type"] == "vertical"
                                host_id = find_host_wall(is_vert, boundary["fixed"], boundary["start"], boundary["end"])
                                
                                dx = boundary["fixed"] if is_vert else mid - DOOR_WIDTH / 2.0
                                dy = mid - DOOR_WIDTH / 2.0 if is_vert else boundary["fixed"]
                                
                                door_count += 1
                                fp_floor.openings.append(Opening(
                                    id=f"door_f{f.floor_number}_{door_count}",
                                    opening_type=OpeningType.door,
                                    host_wall_id=host_id,
                                    x=dx,
                                    y=dy,
                                    width=DOOR_WIDTH,
                                    metadata={"rooms": [r1.id, r2.id]}
                                ))
                                
        # Balcony doors
        for r1 in f.rooms:
            if r1.room_type == RoomType.balcony:
                # Find any touching bedroom or corridor
                for r2 in f.rooms:
                    if r2.room_type in (RoomType.bedroom, RoomType.master_bedroom, RoomType.corridor):
                        pair_id = tuple(sorted([r1.id, r2.id]))
                        if pair_id not in processed_pairs:
                            boundary = get_shared_boundary(r1, r2)
                            if boundary:
                                processed_pairs.add(pair_id)
                                b_len = boundary["end"] - boundary["start"]
                                if b_len >= DOOR_WIDTH:
                                    mid = boundary["start"] + b_len / 2.0
                                    is_vert = boundary["type"] == "vertical"
                                    host_id = find_host_wall(is_vert, boundary["fixed"], boundary["start"], boundary["end"])
                                    
                                    dx = boundary["fixed"] if is_vert else mid - DOOR_WIDTH / 2.0
                                    dy = mid - DOOR_WIDTH / 2.0 if is_vert else boundary["fixed"]
                                    
                                    door_count += 1
                                    fp_floor.openings.append(Opening(
                                        id=f"door_f{f.floor_number}_{door_count}",
                                        opening_type=OpeningType.door,
                                        host_wall_id=host_id,
                                        x=dx,
                                        y=dy,
                                        width=DOOR_WIDTH,
                                        metadata={"rooms": [r1.id, r2.id]}
                                    ))
                                
        # 5. Main Entrance (Do this BEFORE Windows to avoid overlap)
        entrance_rooms = [r for r in f.rooms if r.room_type == RoomType.main_entrance]
        if entrance_rooms:
            ent = entrance_rooms[0]
            # Entrance touches Living room
            living = next((r for r in f.rooms if r.room_type == RoomType.living), None)
            if living:
                boundary = get_shared_boundary(ent, living)
                if boundary:
                    b_len = boundary["end"] - boundary["start"]
                    if b_len >= DOOR_WIDTH:
                        mid = boundary["start"] + b_len / 2.0
                        is_vert = boundary["type"] == "vertical"
                        host_id = find_host_wall(is_vert, boundary["fixed"], boundary["start"], boundary["end"])
                        
                        ex = boundary["fixed"] if is_vert else mid - DOOR_WIDTH / 2.0
                        ey = mid - DOOR_WIDTH / 2.0 if is_vert else boundary["fixed"]
                        
                        door_count += 1
                        fp_floor.openings.append(Opening(
                            id=f"entrance_f{f.floor_number}_{door_count}",
                            opening_type=OpeningType.entrance,
                            host_wall_id=host_id,
                            x=ex,
                            y=ey,
                            width=DOOR_WIDTH,
                            metadata={"room": living.id, "is_main": True}
                        ))

        # 4. Windows (External Openings)
        # Living, Bedroom, Kitchen get windows if they touch the exterior
        window_candidates = (RoomType.living, RoomType.bedroom, RoomType.master_bedroom, RoomType.kitchen, RoomType.bathroom)
        for r in f.rooms:
            if r.room_type in window_candidates:
                ext_segments = find_all_exterior_wall_segments(r, f.rooms)
                
                # Check for available segments
                placed_window = False
                for ext_wall in ext_segments:
                    is_vert = ext_wall["type"] == "vertical"
                    
                    # See if there are existing openings on this exact wall segment that might overlap
                    overlap = False
                    for op in fp_floor.openings:
                        op_is_vert = op.width > 0 and abs(op.x - ext_wall["fixed"]) < eps if is_vert else abs(op.y - ext_wall["fixed"]) < eps
                        if op_is_vert:
                            op_start = op.y if is_vert else op.x
                            op_end = op_start + op.width
                            
                            # Check overlap with the center area we want to place window
                            mid = ext_wall["start"] + (ext_wall["end"] - ext_wall["start"]) / 2.0
                            win_start = mid - WINDOW_WIDTH / 2.0
                            win_end = mid + WINDOW_WIDTH / 2.0
                            
                            if not (win_end <= op_start + eps or win_start >= op_end - eps):
                                overlap = True
                                break
                    
                    if not overlap:
                        b_len = ext_wall["end"] - ext_wall["start"]
                        if b_len >= 0.8:
                            # Determine target window width based on room type
                            target_w = 1.2
                            if r.room_type == RoomType.living:
                                target_w = 2.4
                            elif r.room_type in (RoomType.bedroom, RoomType.master_bedroom):
                                target_w = 1.8
                            elif r.room_type == RoomType.bathroom:
                                target_w = 0.6
                                
                            # Constrain by wall length
                            win_w = min(target_w, b_len - 0.4)
                            win_w = max(0.6, win_w) # minimum 0.6
                            
                            mid = ext_wall["start"] + b_len / 2.0
                            host_id = find_host_wall(is_vert, ext_wall["fixed"], ext_wall["start"], ext_wall["end"])
                            
                            wx = ext_wall["fixed"] if is_vert else mid - win_w / 2.0
                            wy = mid - win_w / 2.0 if is_vert else ext_wall["fixed"]
                            
                            window_count += 1
                            fp_floor.openings.append(Opening(
                                id=f"win_f{f.floor_number}_{window_count}",
                                opening_type=OpeningType.window,
                                host_wall_id=host_id,
                                x=wx,
                                y=wy,
                                width=win_w,
                                metadata={"room": r.id}
                            ))
                            placed_window = True
                            break
                            
                if not placed_window:
                    print(f"ROOM: {r.id} WINDOW: NOT POSSIBLE REASON: No valid exterior wall segment")

        fp.floors.append(fp_floor)
        
    return fp
