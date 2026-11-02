from typing import List, Optional, Tuple, Dict, Any
from ..requirements.models import RequirementOutput
from .models import RoomType, Room, FloorLayout, HouseLayout
import copy

def get_base_dimensions(rtype: RoomType) -> Tuple[float, float]:
    """Returns baseline (width, depth) for a room type."""
    if rtype == RoomType.living: return (5.0, 4.5)
    if rtype == RoomType.dining: return (4.0, 4.0)
    if rtype == RoomType.kitchen: return (3.5, 3.5)
    if rtype == RoomType.master_bedroom: return (4.0, 4.0)
    if rtype == RoomType.bedroom: return (3.5, 3.5)
    if rtype == RoomType.bathroom: return (2.5, 1.5)
    if rtype == RoomType.staircase: return (2.5, 4.0)
    if rtype == RoomType.main_entrance: return (2.0, 2.0)
    if rtype == RoomType.home_office: return (3.0, 3.0)
    if rtype == RoomType.prayer_room: return (2.0, 2.0)
    if rtype == RoomType.utility: return (2.5, 2.0)
    if rtype == RoomType.servant_room: return (2.5, 2.5)
    if rtype == RoomType.family_living: return (4.0, 4.0)
    return (3.0, 3.0)

def create_room(type_enum: RoomType, name: str, prefix: str, idx: int) -> dict:
    w, d = get_base_dimensions(type_enum)
    return {
        "id": f"{prefix}_{type_enum.value}_{idx}",
        "name": name,
        "type": type_enum,
        "w": w,
        "d": d,
        "x": 0.0,
        "y": 0.0,
        "meta": {}
    }

