import unittest
from backend.requirements.models import RequirementOutput
from backend.layout.generator import generate_layout
from backend.floorplan.generator import generate_floorplan
from backend.house3d.builder import generate_3d, FLOOR_HEIGHT, WALL_HEIGHT, SLAB_THICKNESS

class TestHouse3D(unittest.TestCase):
    def setUp(self):
        req = RequirementOutput(
            house_style="modern_kerala",
            floors=2,
            bedrooms=4,
            bathrooms=2,
            parking_spaces=2,
            balconies=1
        )
        self.layout = generate_layout(req)
        self.floorplan = generate_floorplan(self.layout)
        self.scene = generate_3d(self.floorplan)
        
    def test_floor_slabs_generated(self):
        slabs = [o for o in self.scene.objects if o.type == "slab"]
        # There should be at least one slab per floor (more because of room-based slabs)
        self.assertTrue(len(slabs) > 2)
        
    def test_roof_generated(self):
        roofs = [o for o in self.scene.objects if o.type == "roof_pitch"]
        self.assertEqual(len(roofs), 1)
        roof = roofs[0]
        # Should sit on top of upper floor walls
        self.assertEqual(roof.position.z, FLOOR_HEIGHT + WALL_HEIGHT)
        # Should overhang building
        self.assertTrue(roof.dimensions.width > self.floorplan.building_width)
        
    def test_walls_generated(self):
        walls = [o for o in self.scene.objects if o.type == "wall"]
        total_fp_walls = sum(len(f.walls) for f in self.floorplan.floors)
        # Because of constructive segmentation, there should be MORE walls than floorplan base walls
        self.assertTrue(len(walls) >= total_fp_walls)
        
    def test_openings_mapped(self):
        door_leaves = [o for o in self.scene.objects if o.type == "door_leaf"]
        window_glasses = [o for o in self.scene.objects if o.type == "window_glass"]
        
        total_fp_doors = sum(1 for f in self.floorplan.floors for o in f.openings if o.opening_type in ("door", "entrance"))
        total_fp_windows = sum(1 for f in self.floorplan.floors for o in f.openings if o.opening_type == "window")
        
        self.assertEqual(len(door_leaves), total_fp_doors)
        self.assertEqual(len(window_glasses), total_fp_windows)
        
        for w in window_glasses:
            # Z should be above floor level
            floor_index = int(w.id.split("_")[1][1:]) # e.g. win_f1_1_glass -> f1
            base_z = (floor_index - 1) * FLOOR_HEIGHT
            self.assertTrue(w.position.z > base_z)
            self.assertTrue(w.dimensions.height > 0.5)
            self.assertTrue(w.dimensions.height < 2.5)
            
    def test_staircases_mapped(self):
        stairs = [o for o in self.scene.objects if o.type == "staircase"]
        # Because of stepped staircases, there should be multiple tread blocks
        self.assertTrue(len(stairs) >= 12)
        
        # Check coordinates against floorplan
        for st in stairs:
            # ID format: staircase_1_ground_staircase_2_t0
            parts = st.id.split("_")
            floor_idx = int(parts[1])
            room_id = "_".join(parts[2:-1]) # strip _tN
            fp_floor = next(f for f in self.floorplan.floors if f.floor_number == floor_idx)
            fp_room = next(r for r in fp_floor.room_boundaries if r.room_id == room_id)
            
            self.assertEqual(st.position.x, fp_room.x)
            # treads are within y bounds
            self.assertTrue(st.position.y >= fp_room.y - 0.01)
            self.assertTrue(st.position.y <= fp_room.y + fp_room.depth + 0.01)
            self.assertEqual(st.dimensions.width, fp_room.width)

if __name__ == '__main__':
    unittest.main()
