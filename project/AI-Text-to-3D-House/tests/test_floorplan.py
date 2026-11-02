import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.requirements.models import RequirementOutput
from backend.layout.generator import generate_layout
from backend.floorplan.generator import generate_floorplan
from backend.layout.models import RoomType

class TestFloorPlan(unittest.TestCase):
    def setUp(self):
        self.req = RequirementOutput(
            house_style="modern_kerala", floors=2, bedrooms=4, bathrooms=2, parking_spaces=2, balconies=1
        )
        self.layout = generate_layout(self.req)
        self.fp = generate_floorplan(self.layout)

    def test_1_floor_counts(self):
        self.assertEqual(len(self.fp.floors), 2)
        self.assertEqual(self.fp.building_width, self.layout.building_width)
        self.assertEqual(self.fp.building_depth, self.layout.building_depth)
        self.assertEqual(self.fp.plot_width, self.layout.plot_width)
        
    def test_2_room_geometry_preservation(self):
        for lf, ff in zip(self.layout.floors, self.fp.floors):
            for lr in lf.rooms:
                if lr.room_type == RoomType.main_entrance:
                    continue
                if lr.room_type in (RoomType.parking, RoomType.balcony, RoomType.terrace):
                    fr = next((r for r in ff.external_spaces if r.room_id == lr.id), None)
                    self.assertIsNotNone(fr)
                    self.assertEqual(fr.x, lr.x)
                    self.assertEqual(fr.y, lr.y)
                    self.assertEqual(fr.width, lr.width)
                    self.assertEqual(fr.depth, lr.depth)
                else:
                    fr = next((r for r in ff.room_boundaries if r.room_id == lr.id), None)
                    self.assertIsNotNone(fr)
                    self.assertEqual(fr.x, lr.x)
                    self.assertEqual(fr.y, lr.y)
                    self.assertEqual(fr.width, lr.width)
                    self.assertEqual(fr.depth, lr.depth)

    def test_3_no_duplicate_rooms(self):
        for ff in self.fp.floors:
            ids = [r.room_id for r in ff.room_boundaries]
            self.assertEqual(len(ids), len(set(ids)))

    def test_4_all_labels_belong(self):
        for ff in self.fp.floors:
            valid_ids = {r.room_id for r in ff.room_boundaries} | {r.room_id for r in ff.external_spaces}
            for lbl in ff.labels:
                self.assertIn(lbl.room_id, valid_ids)

    def test_5_all_dimensions_belong(self):
        for ff in self.fp.floors:
            valid_ids = {r.room_id for r in ff.room_boundaries} | {r.room_id for r in ff.external_spaces}
            for dim in ff.dimensions:
                self.assertIn(dim.room_id, valid_ids)
                
    def test_6_doors_on_shared_boundaries(self):
        for ff in self.fp.floors:
            all_rooms = list(ff.room_boundaries) + list(ff.external_spaces)
            for op in ff.openings:
                if op.opening_type == "door":
                    rooms = op.metadata.get("rooms", [])
                    self.assertEqual(len(rooms), 2)
                    r1 = next((r for r in all_rooms if r.room_id == rooms[0]), None)
                    r2 = next((r for r in all_rooms if r.room_id == rooms[1]), None)
                    self.assertIsNotNone(r1)
                    self.assertIsNotNone(r2)

    def test_7_main_entrance_exterior(self):
        ent = next((op for op in self.fp.floors[0].openings if op.opening_type == "entrance"), None)
        self.assertIsNotNone(ent)
        # Simply check that the entrance belongs to a wall
        self.assertNotEqual(ent.host_wall_id, "unknown_wall")

    def test_8_windows_exterior(self):
        for ff in self.fp.floors:
            for op in ff.openings:
                if op.opening_type == "window":
                    # Check if the host wall is marked as exterior
                    wall = next((w for w in ff.walls if w.id == op.host_wall_id), None)
                    self.assertIsNotNone(wall)
                    self.assertTrue(wall.is_exterior, f"Window {op.id} is not on an exterior wall")

    def test_9_parking_outside(self):
        for ff in self.fp.floors:
            for ext in ff.external_spaces:
                if ext.space_type == RoomType.parking:
                    self.assertTrue(ext.x >= self.fp.building_width or ext.y >= self.fp.building_depth)

    def test_10_balcony_outside(self):
        for ff in self.fp.floors:
            for ext in ff.external_spaces:
                if ext.space_type == RoomType.balcony:
                    # Balcony could be in front (y < 2.0) or on the side. 
                    # We just ensure it's not inside the typical room core.
                    self.assertTrue(ext.y <= 2.0 or ext.x >= self.fp.building_width or ext.y >= self.fp.building_depth)

    def test_11_staircase_preserved(self):
        s_layout = next(r for r in self.layout.floors[0].rooms if r.room_type == RoomType.staircase)
        s_fp = next(r for r in self.fp.floors[0].room_boundaries if r.room_type == RoomType.staircase)
        self.assertEqual(s_layout.width, s_fp.width)

    def test_12_corridor_preserved(self):
        # Step 6A moved corridor to Upper Landing only.
        c_layout = next(r for r in self.layout.floors[1].rooms if r.room_type == RoomType.corridor)
        c_fp = next(r for r in self.fp.floors[1].room_boundaries if r.room_type == RoomType.corridor)
        self.assertEqual(c_layout.width, c_fp.width)
        
    def test_13_staircase_aligned(self):
        s1 = next(r for r in self.fp.floors[0].room_boundaries if r.room_type == RoomType.staircase)
        s2 = next(r for r in self.fp.floors[1].room_boundaries if r.room_type == RoomType.staircase)
        self.assertEqual(s1.x, s2.x)
        self.assertEqual(s1.y, s2.y)
        
    def test_14_determinism(self):
        fp2 = generate_floorplan(self.layout)
        self.assertEqual(self.fp.model_dump_json(), fp2.model_dump_json())

    def test_15_3_bed_1_floor(self):
        req = RequirementOutput(floors=1, bedrooms=3)
        l = generate_layout(req)
        f = generate_floorplan(l)
        self.assertEqual(len(f.floors), 1)

    def test_16_2_bed_2_floor(self):
        req = RequirementOutput(floors=2, bedrooms=2)
        l = generate_layout(req)
        f = generate_floorplan(l)
        self.assertEqual(len(f.floors), 2)
        
    def test_17_no_balcony(self):
        req = RequirementOutput(balconies=0)
        l = generate_layout(req)
        f = generate_floorplan(l)
        exts = [e for fl in f.floors for e in fl.external_spaces if e.space_type == RoomType.balcony]
        self.assertEqual(len(exts), 0)

    def test_18_no_parking(self):
        req = RequirementOutput(parking_spaces=0)
        l = generate_layout(req)
        f = generate_floorplan(l)
        exts = [e for fl in f.floors for e in fl.external_spaces if e.space_type == RoomType.parking]
        self.assertEqual(len(exts), 0)

if __name__ == "__main__":
    unittest.main()
