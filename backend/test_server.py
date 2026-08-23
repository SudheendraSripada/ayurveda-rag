import unittest
from fastapi.testclient import TestClient
from main import app

class TestAyurvedaDoctorChatServer(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        
    def test_root_serves_html(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Sushruta AI", response.text)
        self.assertIn("Sage Dhanvantari", response.text)
        self.assertIn("landing-site-language", response.text)
        self.assertIn("chat-response-language", response.text)
        self.assertIn("Telugu", response.text)
        
    def test_static_css_served(self):
        response = self.client.get("/static/style.css")
        self.assertEqual(response.status_code, 200)
        self.assertIn("--bg-dark", response.text)
        self.assertIn("chat-response-lang-badge", response.text)
        
    def test_static_js_served(self):
        response = self.client.get("/static/app.js")
        self.assertEqual(response.status_code, 200)
        self.assertIn("I18N_DICTIONARY", response.text)
        self.assertIn("RESPONSE_LANG_STORAGE_KEY", response.text)
        
    def test_config_status_endpoint(self):
        response = self.client.get("/api/config-status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("configured", data)
        self.assertIn("pinecone_configured", data)
        self.assertIn("gemini_configured", data)
        
    def test_index_stats_endpoint(self):
        response = self.client.get("/api/index-stats")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("exists", data)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAyurvedaDoctorChatServer)
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    assert res.wasSuccessful(), "Server tests failed"
