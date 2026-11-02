import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.requirements.models import RequirementOutput
from backend.layout.generator import generate_layout
from backend.layout.models import RoomType

class TestLayout(unittest.TestCase):
    def test_1_modern_kerala_4bhk(self):
        req = RequirementOutput(
            house_style="modern_kerala",
            floors=2, bedrooms=4, bathrooms=2, parking_spaces=2, balconies=1
        )
        layout = generate_layout(req)
        self.assertEqual(len(layout.floors), 2)
        beds = sum(1 for f in layout.floors for r in f.rooms if r.room_type in (RoomType.master_bedroom, RoomType.bedroom))
        self.assertEqual(beds, 4)
        parking = next(r for f in layout.floors for r in f.rooms if r.room_type == RoomType.parking)
        self.assertTrue(parking.x >= layout.building_width) # Should be outside building
        
    def test_2_3bhk_2_floors_1_car(self):
        req = RequirementOutput(floors=2, bedrooms=3, parking_spaces=1)
        layout = generate_layout(req)
        self.assertEqual(len(layout.floors), 2)
        parking = next(r for f in layout.floors for r in f.rooms if r.room_type == RoomType.parking)
        self.assertTrue(parking.width >= 3.0) # 1 car parking
        
    def test_3_2bhk_1_floor(self):
        req = RequirementOutput(floors=1, bedrooms=2)
        layout = generate_layout(req)
        self.assertEqual(len(layout.floors), 1)
        beds = sum(1 for f in layout.floors for r in f.rooms if r.room_type in (RoomType.master_bedroom, RoomType.bedroom))
        self.assertEqual(beds, 2)
        
    def test_4_4bhk_no_parking(self):
        req = RequirementOutput(floors=2, bedrooms=4, parking_spaces=0)
        layout = generate_layout(req)
        parkings = [r for f in layout.floors for r in f.rooms if r.room_type == RoomType.parking]
        self.assertEqual(len(parkings), 0)
        
    def test_5_4bhk_no_balcony(self):
        req = RequirementOutput(floors=2, bedrooms=4, balconies=0)
        layout = generate_layout(req)
        balconies = [r for f in layout.floors for r in f.rooms if r.room_type == RoomType.balcony]
        self.assertEqual(len(balconies), 0)
        
    def test_6_explicit_plot(self):
        req = RequirementOutput(floors=1, bedrooms=2, plot_width=50, plot_depth=50)
        layout = generate_layout(req)
        self.assertEqual(layout.plot_width, 50)
        self.assertEqual(layout.plot_depth, 50)
        
    def test_7_different_road_side(self):
        req = RequirementOutput(floors=1, bedrooms=2, road_side="North")
        layout = generate_layout(req)
        self.assertEqual(layout.metadata.get("road_side"), "North")
        
    def test_8_different_entrance_direction(self):
        req = RequirementOutput(floors=1, bedrooms=2, entrance_direction="East")
        layout = generate_layout(req)
        self.assertEqual(layout.metadata.get("entrance_direction"), "East")
        
    def test_9_small_but_valid_plot(self):
        # We know building width is around 10-15m depending on rooms
        # 25x25 should fit
        req = RequirementOutput(floors=1, bedrooms=2, plot_width=25, plot_depth=25)
        layout = generate_layout(req)
        self.assertTrue(layout.building_width <= 25)
        self.assertTrue(layout.building_depth <= 25)
        
    def test_10_oversized_impossible_plot(self):
        # Extremely small plot shouldn't fit 4BHK
        req = RequirementOutput(floors=2, bedrooms=4, plot_width=5, plot_depth=5)
        with self.assertRaises(ValueError):
            generate_layout(req)

    def test_11_topological_adjacency(self):
        req = RequirementOutput(
            house_style="modern_kerala",
            floors=2, bedrooms=4, bathrooms=2, parking_spaces=2, balconies=1
        )
        layout = generate_layout(req)
        f1_rooms = layout.floors[0].rooms
        f2_rooms = layout.floors[1].rooms
        
        # Helper to check if rects touch (by expanding slightly)
        def rects_overlap(x1, y1, w1, d1, x2, y2, w2, d2, eps=1e-2):
            return not (x1 + w1 + eps <= x2 or x2 + w2 + eps <= x1 or
                        y1 + d1 + eps <= y2 or y2 + d2 + eps <= y1)
                        
        def touches(room1, room2):
            return rects_overlap(room1.x, room1.y, room1.width, room1.depth,
                                 room2.x, room2.y, room2.width, room2.depth)
                                 
        main_ent = next((r for r in f1_rooms if r.room_type == RoomType.main_entrance), None)
        living = next((r for r in f1_rooms if r.room_type == RoomType.living), None)
        dining = next((r for r in f1_rooms if r.room_type == RoomType.dining), None)
        kitchen = next((r for r in f1_rooms if r.room_type == RoomType.kitchen), None)
        stair = next((r for r in f1_rooms if r.room_type == RoomType.staircase), None)
        
        self.assertIsNotNone(main_ent, "Main entrance must exist")
        self.assertTrue(touches(main_ent, living), "Main entrance must connect to Living")
        self.assertTrue(touches(dining, living), "Dining must touch Living")
        self.assertTrue(touches(dining, kitchen), "Dining must touch Kitchen")
        self.assertTrue(touches(stair, dining), "Staircase must touch Dining/circulation")
        
        u_stair = next((r for r in f2_rooms if r.room_type == RoomType.staircase), None)
        u_landing = next((r for r in f2_rooms if r.room_type == RoomType.corridor), None)
        
        self.assertTrue(touches(u_stair, u_landing), "Upper Staircase must touch Upper Landing")
        
        for r in f2_rooms:
            if r.room_type in (RoomType.bedroom, RoomType.bathroom):
                self.assertTrue(touches(r, u_landing), f"{r.name} must touch Upper Landing")
                
        balcony = next((r for r in f2_rooms if r.room_type == RoomType.balcony), None)
        balcony_touches_room = any(touches(balcony, r) for r in f2_rooms if r != balcony)
        self.assertTrue(balcony_touches_room, "Balcony must touch a host room")

if __name__ == '__main__':
    unittest.main()
