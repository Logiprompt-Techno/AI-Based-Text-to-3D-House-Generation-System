from .models import Vector3, Dimension3D, Object3D, Scene3D, Camera3D, Lighting3D
from .materials import Material
from .geometry import validate_opening_in_wall, segment_wall_with_openings
from backend.floorplan.models import FloorPlan

# Visual scale constants
FLOOR_HEIGHT = 3.0
WALL_HEIGHT = 3.0
SLAB_THICKNESS = 0.15

def generate_3d(floorplan: FloorPlan) -> Scene3D:
    scene = Scene3D()
    
    # 1. Floor Slabs
    # Global Plinth for ground floor
    min_gx = min(r.x for f in floorplan.floors if f.floor_number == 1 for r in f.room_boundaries)
    max_gx = max(r.x + r.width for f in floorplan.floors if f.floor_number == 1 for r in f.room_boundaries)
    min_gy = min(r.y for f in floorplan.floors if f.floor_number == 1 for r in f.room_boundaries)
    max_gy = max(r.y + r.depth for f in floorplan.floors if f.floor_number == 1 for r in f.room_boundaries)
    
    plinth = Object3D(
        id="ground_plinth",
        type="slab",
        role="structural",
        position=Vector3(x=min_gx - 0.25, y=min_gy - 0.25, z=-SLAB_THICKNESS),
        dimensions=Dimension3D(width=(max_gx - min_gx) + 0.5, depth=(max_gy - min_gy) + 0.5, height=SLAB_THICKNESS),
        material=Material.SLAB
    )
    scene.objects.append(plinth)

    # Landscape/Grass Plane
    scene.objects.append(Object3D(
        id="landscape_grass",
        type="slab",
        role="exterior",
        position=Vector3(x=min_gx - 20, y=min_gy - 20, z=-SLAB_THICKNESS-0.05),
        dimensions=Dimension3D(width=40, depth=40, height=0.05),
        material=Material.GRASS
    ))
    
    # Parking Slab (if we have a porch or parking area)
    # We can add a simple driveway/parking surface based on house bounds
    scene.objects.append(Object3D(
        id="parking_surface", type="slab", role="exterior",
        position=Vector3(x=min_gx, y=min_gy - 8.0, z=-0.15),
        dimensions=Dimension3D(width=6.0, depth=8.0, height=0.1),
        material=Material.SLAB
    ))

    # Add small trees/bushes if landscaping is requested
    unmapped = floorplan.metadata.get("unmapped_requirements", [])
    if "landscaping" in unmapped:
        # Simple tree 1
        scene.objects.append(Object3D(id="tree1_trunk", type="wall", role="exterior", position=Vector3(x=min_gx - 5.0, y=max_gy + 4.0, z=-SLAB_THICKNESS), dimensions=Dimension3D(width=0.4, depth=0.4, height=1.5), material=Material.DOOR_WOOD))
        scene.objects.append(Object3D(id="tree1_leaves", type="tree_sphere", role="exterior", position=Vector3(x=min_gx - 5.0, y=max_gy + 4.2, z=-SLAB_THICKNESS + 1.5), dimensions=Dimension3D(width=3.0, depth=3.0, height=3.0), material=Material.GRASS))
        # Simple tree 2
        scene.objects.append(Object3D(id="tree2_trunk", type="wall", role="exterior", position=Vector3(x=max_gx + 4.0, y=min_gy - 5.0, z=-SLAB_THICKNESS), dimensions=Dimension3D(width=0.4, depth=0.4, height=1.5), material=Material.DOOR_WOOD))
        scene.objects.append(Object3D(id="tree2_leaves", type="tree_sphere", role="exterior", position=Vector3(x=max_gx + 4.0, y=min_gy - 4.8, z=-SLAB_THICKNESS + 1.5), dimensions=Dimension3D(width=2.5, depth=2.5, height=2.5), material=Material.GRASS))
    # Roof
    top_floor = max([f.floor_number for f in floorplan.floors] + [1])
    top_floor_idx = top_floor - 1
    roof_z = (top_floor_idx * FLOOR_HEIGHT) + WALL_HEIGHT
    
    # Calculate upper floor bounds
    upper_rooms = [r for f in floorplan.floors if f.floor_number == top_floor for r in f.room_boundaries if r.room_type.value != "balcony"]
    if not upper_rooms:
        # Fallback to ground floor
        upper_rooms = [r for f in floorplan.floors if f.floor_number == 1 for r in f.room_boundaries if r.room_type.value != "balcony"]
        
    min_x = min(r.x for r in upper_rooms)
    max_x = max(r.x + r.width for r in upper_rooms)
    min_y = min(r.y for r in upper_rooms)
    max_y = max(r.y + r.depth for r in upper_rooms)
    
    overhang = 0.5
    # Add wall thickness (0.1 on each side) to match the outer face of walls
    
    if floorplan.metadata.get("roof_type", "flat") == "flat":
        # Flat Roof (per room to avoid covering L-shape empty space)
        # Parapets are added later per-wall.
        for r in upper_rooms:
            scene.objects.append(Object3D(
                id=f"roof_main_{r.room_id}",
                type="slab",
                role="exterior",
                position=Vector3(x=r.x - 0.1, y=r.y - 0.1, z=roof_z),
                dimensions=Dimension3D(width=r.width + 0.2, depth=r.depth + 0.2, height=SLAB_THICKNESS),
                material=Material.SLAB
            ))
            # Roof overhang / fascia for modern flat roof detailing
            fascia_t = 0.15
            fascia_h = 0.05
            scene.objects.append(Object3D(id=f"roof_fascia_{r.room_id}", type="slab", role="exterior", position=Vector3(x=r.x - 0.1 - fascia_t, y=r.y - 0.1 - fascia_t, z=roof_z + SLAB_THICKNESS - fascia_h), dimensions=Dimension3D(width=r.width + 0.2 + 2*fascia_t, depth=r.depth + 0.2 + 2*fascia_t, height=fascia_h), material=Material.WALL_EXTERIOR))
    else:
        # Pitched Roof (Default)
        roof_h = 1.5
        roof_w = (max_x - min_x) + overhang * 2
        roof_d = (max_y - min_y) + 0.2
        roof_obj = Object3D(
            id="roof_main",
            type="roof_pitch",
            role="exterior",
            position=Vector3(x=min_x - overhang, y=min_y - 0.1, z=roof_z),
            dimensions=Dimension3D(width=roof_w, depth=roof_d, height=roof_h),
            material=Material.ROOF
        )
        scene.objects.append(roof_obj)
        
        # Roof Fascia (Front and Rear Eave Edges)
        scene.objects.append(Object3D(id="roof_fascia_front", type="wall", role="exterior",
            position=Vector3(x=min_x - overhang, y=max_y + 0.1, z=roof_z - 0.1),
            dimensions=Dimension3D(width=roof_w, depth=0.05, height=0.1), material=Material.WALL_EXTERIOR))
        scene.objects.append(Object3D(id="roof_fascia_rear", type="wall", role="exterior",
            position=Vector3(x=min_x - overhang, y=min_y - 0.15, z=roof_z - 0.1),
            dimensions=Dimension3D(width=roof_w, depth=0.05, height=0.1), material=Material.WALL_EXTERIOR))

    scene.metadata = floorplan.metadata.copy()

    # 2. Extract Openings Map
    openings_by_wall = {}
    for f in floorplan.floors:
        for o in f.openings:
            openings_by_wall.setdefault(o.host_wall_id, []).append({
                'id': o.id,
                'x': o.x,
                'y': o.y,
                'width': o.width,
                'type': o.opening_type
            })

    # Walls & Openings & Slabs & Staircases
    for f in floorplan.floors:
        floor_idx = f.floor_number - 1
        z_offset = floor_idx * FLOOR_HEIGHT
        
        # Add simple roof coping (edge detailing)
        coping_thick = 0.05
        coping_overhang = 0.05
        scene.objects.append(Object3D(
            id="roof_coping", type="slab", role="structural",
            position=Vector3(x=min_x - coping_overhang, y=min_y - coping_overhang, z=roof_z + SLAB_THICKNESS),
            dimensions=Dimension3D(width=(max_x - min_x) + coping_overhang*2, depth=(max_y - min_y) + coping_overhang*2, height=coping_thick),
            material=Material.WALL_INTERIOR
        ))

        # Room bounding validations
        for r in f.room_boundaries:
            if r.width <= 0 or r.depth <= 0:
                raise ValueError(f"Room {r.room_id} has zero or negative dimensions")
                
        # Generate Floor Slab using room unions instead of bounding box
        # We will use individual room slabs to form the floor precisely
        for r in f.room_boundaries:
            if r.room_type.value != "staircase":  # Staircase has a void or its own geometry
                scene.objects.append(Object3D(
                    id=f"slab_f{f.floor_number}_{r.room_id}",
                    type="slab",
                    role="structural",
                    position=Vector3(x=r.x - 0.1, y=r.y - 0.1, z=z_offset - SLAB_THICKNESS),
                    dimensions=Dimension3D(width=r.width + 0.2, depth=r.depth + 0.2, height=SLAB_THICKNESS),
                    material=Material.SLAB
                ))
        
        # Corridor explicit slab for upper floor if needed, but they are in room_boundaries
        
        # Constructive walls
        roof_type = floorplan.metadata.get("roof_type", "flat")
        
        # Find the front-most exterior wall for accent (min y)
        accent_wall_id = None
        min_y_wall = 9999
        for w in f.walls:
            if w.is_exterior:
                wall_y = min(w.y1, w.y2)
                if wall_y < min_y_wall:
                    min_y_wall = wall_y
                    accent_wall_id = w.id
                    
        for w in f.walls:
            ops = openings_by_wall.get(w.id, [])
            blocks = segment_wall_with_openings(w.x1, w.y1, w.x2, w.y2, w.thickness, WALL_HEIGHT, ops)
            
            for i, blk in enumerate(blocks):
                is_accent = (w.id == accent_wall_id)
                mat = Material.WALL_EXTERIOR if w.is_exterior else Material.WALL_INTERIOR
                if is_accent:
                    mat = Material.WALL_INTERIOR  # Darker accent color
                    
                scene.objects.append(Object3D(
                    id=f"{w.id}_seg_{i}",
                    type="wall",
                    role="exterior" if w.is_exterior else "interior",
                    position=Vector3(x=blk['x'], y=blk['y'], z=z_offset + blk['z']),
                    dimensions=Dimension3D(width=blk['w'], depth=blk['d'], height=blk['h']),
                    material=mat
                ))
            
            if w.is_exterior and roof_type == "flat":
                p_h = 0.6
                p_thick = 0.1
                
                center_gx = (min_gx + max_gx) / 2
                center_gy = (min_gy + max_gy) / 2
                is_vert = abs(w.x1 - w.x2) < 0.01
                
                if is_vert:
                    ext_sign_x = -1 if w.x1 < center_gx else 1
                    p_x = w.x1 - w.thickness/2 if ext_sign_x == -1 else w.x1 + w.thickness/2 - p_thick
                    scene.objects.append(Object3D(id=f"{w.id}_parapet", type="wall", role="exterior", position=Vector3(x=p_x, y=min(w.y1, w.y2), z=roof_z + SLAB_THICKNESS), dimensions=Dimension3D(width=p_thick, depth=abs(w.y1 - w.y2), height=p_h), material=Material.WALL_EXTERIOR))
                else:
                    ext_sign_y = -1 if w.y1 < center_gy else 1
                    p_y = w.y1 - w.thickness/2 if ext_sign_y == -1 else w.y1 + w.thickness/2 - p_thick
                    scene.objects.append(Object3D(id=f"{w.id}_parapet", type="wall", role="exterior", position=Vector3(x=min(w.x1, w.x2), y=p_y, z=roof_z + SLAB_THICKNESS), dimensions=Dimension3D(width=abs(w.x1 - w.x2), depth=p_thick, height=p_h), material=Material.WALL_EXTERIOR))
            
        # Detailed Openings (Doors & Windows)
        for o in f.openings:
            is_vert = False
            for w in f.walls:
                if w.id == o.host_wall_id:
                    is_vert = abs(w.x1 - w.x2) < 0.01
                    wall_thickness = w.thickness
                    break
                    
            if o.opening_type in ("door", "entrance"):
                op_h = 2.1
                # Increase door frame depth
                frame_thick = wall_thickness + 0.15
                frame_t = 0.04
                
                # Determine which way is exterior for this opening
                center_gx = (min_gx + max_gx) / 2
                center_gy = (min_gy + max_gy) / 2
                ext_sign_x = -1 if o.x < center_gx else 1
                ext_sign_y = -1 if o.y < center_gy else 1
                
                if is_vert:
                    # Door Frame (2 sides + 1 top)
                    f_side_dim = Dimension3D(width=frame_thick, depth=frame_t, height=op_h)
                    
                    # Left frame
                    scene.objects.append(Object3D(id=f"{o.id}_fl", type="door_frame", role="frame",
                        position=Vector3(x=o.x - frame_thick/2, y=o.y - o.width/2, z=z_offset),
                        dimensions=f_side_dim, material=Material.DOOR_WOOD))
                    # Right frame
                    scene.objects.append(Object3D(id=f"{o.id}_fr", type="door_frame", role="frame",
                        position=Vector3(x=o.x - frame_thick/2, y=o.y + o.width/2 - frame_t, z=z_offset),
                        dimensions=f_side_dim, material=Material.DOOR_WOOD))
                    # Top frame
                    scene.objects.append(Object3D(id=f"{o.id}_ft", type="door_frame", role="frame",
                        position=Vector3(x=o.x - frame_thick/2, y=o.y - o.width/2, z=z_offset + op_h - frame_t),
                        dimensions=Dimension3D(width=frame_thick, depth=o.width, height=frame_t), material=Material.DOOR_WOOD))
                
                    # Door Leaf
                    dim_leaf = Dimension3D(width=0.04, depth=o.width - frame_t*2, height=op_h - frame_t)
                    pos_leaf = Vector3(x=o.x - 0.02, y=o.y - o.width/2 + frame_t, z=z_offset)
                
                    if getattr(o, 'opening_type', None) == 'entrance' or 'entrance' in str(o.id).lower():
                        canopy_h = 0.05
                        canopy_d = 0.6
                        canopy_w = o.width + 0.4
                        proj_t = 0.05
                        
                        surr_x = o.x - wall_thickness/2 - proj_t if ext_sign_x == -1 else o.x + wall_thickness/2
                        canopy_x = o.x - wall_thickness/2 - canopy_d if ext_sign_x == -1 else o.x + wall_thickness/2
                        thresh_x = o.x - wall_thickness/2 - 0.6 if ext_sign_x == -1 else o.x + wall_thickness/2
                        step_x = o.x - wall_thickness/2 - 1.0 if ext_sign_x == -1 else o.x + wall_thickness/2 + 0.6
                        
                        # Surround
                        scene.objects.append(Object3D(id=f"{o.id}_surround_l", type="wall", role="exterior", position=Vector3(x=surr_x, y=o.y - o.width/2 - 0.15, z=z_offset), dimensions=Dimension3D(width=proj_t, depth=0.15, height=op_h+0.15), material=Material.WALL_EXTERIOR))
                        scene.objects.append(Object3D(id=f"{o.id}_surround_r", type="wall", role="exterior", position=Vector3(x=surr_x, y=o.y + o.width/2, z=z_offset), dimensions=Dimension3D(width=proj_t, depth=0.15, height=op_h+0.15), material=Material.WALL_EXTERIOR))
                        scene.objects.append(Object3D(id=f"{o.id}_surround_t", type="wall", role="exterior", position=Vector3(x=surr_x, y=o.y - o.width/2 - 0.15, z=z_offset + op_h), dimensions=Dimension3D(width=proj_t, depth=o.width+0.3, height=0.15), material=Material.WALL_EXTERIOR))
                        
                        # Canopy
                        scene.objects.append(Object3D(id=f"{o.id}_canopy", type="slab", role="exterior", position=Vector3(x=canopy_x, y=o.y - canopy_w/2, z=z_offset + op_h + 0.15), dimensions=Dimension3D(width=canopy_d, depth=canopy_w, height=canopy_h), material=Material.SLAB))
                        
                        # Platform and Steps
                        scene.objects.append(Object3D(id=f"{o.id}_threshold", type="slab", role="exterior", position=Vector3(x=thresh_x, y=o.y - o.width/2 - 0.2, z=-0.1), dimensions=Dimension3D(width=0.6, depth=o.width+0.4, height=0.1), material=Material.SLAB))
                        scene.objects.append(Object3D(id=f"{o.id}_step", type="slab", role="exterior", position=Vector3(x=step_x, y=o.y - o.width/2 - 0.2, z=-0.2), dimensions=Dimension3D(width=0.4, depth=o.width+0.4, height=0.1), material=Material.SLAB))
                else:
                    # Door Frame (2 sides + 1 top)
                    f_side_dim = Dimension3D(width=frame_t, depth=frame_thick, height=op_h)
                    
                    # Bottom frame (left visually)
                    scene.objects.append(Object3D(id=f"{o.id}_fl", type="door_frame", role="frame",
                        position=Vector3(x=o.x - o.width/2, y=o.y - frame_thick/2, z=z_offset),
                        dimensions=f_side_dim, material=Material.DOOR_WOOD))
                    # Top frame (right visually)
                    scene.objects.append(Object3D(id=f"{o.id}_fr", type="door_frame", role="frame",
                        position=Vector3(x=o.x + o.width/2 - frame_t, y=o.y - frame_thick/2, z=z_offset),
                        dimensions=f_side_dim, material=Material.DOOR_WOOD))
                    # Header frame
                    scene.objects.append(Object3D(id=f"{o.id}_ft", type="door_frame", role="frame",
                        position=Vector3(x=o.x - o.width/2, y=o.y - frame_thick/2, z=z_offset + op_h - frame_t),
                        dimensions=Dimension3D(width=o.width, depth=frame_thick, height=frame_t), material=Material.DOOR_WOOD))
                        
                    # Door Leaf
                    dim_leaf = Dimension3D(width=o.width - frame_t*2, depth=0.04, height=op_h - frame_t)
                    pos_leaf = Vector3(x=o.x - o.width/2 + frame_t, y=o.y - 0.02, z=z_offset)
                    
                scene.objects.append(Object3D(
                    id=f"{o.id}_leaf", type="door_leaf", role="leaf",
                    position=pos_leaf, dimensions=dim_leaf, material=Material.DOOR_WOOD
                ))
                
                if getattr(o, 'opening_type', None) == 'entrance' or 'entrance' in str(o.id).lower():
                    canopy_h = 0.05
                    canopy_d = 0.6
                    canopy_w = o.width + 0.4
                    proj_t = 0.05
                    
                    # Horizontal accent band on the canopy
                    scene.objects.append(Object3D(id=f"{o.id}_canopy_band", type="slab", role="exterior",
                        position=Vector3(x=o.x - canopy_w/2 - 0.02, y=o.y - canopy_d, z=z_offset + op_h + 0.2),
                        dimensions=Dimension3D(width=canopy_w + 0.04, depth=canopy_d, height=0.02), material=Material.WALL_INTERIOR))
                    
                    if is_vert:
                        surr_x = o.x - wall_thickness/2 - proj_t if ext_sign_x == -1 else o.x + wall_thickness/2
                        canopy_x = o.x - wall_thickness/2 - canopy_d if ext_sign_x == -1 else o.x + wall_thickness/2
                        thresh_x = o.x - wall_thickness/2 - 0.6 if ext_sign_x == -1 else o.x + wall_thickness/2
                        step_x = o.x - wall_thickness/2 - 1.0 if ext_sign_x == -1 else o.x + wall_thickness/2 + 0.6
                        
                        # Restrained Vertical Accent Panel (Physically attached, framing the entrance)
                        panel_w = o.width + 1.0
                        panel_side_w = (panel_w - o.width) / 2
                        scene.objects.append(Object3D(id=f"{o.id}_surround_l", type="wall", role="exterior", position=Vector3(x=surr_x, y=o.y - o.width/2 - panel_side_w, z=0), dimensions=Dimension3D(width=proj_t, depth=panel_side_w, height=op_h), material=Material.WALL_INTERIOR))
                        scene.objects.append(Object3D(id=f"{o.id}_surround_r", type="wall", role="exterior", position=Vector3(x=surr_x, y=o.y + o.width/2, z=0), dimensions=Dimension3D(width=proj_t, depth=panel_side_w, height=op_h), material=Material.WALL_INTERIOR))
                        # Top part extends to roof
                        top_h = (roof_z + SLAB_THICKNESS) - op_h
                        scene.objects.append(Object3D(id=f"{o.id}_surround_t", type="wall", role="exterior", position=Vector3(x=surr_x, y=o.y - panel_w/2, z=op_h), dimensions=Dimension3D(width=proj_t, depth=panel_w, height=top_h), material=Material.WALL_INTERIOR))
                        
                        # Canopy
                        scene.objects.append(Object3D(id=f"{o.id}_canopy", type="slab", role="exterior", position=Vector3(x=canopy_x, y=o.y - canopy_w/2, z=op_h + 0.15), dimensions=Dimension3D(width=canopy_d, depth=canopy_w, height=canopy_h), material=Material.SLAB))
                        
                        # Platform and Steps
                        scene.objects.append(Object3D(id=f"{o.id}_threshold", type="slab", role="exterior", position=Vector3(x=thresh_x, y=o.y - o.width/2 - 0.2, z=-0.1), dimensions=Dimension3D(width=0.6, depth=o.width+0.4, height=0.1), material=Material.SLAB))
                        scene.objects.append(Object3D(id=f"{o.id}_step", type="slab", role="exterior", position=Vector3(x=step_x, y=o.y - o.width/2 - 0.2, z=-0.2), dimensions=Dimension3D(width=0.4, depth=o.width+0.4, height=0.1), material=Material.SLAB))
                        
                        # Entrance Pathway
                        path_len = 5.0
                        path_x = step_x - path_len if ext_sign_x == -1 else step_x + 0.4
                        scene.objects.append(Object3D(id=f"{o.id}_path", type="slab", role="exterior", position=Vector3(x=path_x, y=o.y - o.width/2 - 0.2, z=-0.25), dimensions=Dimension3D(width=path_len, depth=o.width+0.4, height=0.05), material=Material.SLAB))
                        
                        # Restrained Shrubs near entrance
                        shrub_y = o.y - o.width/2 - 1.0
                        shrub_x = step_x - 0.5 if ext_sign_x == -1 else step_x + 0.5
                        scene.objects.append(Object3D(id=f"{o.id}_shrub1", type="tree_sphere", role="exterior", position=Vector3(x=shrub_x, y=shrub_y, z=-0.2), dimensions=Dimension3D(width=0.6, depth=0.6, height=0.6), material=Material.GRASS))
                        scene.objects.append(Object3D(id=f"{o.id}_shrub2", type="tree_sphere", role="exterior", position=Vector3(x=shrub_x, y=o.y + o.width/2 + 0.4, z=-0.2), dimensions=Dimension3D(width=0.6, depth=0.6, height=0.6), material=Material.GRASS))
                    else:
                        surr_y = o.y - wall_thickness/2 - proj_t if ext_sign_y == -1 else o.y + wall_thickness/2
                        canopy_y = o.y - wall_thickness/2 - canopy_d if ext_sign_y == -1 else o.y + wall_thickness/2
                        thresh_y = o.y - wall_thickness/2 - 0.6 if ext_sign_y == -1 else o.y + wall_thickness/2
                        step_y = o.y - wall_thickness/2 - 1.0 if ext_sign_y == -1 else o.y + wall_thickness/2 + 0.6
                        
                        # Restrained Vertical Accent Panel (Physically attached, framing the entrance)
                        panel_w = o.width + 1.0
                        panel_side_w = (panel_w - o.width) / 2
                        scene.objects.append(Object3D(id=f"{o.id}_surround_l", type="wall", role="exterior", position=Vector3(x=o.x - o.width/2 - panel_side_w, y=surr_y, z=0), dimensions=Dimension3D(width=panel_side_w, depth=proj_t, height=op_h), material=Material.WALL_INTERIOR))
                        scene.objects.append(Object3D(id=f"{o.id}_surround_r", type="wall", role="exterior", position=Vector3(x=o.x + o.width/2, y=surr_y, z=0), dimensions=Dimension3D(width=panel_side_w, depth=proj_t, height=op_h), material=Material.WALL_INTERIOR))
                        # Top part extends to roof
                        top_h = (roof_z + SLAB_THICKNESS) - op_h
                        scene.objects.append(Object3D(id=f"{o.id}_surround_t", type="wall", role="exterior", position=Vector3(x=o.x - panel_w/2, y=surr_y, z=op_h), dimensions=Dimension3D(width=panel_w, depth=proj_t, height=top_h), material=Material.WALL_INTERIOR))
                        
                        # Canopy
                        scene.objects.append(Object3D(id=f"{o.id}_canopy", type="slab", role="exterior", position=Vector3(x=o.x - canopy_w/2, y=canopy_y, z=op_h + 0.15), dimensions=Dimension3D(width=canopy_w, depth=canopy_d, height=canopy_h), material=Material.SLAB))
                        
                        # Platform and Steps
                        scene.objects.append(Object3D(id=f"{o.id}_threshold", type="slab", role="exterior", position=Vector3(x=o.x - o.width/2 - 0.2, y=thresh_y, z=-0.1), dimensions=Dimension3D(width=o.width+0.4, depth=0.6, height=0.1), material=Material.SLAB))
                        scene.objects.append(Object3D(id=f"{o.id}_step", type="slab", role="exterior", position=Vector3(x=o.x - o.width/2 - 0.2, y=step_y, z=-0.2), dimensions=Dimension3D(width=o.width+0.4, depth=0.4, height=0.1), material=Material.SLAB))
                        
                        # Entrance Pathway
                        path_len = 5.0
                        path_y = step_y - path_len if ext_sign_y == -1 else step_y + 0.4
                        scene.objects.append(Object3D(id=f"{o.id}_path", type="slab", role="exterior", position=Vector3(x=o.x - o.width/2 - 0.2, y=path_y, z=-0.25), dimensions=Dimension3D(width=o.width+0.4, depth=path_len, height=0.05), material=Material.SLAB))
                        
                        # Restrained Shrubs near entrance
                        shrub_x = o.x - o.width/2 - 1.0
                        shrub_y = step_y - 0.5 if ext_sign_y == -1 else step_y + 0.5
                        scene.objects.append(Object3D(id=f"{o.id}_shrub1", type="tree_sphere", role="exterior", position=Vector3(x=shrub_x, y=shrub_y, z=-0.2), dimensions=Dimension3D(width=0.6, depth=0.6, height=0.6), material=Material.GRASS))
                        scene.objects.append(Object3D(id=f"{o.id}_shrub2", type="tree_sphere", role="exterior", position=Vector3(x=o.x + o.width/2 + 0.4, y=shrub_y, z=-0.2), dimensions=Dimension3D(width=0.6, depth=0.6, height=0.6), material=Material.GRASS))

            elif o.opening_type == "window":
                sill = 1.0
                win_h = 1.4
                
                room_id = o.metadata.get("room")
                if room_id:
                    host_room = next((r for r in f.room_boundaries if r.room_id == room_id), None)
                    if host_room:
                        if host_room.room_type == "living_room":
                            win_h = 2.0
                            sill = 0.4
                        elif host_room.room_type == "bathroom":
                            win_h = 0.8
                            sill = 1.6
                        elif host_room.room_type == "kitchen":
                            win_h = 1.2
                            sill = 1.0
                            
                # Increase window frame depth and make it slimmer
                frame_thick = wall_thickness + 0.15
                frame_t = 0.04
                
                if is_vert:
                    # Wall is along Y axis, thickness along X
                    f_side_dim = Dimension3D(width=frame_thick, depth=frame_t, height=win_h)
                    f_tb_dim = Dimension3D(width=frame_thick, depth=o.width, height=frame_t)
                    
                    # Recessed glass
                    dim_glass = Dimension3D(width=0.02, depth=o.width - frame_t*2, height=win_h - frame_t*2)
                    pos_glass = Vector3(x=o.x, y=o.y - o.width/2 + frame_t, z=z_offset + sill + frame_t)
                    
                    # Exterior sill projection
                    sill_d = 0.12
                    sill_th = 0.06
                    sill_x = o.x - wall_thickness/2 - sill_d if ext_sign_x == -1 else o.x + wall_thickness/2
                    scene.objects.append(Object3D(id=f"{o.id}_ext_sill", type="window_frame", role="frame", position=Vector3(x=sill_x, y=o.y - o.width/2 - 0.05, z=z_offset + sill - sill_th), dimensions=Dimension3D(width=sill_d, depth=o.width+0.1, height=sill_th), material=Material.WINDOW_FRAME))
                    
                    # Sides
                    scene.objects.append(Object3D(id=f"{o.id}_fl", type="window_frame", role="frame", position=Vector3(x=o.x - frame_thick/2, y=o.y - o.width/2, z=z_offset + sill), dimensions=f_side_dim, material=Material.WINDOW_FRAME))
                    scene.objects.append(Object3D(id=f"{o.id}_fr", type="window_frame", role="frame", position=Vector3(x=o.x - frame_thick/2, y=o.y + o.width/2 - frame_t, z=z_offset + sill), dimensions=f_side_dim, material=Material.WINDOW_FRAME))
                    # Top/Bottom
                    scene.objects.append(Object3D(id=f"{o.id}_fb", type="window_frame", role="frame", position=Vector3(x=o.x - frame_thick/2, y=o.y - o.width/2, z=z_offset + sill), dimensions=f_tb_dim, material=Material.WINDOW_FRAME))
                    scene.objects.append(Object3D(id=f"{o.id}_ft", type="window_frame", role="frame", position=Vector3(x=o.x - frame_thick/2, y=o.y - o.width/2, z=z_offset + sill + win_h - frame_t), dimensions=f_tb_dim, material=Material.WINDOW_FRAME))
                else:
                    # Wall is along X axis, thickness along Y
                    f_side_dim = Dimension3D(width=frame_t, depth=frame_thick, height=win_h)
                    f_tb_dim = Dimension3D(width=o.width, depth=frame_thick, height=frame_t)
                    
                    # Recessed glass
                    dim_glass = Dimension3D(width=o.width - frame_t*2, depth=0.02, height=win_h - frame_t*2)
                    pos_glass = Vector3(x=o.x - o.width/2 + frame_t, y=o.y, z=z_offset + sill + frame_t)
                    
                    # Exterior sill projection
                    sill_d = 0.12
                    sill_th = 0.06
                    sill_y = o.y - wall_thickness/2 - sill_d if ext_sign_y == -1 else o.y + wall_thickness/2
                    scene.objects.append(Object3D(id=f"{o.id}_ext_sill", type="window_frame", role="frame", position=Vector3(x=o.x - o.width/2 - 0.05, y=sill_y, z=z_offset + sill - sill_th), dimensions=Dimension3D(width=o.width+0.1, depth=sill_d, height=sill_th), material=Material.WINDOW_FRAME))
                    # Sides
                    scene.objects.append(Object3D(id=f"{o.id}_fl", type="window_frame", role="frame", position=Vector3(x=o.x - o.width/2, y=o.y - frame_thick/2, z=z_offset + sill), dimensions=f_side_dim, material=Material.WINDOW_FRAME))
                    scene.objects.append(Object3D(id=f"{o.id}_fr", type="window_frame", role="frame", position=Vector3(x=o.x + o.width/2 - frame_t, y=o.y - frame_thick/2, z=z_offset + sill), dimensions=f_side_dim, material=Material.WINDOW_FRAME))
                    # Top/Bottom
                    scene.objects.append(Object3D(id=f"{o.id}_fb", type="window_frame", role="frame", position=Vector3(x=o.x - o.width/2, y=o.y - frame_thick/2, z=z_offset + sill), dimensions=f_tb_dim, material=Material.WINDOW_FRAME))
                    scene.objects.append(Object3D(id=f"{o.id}_ft", type="window_frame", role="frame", position=Vector3(x=o.x - o.width/2, y=o.y - frame_thick/2, z=z_offset + sill + win_h - frame_t), dimensions=f_tb_dim, material=Material.WINDOW_FRAME))
                    
                scene.objects.append(Object3D(
                    id=f"{o.id}_glass", type="window_glass", role="glass",
                    position=pos_glass, dimensions=dim_glass, material=Material.WINDOW_GLASS
                ))

        # External Spaces (Parking, Balcony)
        for ext in f.external_spaces:
            if ext.space_type == "parking":
                scene.objects.append(Object3D(
                    id=f"parking_{f.floor_number}_{ext.room_id}",
                    type="parking",
                    role="exterior",
                    position=Vector3(x=ext.x, y=ext.y, z=-0.15),
                    dimensions=Dimension3D(width=ext.width, depth=ext.depth, height=0.15),
                    material=Material.PARKING
                ))
                # Parking boundary (low curb)
                curb_w = 0.1
                curb_h = 0.2
                scene.objects.append(Object3D(id=f"curb_{ext.room_id}_l", type="wall", role="exterior", position=Vector3(x=ext.x - curb_w, y=ext.y, z=-0.15), dimensions=Dimension3D(width=curb_w, depth=ext.depth, height=curb_h), material=Material.SLAB))
                scene.objects.append(Object3D(id=f"curb_{ext.room_id}_r", type="wall", role="exterior", position=Vector3(x=ext.x + ext.width, y=ext.y, z=-0.15), dimensions=Dimension3D(width=curb_w, depth=ext.depth, height=curb_h), material=Material.SLAB))
                scene.objects.append(Object3D(id=f"curb_{ext.room_id}_b", type="wall", role="exterior", position=Vector3(x=ext.x, y=ext.y + ext.depth, z=-0.15), dimensions=Dimension3D(width=ext.width, depth=curb_w, height=curb_h), material=Material.SLAB))
            elif ext.space_type == "balcony":
                # Thicker slab to look structural
                scene.objects.append(Object3D(
                    id=f"balcony_{f.floor_number}_{ext.room_id}",
                    type="balcony",
                    role="exterior",
                    position=Vector3(x=ext.x, y=ext.y, z=z_offset - 0.15),
                    dimensions=Dimension3D(width=ext.width, depth=ext.depth, height=0.30),
                    material=Material.WALL_EXTERIOR
                ))
                
                # Glass railing (very modern)
                r_h = 1.1
                r_t = 0.05
                
                # Glass panels
                scene.objects.append(Object3D(id=f"br1_glass_{ext.room_id}", type="glass", role="exterior", position=Vector3(x=ext.x, y=ext.y, z=z_offset+0.15), dimensions=Dimension3D(width=ext.width, depth=0.02, height=r_h-0.1), material=Material.WINDOW_GLASS))
                scene.objects.append(Object3D(id=f"br2_glass_{ext.room_id}", type="glass", role="exterior", position=Vector3(x=ext.x, y=ext.y+ext.depth-0.02, z=z_offset+0.15), dimensions=Dimension3D(width=ext.width, depth=0.02, height=r_h-0.1), material=Material.WINDOW_GLASS))
                scene.objects.append(Object3D(id=f"br3_glass_{ext.room_id}", type="glass", role="exterior", position=Vector3(x=ext.x, y=ext.y, z=z_offset+0.15), dimensions=Dimension3D(width=0.02, depth=ext.depth, height=r_h-0.1), material=Material.WINDOW_GLASS))
                scene.objects.append(Object3D(id=f"br4_glass_{ext.room_id}", type="glass", role="exterior", position=Vector3(x=ext.x+ext.width-0.02, y=ext.y, z=z_offset+0.15), dimensions=Dimension3D(width=0.02, depth=ext.depth, height=r_h-0.1), material=Material.WINDOW_GLASS))
                
                # Top Rails (Handrail)
                scene.objects.append(Object3D(id=f"br1_t_{ext.room_id}", type="railing", role="exterior", position=Vector3(x=ext.x, y=ext.y-r_t/2, z=z_offset+0.15+r_h-r_t), dimensions=Dimension3D(width=ext.width, depth=r_t, height=r_t), material=Material.WINDOW_FRAME))
                scene.objects.append(Object3D(id=f"br2_t_{ext.room_id}", type="railing", role="exterior", position=Vector3(x=ext.x, y=ext.y+ext.depth-r_t/2, z=z_offset+0.15+r_h-r_t), dimensions=Dimension3D(width=ext.width, depth=r_t, height=r_t), material=Material.WINDOW_FRAME))
                scene.objects.append(Object3D(id=f"br3_t_{ext.room_id}", type="railing", role="exterior", position=Vector3(x=ext.x-r_t/2, y=ext.y, z=z_offset+0.15+r_h-r_t), dimensions=Dimension3D(width=r_t, depth=ext.depth, height=r_t), material=Material.WINDOW_FRAME))
                scene.objects.append(Object3D(id=f"br4_t_{ext.room_id}", type="railing", role="exterior", position=Vector3(x=ext.x+ext.width-r_t/2, y=ext.y, z=z_offset+0.15+r_h-r_t), dimensions=Dimension3D(width=r_t, depth=ext.depth, height=r_t), material=Material.WINDOW_FRAME))


        # Staircases
        for r in f.room_boundaries:
            if r.room_type == "staircase":
                # Stepped staircase
                treads = 12
                tread_d = r.depth / treads
                rise_h = FLOOR_HEIGHT / treads
                for t in range(treads):
                    scene.objects.append(Object3D(
                        id=f"staircase_{f.floor_number}_{r.room_id}_t{t}",
                        type="staircase",
                        role="interior",
                        position=Vector3(x=r.x, y=r.y + t*tread_d, z=z_offset),
                        dimensions=Dimension3D(width=r.width, depth=tread_d, height=(t+1)*rise_h),
                        material=Material.STAIRS
                    ))

    # Camera framing
    # Focus exactly on building center by deriving bounds from actual slabs
    cx = (min_gx + max_gx) / 2.0
    cy = (min_gy + max_gy) / 2.0
    cz = roof_z / 2.0
    
    # Calculate a safe distance based on max dimension
    b_size = max(max_gx - min_gx, max_gy - min_gy)
    
    scene.camera = Camera3D(
        target=Vector3(x=cx, y=cy, z=cz),
        position=Vector3(x=cx - b_size, y=cy - b_size - 10, z=cz + 5),
        fov=45.0,
        lens=35.0
    )
    
    scene.lighting = Lighting3D(
        sun_position=Vector3(x=-20, y=-30, z=30),
        sun_energy=4.0,
        ambient_energy=1.2
    )

    return scene
