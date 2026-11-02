import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.requirements.parser import parse_requirements
from backend.requirements.models import RequirementOutput
from pydantic import ValidationError

class TestRequirements(unittest.TestCase):
    def test_1_full_prompt(self):
        text = "Create a modern Kerala 4BHK house with 2 floors, 2 bathrooms, 2-car parking and a balcony."
        req = parse_requirements(text)
        self.assertEqual(req.house_style, "modern_kerala")
        self.assertEqual(req.bedrooms, 4)
        self.assertEqual(req.floors, 2)
        self.assertEqual(req.bathrooms, 2)
        self.assertEqual(req.parking_spaces, 2)
        self.assertEqual(req.balconies, 1)
        self.assertIsNone(req.terraces)
        
    def test_2_contemporary(self):
        text = "Build a contemporary four bedroom house with two floors and parking for two cars."
        req = parse_requirements(text)
        self.assertEqual(req.house_style, "contemporary")
        self.assertEqual(req.bedrooms, 4)
        self.assertEqual(req.floors, 2)
        self.assertEqual(req.parking_spaces, 2)
        self.assertIsNone(req.bathrooms)
        self.assertIsNone(req.balconies)
        
    def test_3_traditional_zero(self):
        text = "Traditional Kerala 3BHK single floor house with no balcony and no parking."
        req = parse_requirements(text)
        self.assertEqual(req.house_style, "traditional_kerala")
        self.assertEqual(req.bedrooms, 3)
        self.assertEqual(req.floors, 1)
        self.assertEqual(req.balconies, 0)
        self.assertEqual(req.parking_spaces, 0)
        
    def test_4_luxury_duplex_special(self):
        text = "Luxury duplex with master bedroom with attached bathroom, home office and prayer room."
        req = parse_requirements(text)
        self.assertEqual(req.house_style, "luxury")
        self.assertEqual(req.floors, 2)
        self.assertIn("master bedroom with attached bathroom", req.special_requirements)
        self.assertIn("home office", req.special_requirements)
        self.assertIn("prayer room", req.special_requirements)
        
    def test_5_plot_and_directions(self):
        text = "Modern house on a 30 ft x 50 ft plot with north road and east-facing entrance."
        req = parse_requirements(text)
        self.assertEqual(req.house_style, "modern")
        self.assertEqual(req.plot_width, 30.0)
        self.assertEqual(req.plot_depth, 50.0)
        self.assertEqual(req.road_side, "north")
        self.assertEqual(req.entrance_direction, "east")
        
    def test_6_minimal(self):
        text = "4BHK house"
        req = parse_requirements(text)
        self.assertEqual(req.bedrooms, 4)
        self.assertIsNone(req.floors)
        self.assertIsNone(req.house_style)
        
    def test_edge_zero_balcony(self):
        req = parse_requirements("house with no balcony")
        self.assertEqual(req.balconies, 0)
        
    def test_edge_zero_parking(self):
        req = parse_requirements("house without parking")
        self.assertEqual(req.parking_spaces, 0)
        
    def test_edge_two_storey(self):
        req = parse_requirements("two-storey 3 bedroom house")
        self.assertEqual(req.floors, 2)
        self.assertEqual(req.bedrooms, 3)
        
    def test_edge_balconies_terraces(self):
        req = parse_requirements("2 balconies and 1 terrace")
        self.assertEqual(req.balconies, 2)
        self.assertEqual(req.terraces, 1)
        
    def test_edge_parking(self):
        req = parse_requirements("parking for 3 cars")
        self.assertEqual(req.parking_spaces, 3)

    def test_validation_errors(self):
        with self.assertRaises(ValidationError):
            RequirementOutput(floors=0)
        with self.assertRaises(ValidationError):
            RequirementOutput(bedrooms=-1)

if __name__ == "__main__":
    unittest.main()
