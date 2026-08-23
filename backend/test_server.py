import unittest
import json
from fastapi.testclient import TestClient
from main import app
import database

class TestAyurvedaDoctorChatServer(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        database.init_db()
        
    def test_root_serves_html(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Sushruta AI", response.text)
        self.assertIn("Sage Dhanvantari", response.text)
        self.assertIn("landing-site-language", response.text)
        self.assertIn("chat-response-language", response.text)
        self.assertIn("auth-modal", response.text)
        
    def test_static_css_served(self):
        response = self.client.get("/static/style.css")
        self.assertEqual(response.status_code, 200)
        self.assertIn("--bg-dark", response.text)
        self.assertIn("auth-user-pill", response.text)
        self.assertIn("streaming-cursor", response.text)
        
    def test_static_js_served(self):
        response = self.client.get("/static/app.js")
        self.assertEqual(response.status_code, 200)
        self.assertIn("AUTH_TOKEN_KEY", response.text)
        self.assertIn("/api/chat/stream", response.text)
        
    def test_auth_signup_and_login_flow(self):
        unique_email = f"vaidya_{database.secrets.token_hex(4)}@ayurveda.test"
        # 1. Sign up
        signup_res = self.client.post("/api/auth/signup", json={
            "email": unique_email,
            "password": "Password123!",
            "full_name": "Dr. Charaka"
        })
        self.assertEqual(signup_res.status_code, 200)
        data = signup_res.json()
        self.assertTrue(data["success"])
        token = data["token"]
        self.assertIsNotNone(token)
        
        # 2. Get Me
        me_res = self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.json()["user"]["email"], unique_email)
        
        # 3. Log in again
        login_res = self.client.post("/api/auth/login", json={
            "email": unique_email,
            "password": "Password123!"
        })
        self.assertEqual(login_res.status_code, 200)
        self.assertTrue(login_res.json()["success"])

    def test_multi_user_isolation(self):
        user1_email = f"u1_{database.secrets.token_hex(4)}@test.com"
        user2_email = f"u2_{database.secrets.token_hex(4)}@test.com"
        
        u1_token = self.client.post("/api/auth/signup", json={
            "email": user1_email, "password": "pass", "full_name": "User 1"
        }).json()["token"]
        
        u2_token = self.client.post("/api/auth/signup", json={
            "email": user2_email, "password": "pass", "full_name": "User 2"
        }).json()["token"]
        
        # User 1 creates session
        ses_res = self.client.post("/api/chat/sessions", json={
            "title": "User 1 Private Consultation"
        }, headers={"Authorization": f"Bearer {u1_token}"})
        self.assertEqual(ses_res.status_code, 200)
        session_id = ses_res.json()["session"]["id"]
        
        # User 2 list sessions -> User 1 session should NOT be in list
        u2_sessions = self.client.get("/api/chat/sessions", headers={"Authorization": f"Bearer {u2_token}"}).json()["sessions"]
        session_ids = [s["id"] for s in u2_sessions]
        self.assertNotIn(session_id, session_ids)
        
        # User 2 tries to fetch messages from User 1's session -> should get empty list / unauthorized
        u2_msgs = self.client.get(f"/api/chat/sessions/{session_id}/messages", headers={"Authorization": f"Bearer {u2_token}"}).json()["messages"]
        self.assertEqual(len(u2_msgs), 0)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAyurvedaDoctorChatServer)
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    assert res.wasSuccessful(), "Server tests failed"
