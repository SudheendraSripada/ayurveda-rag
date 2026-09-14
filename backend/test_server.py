import unittest
import json
from fastapi.testclient import TestClient
from main import app
import database

class TestAyurvedaDoctorChatServer(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        database.init_db()
        
    def tearDown(self):
        conn = database.get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE email LIKE '%@ayurveda.test' OR email LIKE '%@test.com'")
        cursor.execute("DELETE FROM chat_sessions WHERE title LIKE '%Private Consultation%'")
        conn.commit()
        conn.close()
        
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

    def test_books_catalog_endpoints(self):
        # 1. Search books list
        res = self.client.get("/api/books?limit=10")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("books", data)
        self.assertIn("total", data)
        self.assertGreater(data["total"], 3400)
        self.assertEqual(len(data["books"]), 10)
        
        # 2. Filter by category
        res_cat = self.client.get("/api/books?category=ఉప వేదాలు&limit=5")
        self.assertEqual(res_cat.status_code, 200)
        data_cat = res_cat.json()
        for b in data_cat["books"]:
            self.assertEqual(b["category"], "ఉప వేదాలు")
            
        # 3. Filter by query
        res_q = self.client.get("/api/books?query=Charaka&limit=5")
        self.assertEqual(res_q.status_code, 200)
        data_q = res_q.json()
        self.assertGreater(data_q["total"], 0)
        
        # 4. Catalog stats
        res_stats = self.client.get("/api/books/stats")
        self.assertEqual(res_stats.status_code, 200)
        stats = res_stats.json()
        self.assertGreater(stats["total_books"], 3400)
        self.assertGreater(stats["ayurveda_books"], 50)
        self.assertIn("top_categories", stats)
        
        # 5. Catalog categories
        res_cats = self.client.get("/api/books/categories")
        self.assertEqual(res_cats.status_code, 200)
        cats = res_cats.json()
        self.assertIn("categories", cats)
        self.assertGreater(len(cats["categories"]), 10)
        
        # 6. Specific book detail
        first_book_id = data["books"][0]["id"]
        res_b = self.client.get(f"/api/books/{first_book_id}")
        self.assertEqual(res_b.status_code, 200)
        self.assertEqual(res_b.json()["book"]["id"], first_book_id)

    def test_config_status_endpoint(self):
        res = self.client.get("/api/config-status")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("pinecone_configured", data)
        self.assertTrue(data["pinecone_configured"])

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAyurvedaDoctorChatServer)
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    assert res.wasSuccessful(), "Server tests failed"
