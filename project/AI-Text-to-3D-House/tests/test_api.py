import unittest
from fastapi.testclient import TestClient
from backend.api.main import app
import os

client = TestClient(app)

class TestAPI(unittest.TestCase):
    def test_health(self):
        response = client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_generate(self):
        # We test with a basic prompt
        response = client.post("/api/generate", json={"prompt": "Modern Kerala 4BHK 2 floors 2 bathrooms 2-car parking balcony"})
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("requirements", data)
        self.assertEqual(data["requirements"]["bathrooms"], 2)
        self.assertEqual(data["requirements"]["bedrooms"], 4)
        self.assertEqual(data["requirements"]["floors"], 2)
        
        self.assertIn("layout", data)
        self.assertIn("floorplan", data)
        self.assertIn("scene", data)
        self.assertIn("renders", data)

        # Check render files actually exist
        renders = data["renders"]
        for key, path in renders.items():
            # Path is like /renders/id/file.png
            # We strip the leading slash to check local filesystem
            local_path = path.lstrip("/")
            self.assertTrue(os.path.exists(local_path))

if __name__ == "__main__":
    unittest.main()
