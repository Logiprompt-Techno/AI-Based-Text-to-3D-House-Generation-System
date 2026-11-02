import bpy
import sys
import json
import os
import math

def get_args():
    # Args after '--'
    try:
        idx = sys.argv.index("--")
        return sys.argv[idx + 1:]
    except ValueError:
        return []

def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
def setup_materials():
    materials = {}
    
    def create_mat(name, color, roughness=0.8, transmission=0.0):
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            # Blender 4.0+ BSDF has 'Base Color'
            if 'Base Color' in bsdf.inputs:
                bsdf.inputs['Base Color'].default_value = color
            if 'Roughness' in bsdf.inputs:
                bsdf.inputs['Roughness'].default_value = roughness
            if transmission > 0 and 'Transmission Weight' in bsdf.inputs:
                bsdf.inputs['Transmission Weight'].default_value = transmission
        return mat

    materials["wall_exterior"] = create_mat("wall_exterior", (0.85, 0.83, 0.80, 1.0), roughness=0.7)
    materials["wall_interior"] = create_mat("wall_interior", (0.7, 0.68, 0.65, 1.0), roughness=0.8)
    materials["slab"] = create_mat("slab", (0.8, 0.8, 0.8, 1.0), roughness=0.8)
    materials["roof"] = create_mat("roof", (0.25, 0.25, 0.28, 1.0), roughness=0.9)
    materials["door_wood"] = create_mat("door_wood", (0.25, 0.12, 0.05, 1.0), roughness=0.4)
    materials["door_frame"] = create_mat("door_frame", (0.1, 0.1, 0.1, 1.0), roughness=0.6)
    
    # Eevee architectural glass: Opaque, very dark, highly reflective
    materials["window_glass"] = create_mat("window_glass", (0.02, 0.03, 0.05, 1.0), roughness=0.05, transmission=0.0)
    materials["window_frame"] = create_mat("window_frame", (0.15, 0.15, 0.15, 1.0), roughness=0.5) 
    
    materials["stairs"] = create_mat("stairs", (0.6, 0.6, 0.6, 1.0), roughness=0.7)
    materials["parking"] = create_mat("parking", (0.35, 0.35, 0.35, 1.0), roughness=0.95)
    materials["balcony"] = create_mat("balcony", (0.65, 0.65, 0.65, 1.0), roughness=0.7)
    materials["grass"] = create_mat("grass", (0.15, 0.30, 0.15, 1.0), roughness=0.9)
    
    return materials

def create_cube(name, x, y, z, w, d, h, mat):
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.active_object
    obj.name = name
    
    # Position is lower-left corner in our coordinate system, but blender cube is centered.
    # So we shift it by half width/depth/height
    obj.location = (x + w/2, y + d/2, z + h/2)
    obj.scale = (w, d, h)
    if mat:
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
            
    return obj

def create_prism(name, x, y, z, w, d, h, mat_roof, mat_wall):
    """Create a triangular prism for a pitched roof."""
    # Vertices of a triangular prism (gable roof)
    # The roof spans from x to x+w, and y to y+d
    # The ridge is at x+w/2
    verts = [
        (x, y, z),               # 0: bottom-left-front
        (x + w, y, z),           # 1: bottom-right-front
        (x + w, y + d, z),       # 2: bottom-right-back
        (x, y + d, z),           # 3: bottom-left-back
        (x + w/2, y, z + h),     # 4: top-ridge-front
        (x + w/2, y + d, z + h)  # 5: top-ridge-back
    ]
    
    faces = [
        (0, 1, 4),          # front gable
        (3, 2, 5),          # back gable
        (0, 3, 5, 4),       # left slope
        (1, 2, 5, 4),       # right slope
        (0, 1, 2, 3)        # bottom
    ]
    
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    if mat_roof:
        obj.data.materials.append(mat_roof)
    if mat_wall:
        obj.data.materials.append(mat_wall)
        
        # Faces 0 and 1 are front and back gables
        if len(obj.data.polygons) > 1:
            obj.data.polygons[0].material_index = 1
            obj.data.polygons[1].material_index = 1
            
    return obj

def setup_lighting(lighting_data):
    # Sun
    bpy.ops.object.light_add(type='SUN', radius=1, align='WORLD', location=(0, 0, 0))
    sun = bpy.context.active_object
    sun.data.energy = lighting_data.get('sun_energy', 4.0)
    
    # Enable shadows
    sun.data.use_shadow = True
    sun.data.shadow_soft_size = 0.15  # Sharper shadows for stronger architectural definition
    sun.data.color = (1.0, 0.95, 0.90) # Warm sun

    sun_pos = lighting_data.get('sun_position', {'x':-25, 'y':-45, 'z':35})
    sun.location = (sun_pos['x'], sun_pos['y'], sun_pos['z'])
    
    # Point sun at center
    direction = -sun.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    sun.rotation_euler = rot_quat.to_euler()
    
    # Fill Light (Subtle Hemi/Area equivalent to prevent pitch-black shadows)
    bpy.ops.object.light_add(type='AREA', radius=50, align='WORLD', location=(20, 20, 20))
    fill = bpy.context.active_object
    fill.data.energy = lighting_data.get('sun_energy', 3.5) * 12 # Lower fill light energy to preserve contrast
    fill.data.color = (0.75, 0.85, 0.95) # Cool fill
    direction_fill = -fill.location
    fill.rotation_euler = direction_fill.to_track_quat('-Z', 'Y').to_euler()
    
    # World
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs[0].default_value = (0.35, 0.4, 0.45, 1.0) # Sky color
        bg_node.inputs[1].default_value = lighting_data.get('ambient_energy', 0.8)
        
    # Ambient Occlusion for depth (Important for EEVEE <= 4.1)
    try:
        bpy.context.scene.eevee.use_gtao = True
        bpy.context.scene.eevee.gtao_distance = 1.5
        bpy.context.scene.eevee.gtao_factor = 1.2
    except AttributeError:
        pass
        
    # Enable Raytracing if available (EEVEE Next Blender 4.2+)
    try:
        bpy.context.scene.eevee.use_raytracing = True
    except AttributeError:
        pass

