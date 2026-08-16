import unittest
from fastapi.testclient import TestClient
from main import app

class TestFastAPIServer(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        
    def test_root_serves_html(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Sushruta", response.text)
        self.assertIn("Ayurvedic Remedy Finder", response.text)
        
    def test_static_css_served(self):
        response = self.client.get("/static/style.css")
        self.assertEqual(response.status_code, 200)
        self.assertIn("--primary", response.text)
        
    def test_static_js_served(self):
        response = self.client.get("/static/app.js")
        self.assertEqual(response.status_code, 200)
        self.assertIn("executeRemedySearch", response.text)
        
    def test_config_status_endpoint(self):
        response = self.client.get("/api/config-status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("configured", data)
        self.assertIn("pinecone_configured", data)
        self.assertIn("gemini_configured", data)
        
    def test_documents_endpoint(self):
        response = self.client.get("/api/documents")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)
        
    def test_index_stats_endpoint(self):
        response = self.client.get("/api/index-stats")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("exists", data)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFastAPIServer)
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    assert res.wasSuccessful(), "Server tests failed"