def generate_layout(req: RequirementOutput) -> HouseLayout:
    num_floors = req.floors if req.floors and req.floors > 0 else 1

    # ==========================================
    # 1. ROOM PROGRAM GENERATION
    # ==========================================
    ground_rooms = []
    upper_rooms = []
    external_rooms = []
    unmapped = []
    
    # Entrance
    ground_rooms.append(create_room(RoomType.main_entrance, "Main Entrance", "ground", 1))
    ground_rooms.append(create_room(RoomType.living, "Living Room", "ground", 2))
    ground_rooms.append(create_room(RoomType.dining, "Dining Room", "ground", 3))
    ground_rooms.append(create_room(RoomType.kitchen, "Kitchen", "ground", 4))
    
    beds_needed = req.bedrooms if req.bedrooms else 0
    if beds_needed > 0:
        ground_rooms.append(create_room(RoomType.master_bedroom, "Master Bedroom", "ground", 5))
        beds_needed -= 1
        
    b_idx = 1
    while beds_needed > 0:
        if num_floors > 1:
            upper_rooms.append(create_room(RoomType.bedroom, f"Bedroom {b_idx + 1}", "upper", b_idx))
        else:
            ground_rooms.append(create_room(RoomType.bedroom, f"Bedroom {b_idx + 1}", "ground", 5 + b_idx))
        beds_needed -= 1
        b_idx += 1
        
    baths_needed = req.bathrooms if req.bathrooms else 0
    if baths_needed > 0:
        ground_rooms.append(create_room(RoomType.bathroom, "Bathroom 1", "ground", 6))
        baths_needed -= 1
        
    bath_idx = 1
    while baths_needed > 0:
        if num_floors > 1:
            upper_rooms.append(create_room(RoomType.bathroom, f"Bathroom {bath_idx + 1}", "upper", bath_idx))
        else:
            ground_rooms.append(create_room(RoomType.bathroom, f"Bathroom {bath_idx + 1}", "ground", 6 + bath_idx))
        baths_needed -= 1
        bath_idx += 1

    has_stairs = num_floors > 1
    if has_stairs:
        ground_rooms.append(create_room(RoomType.staircase, "Staircase", "ground", 7))
        upper_rooms.insert(0, create_room(RoomType.staircase, "Staircase", "upper", 1))
        
    for i in range(req.parking_spaces or 0):
        er = create_room(RoomType.parking, f"Parking {i+1}", "ext", i+1)
        er["meta"]["capacity"] = 1
        external_rooms.append(er)
        
    for i in range(req.balconies or 0):
        external_rooms.append(create_room(RoomType.balcony, f"Balcony {i+1}", "ext", i+1))
        
    for i in range(req.terraces or 0):
        external_rooms.append(create_room(RoomType.terrace, f"Terrace {i+1}", "ext", i+1))
        
    for i, sr in enumerate(req.special_requirements):
        sr_low = sr.lower()
        if "home office" in sr_low: ground_rooms.append(create_room(RoomType.home_office, "Home Office", "ground", 10+i))
        elif "prayer room" in sr_low: ground_rooms.append(create_room(RoomType.prayer_room, "Prayer Room", "ground", 10+i))
        elif "utility room" in sr_low: ground_rooms.append(create_room(RoomType.utility, "Utility Room", "ground", 10+i))
        elif "servant room" in sr_low: ground_rooms.append(create_room(RoomType.servant_room, "Servant Room", "ground", 10+i))
        elif "family living" in sr_low:
            if num_floors > 1: upper_rooms.append(create_room(RoomType.family_living, "Family Living", "upper", 10+i))
            else: ground_rooms.append(create_room(RoomType.family_living, "Family Living", "ground", 10+i))
        else:
            unmapped.append(sr)

    # ==========================================
    # 2. TOPOLOGICAL PLACEMENT (GROUND FLOOR)
    # ==========================================
    gf_layout = []
    
    def extract_room(rtype, name=None):
        for r in ground_rooms:
            if r["type"] == rtype and (name is None or r["name"] == name):
                ground_rooms.remove(r)
                return r
        return None
        
    entrance = extract_room(RoomType.main_entrance)
    living = extract_room(RoomType.living)
    dining = extract_room(RoomType.dining)
    kitchen = extract_room(RoomType.kitchen)
    staircase = extract_room(RoomType.staircase)
    master = extract_room(RoomType.master_bedroom)
    bathroom = extract_room(RoomType.bathroom)
    
    # Establish grid dimensions
    stair_w = staircase["w"] if staircase else 2.5
    stair_d = staircase["d"] if staircase else 4.0
    din_w = dining["w"] if dining else 4.0
    din_d = dining["d"] if dining else 4.0
    kit_w = kitchen["w"] if kitchen else 3.5
    kit_d = kitchen["d"] if kitchen else 3.5
    
    # Front Zone
    ent_y = 0.0
    liv_y = ent_y + entrance["d"] if entrance else 0.0
    
    if entrance:
        entrance["x"] = stair_w + (din_w / 2) - (entrance["w"] / 2)
        entrance["y"] = ent_y
        entrance["meta"]["adjacent_to"] = [RoomType.living.value]
        gf_layout.append(entrance)
        
    if living:
        living["x"] = stair_w
        living["y"] = liv_y
        living["meta"]["adjacent_to"] = [RoomType.main_entrance.value, RoomType.dining.value]
        gf_layout.append(living)
        
    # Middle Zone
    mid_y = liv_y + (living["d"] if living else 4.5)
    
    if dining:
        dining["x"] = stair_w
        dining["y"] = mid_y
        dining["meta"]["adjacent_to"] = [RoomType.living.value]
        gf_layout.append(dining)
        
    if staircase:
        staircase["x"] = 0.0
        staircase["y"] = mid_y
        staircase["meta"]["adjacent_to"] = [RoomType.dining.value]
        gf_layout.append(staircase)
        
    if kitchen:
        kitchen["x"] = stair_w + din_w
        kitchen["y"] = mid_y
        kitchen["meta"]["adjacent_to"] = [RoomType.dining.value]
        gf_layout.append(kitchen)
        
    # Side / Extra spaces next to Living
    side_y = liv_y
    for r in ground_rooms:
        if r["type"] in (RoomType.home_office, RoomType.prayer_room):
            r["x"] = stair_w + din_w
            r["y"] = side_y
            r["meta"]["adjacent_to"] = [RoomType.living.value]
            gf_layout.append(r)
            side_y += r["d"]
            
    # Rear Zone
    rear_y = mid_y + din_d
    
    if master:
        master["x"] = stair_w
        master["y"] = rear_y
        master["meta"]["adjacent_to"] = [RoomType.dining.value]
        gf_layout.append(master)
        
    if bathroom:
        bathroom["x"] = stair_w + din_w
        bathroom["y"] = mid_y + kit_d
        bathroom["meta"]["adjacent_to"] = [RoomType.kitchen.value, RoomType.dining.value]
        gf_layout.append(bathroom)
        
    # Place remaining ground rooms (e.g. bedrooms in 1-floor plan)
    extra_x = 0.0
    extra_y = rear_y
    for r in ground_rooms:
        if r not in gf_layout: # Filter out those already placed
            if r["type"] == RoomType.bedroom:
                r["x"] = extra_x
                r["y"] = extra_y
                r["meta"]["adjacent_to"] = [RoomType.dining.value] if extra_y == rear_y else []
                gf_layout.append(r)
                extra_x += r["w"]
            else:
                # Utility, Servant
                r["x"] = stair_w + din_w
                r["y"] = rear_y + (bathroom["d"] if bathroom else 0)
                r["meta"]["adjacent_to"] = [RoomType.kitchen.value]
                gf_layout.append(r)

    # ==========================================
    # 3. TOPOLOGICAL PLACEMENT (UPPER FLOOR)
    # ==========================================
    uf_layout = []
    if num_floors > 1:
        def extract_u_room(rtype, name=None):
            for r in upper_rooms:
                if r["type"] == rtype and (name is None or r["name"] == name):
                    upper_rooms.remove(r)
                    return r
            return None
            
        u_staircase = extract_u_room(RoomType.staircase)
        if u_staircase:
            u_staircase["x"] = staircase["x"]
            u_staircase["y"] = staircase["y"]
            u_staircase["meta"]["adjacent_to"] = [RoomType.corridor.value]
            uf_layout.append(u_staircase)
            
        # Upper Landing acts as Dining's equivalent
        landing = create_room(RoomType.corridor, "Upper Landing", "upper", 99)
        landing["w"] = dining["w"] if dining else 4.0
        landing["d"] = dining["d"] if dining else 4.0
        landing["x"] = stair_w
        landing["y"] = mid_y
        landing["meta"]["adjacent_to"] = [RoomType.staircase.value]
        uf_layout.append(landing)
        
        # Front Zone (Above Living)
        u_bed2 = extract_u_room(RoomType.bedroom)
        if u_bed2:
            u_bed2["x"] = stair_w
            u_bed2["y"] = mid_y - u_bed2["d"]
            u_bed2["meta"]["adjacent_to"] = [RoomType.corridor.value]
            uf_layout.append(u_bed2)
            
        # Side Zone (Above Kitchen)
        u_bed3 = extract_u_room(RoomType.bedroom)
        if u_bed3:
            u_bed3["x"] = stair_w + landing["w"]
            u_bed3["y"] = mid_y
            u_bed3["meta"]["adjacent_to"] = [RoomType.corridor.value]
            uf_layout.append(u_bed3)
            
        # Rear Zone (Above Master)
        u_bed4 = extract_u_room(RoomType.bedroom)
        if u_bed4:
            u_bed4["x"] = stair_w
            u_bed4["y"] = rear_y
            u_bed4["meta"]["adjacent_to"] = [RoomType.corridor.value]
            uf_layout.append(u_bed4)
            
        u_bath = extract_u_room(RoomType.bathroom)
        if u_bath:
            u_bath["x"] = stair_w + landing["w"]
            bed3_d = u_bed3["d"] if u_bed3 else 3.5
            u_bath["y"] = mid_y + bed3_d
            u_bath["meta"]["adjacent_to"] = [RoomType.corridor.value]
            uf_layout.append(u_bath)
            
        # Place any remaining upper rooms
        u_extra_x = 0.0
        u_extra_y = rear_y
        for r in upper_rooms:
            r["x"] = u_extra_x
            r["y"] = u_extra_y
            r["meta"]["adjacent_to"] = [RoomType.corridor.value] if u_extra_y == rear_y else []
            uf_layout.append(r)
            u_extra_x += r["w"]

    # ==========================================
    # 4. EXTERNAL PLACEMENT
    # ==========================================
    all_internal_rooms = gf_layout + uf_layout
    max_build_x = max([r["x"] + r["w"] for r in all_internal_rooms])
    min_build_x = min([r["x"] for r in all_internal_rooms])
    
    ext_park_y = 0.0
    for r in external_rooms:
        if r["type"] == RoomType.parking:
            cap = r["meta"].get("capacity", 1)
            r["w"], r["d"] = max(3.0, cap * 2.8), 5.5
            r["x"] = max_build_x
            r["y"] = ext_park_y
            r["floor"] = 1
            gf_layout.append(r)
            ext_park_y += r["d"]
            
        elif r["type"] == RoomType.balcony:
            r["w"], r["d"] = 4.0, 2.0
            r["floor"] = 2 if num_floors > 1 else 1
            
            # Attach to the front-most bedroom
            target_layout = uf_layout if num_floors > 1 else gf_layout
            front_bed = None
            min_y = 9999
            for tr in target_layout:
                if tr["type"] in (RoomType.bedroom, RoomType.master_bedroom):
                    if tr["y"] < min_y:
                        min_y = tr["y"]
                        front_bed = tr
                        
            if front_bed:
                r["x"] = front_bed["x"]
                r["y"] = front_bed["y"] - r["d"]
            else:
                r["x"] = stair_w
                r["y"] = -r["d"]
                
            if num_floors > 1:
                uf_layout.append(r)
            else:
                gf_layout.append(r)
                
        elif r["type"] == RoomType.terrace:
            r["w"], r["d"] = 5.0, 5.0
            r["floor"] = 2 if num_floors > 1 else 1
            r["x"] = max_build_x
            r["y"] = rear_y
            if num_floors > 1:
                uf_layout.append(r)
            else:
                gf_layout.append(r)

    # Convert to actual Room objects
    def dicts_to_rooms(layout_dicts, floor_idx):
        return [Room(
            id=r["id"],
            name=r["name"],
            room_type=r["type"],
            floor=floor_idx,
            x=r["x"],
            y=r["y"],
            width=r["w"],
            depth=r["d"],
            metadata=r["meta"]
        ) for r in layout_dicts]
        
    f1_rooms = dicts_to_rooms(gf_layout, 1)
    f2_rooms = dicts_to_rooms(uf_layout, 2) if num_floors > 1 else []
    
    # Calculate bounds correctly (excluding external if they shouldn't constrain building bounds)
    def calc_bounds(rooms):
        b_rooms = [r for r in rooms if r.room_type not in (RoomType.parking, RoomType.balcony, RoomType.terrace)]
        if not b_rooms: return 0, 0
        w = max([r.x + r.width for r in b_rooms])
        d = max([r.y + r.depth for r in b_rooms])
        return w, d
        
    bw1, bd1 = calc_bounds(f1_rooms)
    bw2, bd2 = calc_bounds(f2_rooms)
    building_width = max(bw1, bw2)
    building_depth = max(bd1, bd2)

    # Plot calculations
    all_r = f1_rooms + f2_rooms
    max_ext_x = max([r.x + r.width for r in all_r])
    max_ext_y = max([r.y + r.depth for r in all_r])
    min_ext_x = min([r.x for r in all_r])
    min_ext_y = min([r.y for r in all_r])
    
    plot_width_needed = (max_ext_x - min_ext_x) + 2.0
    plot_depth_needed = (max_ext_y - min_ext_y) + 2.0
    
    if req.plot_width and req.plot_width < plot_width_needed:
        raise ValueError(f"Plot width {req.plot_width} is too small. Need {plot_width_needed}")
    if req.plot_depth and req.plot_depth < plot_depth_needed:
        raise ValueError(f"Plot depth {req.plot_depth} is too small. Need {plot_depth_needed}")
    
    final_plot_width = max(plot_width_needed, req.plot_width if req.plot_width else 0.0)
    final_plot_depth = max(plot_depth_needed, req.plot_depth if req.plot_depth else 0.0)

    house = HouseLayout(
        plot_width=final_plot_width,
        plot_depth=final_plot_depth,
        building_width=building_width,
        building_depth=building_depth,
        floors=[],
        metadata={
            "style": req.house_style, 
            "entrance_direction": req.entrance_direction, 
            "road_side": req.road_side, 
            "roof_type": req.roof_type,
            "unmapped_requirements": unmapped
        }
    )
    
    house.floors.append(FloorLayout(floor_number=1, width=building_width, depth=building_depth, rooms=f1_rooms))
    if num_floors > 1:
        house.floors.append(FloorLayout(floor_number=2, width=building_width, depth=building_depth, rooms=f2_rooms))
        
    # Validate bedroom count
    if req.bedrooms is not None:
        actual_beds = sum(1 for f in house.floors for r in f.rooms if r.room_type in (RoomType.bedroom, RoomType.master_bedroom))
        if actual_beds != req.bedrooms:
            raise ValueError(f"Generated layout has {actual_beds} bedrooms, but {req.bedrooms} were requested.")
            
    return house
