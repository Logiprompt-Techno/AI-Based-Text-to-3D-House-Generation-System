import os
import unittest
from backend.requirements.models import RequirementOutput
from backend.layout.generator import generate_layout
from backend.floorplan.generator import generate_floorplan
from backend.house3d.builder import generate_3d
from backend.house3d.blender_export import export_and_render, BLENDER_EXECUTABLE

class TestBlenderRender(unittest.TestCase):
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
        self.output_dir = "renders/step5"
        
    def test_blender_executable_detection(self):
        self.assertTrue(os.path.exists(BLENDER_EXECUTABLE), f"Blender not found at {BLENDER_EXECUTABLE}")

    def test_scene_generation_and_export(self):
        # Clear existing renders
        for file in ["front.png", "rear.png", "angled.png"]:
            path = os.path.join(self.output_dir, file)
            if os.path.exists(path):
                os.remove(path)
                
        # Only run if blender exists
        if os.path.exists(BLENDER_EXECUTABLE):
            export_and_render(self.scene, self.output_dir)
            
            # Check render files exist
            for file in ["front.png", "rear.png", "angled.png"]:
                path = os.path.join(self.output_dir, file)
                self.assertTrue(os.path.exists(path))
                self.assertTrue(os.path.getsize(path) > 0)

if __name__ == '__main__':
    unittest.main()