def render_camera(scene, output_dir, name, location, target):
    cam_data = bpy.data.cameras.new(name=name)
    cam_data.lens = 60.0 # 50-65mm equivalent
    cam_obj = bpy.data.objects.new(name=name, object_data=cam_data)
    bpy.context.collection.objects.link(cam_obj)
    
    cam_obj.location = location
    
    # Track to target
    import mathutils
    target_vec = mathutils.Vector(target)
    loc_vec = mathutils.Vector(location)
    direction = target_vec - loc_vec
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    
    bpy.context.scene.camera = cam_obj
    
    # Render settings
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    bpy.context.scene.eevee.taa_render_samples = 32
    bpy.context.scene.render.resolution_x = 1280
    bpy.context.scene.render.resolution_y = 720
    
    # Enable AO and Shadows for architectural readability (Blender 4.2+ Eevee Next)
    if hasattr(bpy.context.scene.eevee, 'use_raytracing'):
        bpy.context.scene.eevee.use_raytracing = True
    
    output_path = os.path.join(output_dir, f"{name}.png")
    bpy.context.scene.render.filepath = output_path
    
    bpy.ops.render.render(write_still=True)
    print(f"Saved render to {output_path}")

def create_sphere(name, x, y, z, w, d, h, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=1.0)
    obj = bpy.context.active_object
    obj.name = name
    
    # Scale sphere
    obj.scale = (w/2, d/2, h/2)
    # Position
    obj.location = (x + w/2, y + d/2, z + h/2)
    
    if mat:
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
    return obj

def build_scene(scene_data):
    mats = setup_materials()
    
    # We no longer need boolean operations. Everything is constructive.
    for obj_data in scene_data.get('objects', []):
        t = obj_data['type']
        pos = obj_data['position']
        dim = obj_data['dimensions']
        mat_name = obj_data['material']
        obj_name = obj_data['id']
        
        if t == 'roof_pitch':
            create_prism(obj_name, pos['x'], pos['y'], pos['z'], dim['width'], dim['depth'], dim['height'], mats.get(mat_name), mats.get('wall_exterior'))
        elif t == 'tree_sphere':
            create_sphere(obj_name, pos['x'], pos['y'], pos['z'], dim['width'], dim['depth'], dim['height'], mats.get(mat_name))
        else:
            # Everything else (wall, slab, door_frame, window_glass, staircase, etc.) is a cube block
            create_cube(obj_name, pos['x'], pos['y'], pos['z'], dim['width'], dim['depth'], dim['height'], mats.get(mat_name))

def main():
    args = get_args()
    if len(args) < 2:
        print("Usage: blender -b -P blender_script.py -- <scene_json> <output_dir>")
        sys.exit(1)
        
    scene_json = args[0]
    output_dir = args[1]
    
    with open(scene_json, 'r') as f:
        scene_data = json.load(f)
        
    clean_scene()
    build_scene(scene_data)
    setup_lighting(scene_data.get('lighting', {}))
    
    # Calculate bounding box to place cameras
    cam_data = scene_data.get('camera', {})
    
    # From scene_data, compute rough bounds excluding landscape
    objects = [o for o in scene_data.get('objects', []) if o['id'] != 'landscape_grass']
    if objects:
        min_x = min(o['position']['x'] for o in objects)
        max_x = max(o['position']['x'] + o['dimensions']['width'] for o in objects)
        min_y = min(o['position']['y'] for o in objects)
        max_y = max(o['position']['y'] + o['dimensions']['depth'] for o in objects)
        max_z = max(o['position']['z'] + o['dimensions']['height'] for o in objects)

        building_width = max_x - min_x
        building_depth = max_y - min_y
        
        # Center of massing
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        center_z = max_z / 2
        target_vec = (center_x, center_y, center_z * 0.8)

        # Determine camera distance based on building size
        # We need a larger multiplier for a 60mm lens to keep the house fully in frame with margins.
        dist_from_center_y = max(building_width, max_z * 1.77) * 2.5
        dist_from_center_x = max(building_depth, max_z * 1.77) * 2.5
        
        # Angled view needs to encompass the diagonal
        diagonal = math.sqrt(building_width**2 + building_depth**2)
        dist_angled = max(diagonal, max_z * 1.77) * 2.5
        
        # Front Camera (Elevated slightly)
        render_camera(scene_data, output_dir, "front", (center_x, center_y - dist_from_center_y, max_z * 0.5), target_vec)
        # Rear Camera
        render_camera(scene_data, output_dir, "rear", (center_x, center_y + dist_from_center_y, max_z * 0.5), target_vec)
        # Angled Camera (isometric-ish, 3/4 view)
        render_camera(scene_data, output_dir, "angled", (center_x - dist_angled*0.7, center_y - dist_angled*0.7, max_z * 0.8), target_vec)
    
if __name__ == "__main__":
    main()
