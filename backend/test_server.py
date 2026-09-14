import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient  # noqa: E402
import main  # noqa: E402
from main import app  # noqa: E402
import database  # noqa: E402
import pinecone_helper  # noqa: E402
import gemini_helper  # noqa: E402
from datetime import datetime, timezone, timedelta  # noqa: E402

class TestAyurvedaDoctorChatServer(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        database.init_db()
        
    def tearDown(self):
        conn = database.get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE email LIKE '%@ayurveda.test' OR email LIKE '%@test.com'")
        cursor.execute("DELETE FROM chat_sessions WHERE title LIKE '%Private Consultation%' OR title LIKE '%Test%'")
        cursor.execute("DELETE FROM auth_tokens WHERE user_id NOT IN (SELECT id FROM users)")
        cursor.execute("DELETE FROM chat_messages WHERE session_id NOT IN (SELECT id FROM chat_sessions)")
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

    def test_api_health_endpoint(self):
        res1 = self.client.get("/api")
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.json()["status"], "healthy")
        res2 = self.client.get("/api/health")
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json()["status"], "healthy")
        
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

    def test_idor_chat_deletion_protection(self):
        # 1. User 1 creates session and message
        u1_res = self.client.post("/api/auth/signup", json={
            "email": f"victim_{database.secrets.token_hex(4)}@test.com", "password": "pass", "full_name": "Victim"
        }).json()
        u1_token = u1_res["token"]
        u1_id = u1_res["user"]["id"]

        ses = database.create_chat_session(u1_id, "Victim Consultation")
        session_id = ses["id"]
        database.add_chat_message(session_id, u1_id, "user", "Confidential clinical data")

        # 2. Unauthenticated deletion attempt -> 401 Unauthorized
        unauth_del = self.client.delete(f"/api/chat/sessions/{session_id}")
        self.assertEqual(unauth_del.status_code, 401)

        # 3. Attacker User 2 signs up and tries to delete User 1's session -> denied
        u2_token = self.client.post("/api/auth/signup", json={
            "email": f"attacker_{database.secrets.token_hex(4)}@test.com", "password": "pass", "full_name": "Attacker"
        }).json()["token"]

        del_res = self.client.delete(f"/api/chat/sessions/{session_id}", headers={"Authorization": f"Bearer {u2_token}"})
        self.assertEqual(del_res.status_code, 200)
        self.assertFalse(del_res.json()["success"])

        # 4. Verify User 1's messages and session are NOT deleted
        msgs = database.get_session_messages(session_id, u1_id)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0]["content"], "Confidential clinical data")

        # 5. Now User 1 legitimately deletes session
        legit_del = self.client.delete(f"/api/chat/sessions/{session_id}", headers={"Authorization": f"Bearer {u1_token}"})
        self.assertEqual(legit_del.status_code, 200)
        self.assertTrue(legit_del.json()["success"])
        self.assertEqual(len(database.get_session_messages(session_id, u1_id)), 0)

    def test_config_protection_and_toggle(self):
        # 1. Anonymous attempt -> 401 Unauthorized
        res_anon = self.client.post("/api/config", json={"pinecone_index_name": "hacked-index"})
        self.assertEqual(res_anon.status_code, 401)

        # 2. Authenticated user without ALLOW_CONFIG_OVERWRITE -> 403 Forbidden
        user_res = self.client.post("/api/auth/signup", json={
            "email": f"cfg_{database.secrets.token_hex(4)}@test.com", "password": "pass", "full_name": "Config User"
        }).json()
        token = user_res["token"]

        prev_toggle = os.environ.get("ALLOW_CONFIG_OVERWRITE")
        prev_admin = os.environ.get("ADMIN_TOKEN")
        try:
            if "ALLOW_CONFIG_OVERWRITE" in os.environ:
                del os.environ["ALLOW_CONFIG_OVERWRITE"]
            res_forbidden = self.client.post(
                "/api/config",
                json={"pinecone_index_name": "ayurveda-index"},
                headers={"Authorization": f"Bearer {token}"}
            )
            self.assertEqual(res_forbidden.status_code, 403)

            # 3. Enabled ALLOW_CONFIG_OVERWRITE with user token -> 200 OK
            os.environ["ALLOW_CONFIG_OVERWRITE"] = "true"
            res_ok = self.client.post(
                "/api/config",
                json={"pinecone_index_name": "ayurveda-index"},
                headers={"Authorization": f"Bearer {token}"}
            )
            self.assertEqual(res_ok.status_code, 200)
            self.assertEqual(res_ok.json()["status"], "success")

            # 4. Admin token authentication via ADMIN_TOKEN
            os.environ["ADMIN_TOKEN"] = "super-secret-admin-key"
            res_admin = self.client.post(
                "/api/config",
                json={"pinecone_index_name": "ayurveda-index"},
                headers={"Authorization": "Bearer super-secret-admin-key"}
            )
            self.assertEqual(res_admin.status_code, 200)
            self.assertEqual(res_admin.json()["status"], "success")
        finally:
            if prev_toggle is not None:
                os.environ["ALLOW_CONFIG_OVERWRITE"] = prev_toggle
            elif "ALLOW_CONFIG_OVERWRITE" in os.environ:
                del os.environ["ALLOW_CONFIG_OVERWRITE"]
            if prev_admin is not None:
                os.environ["ADMIN_TOKEN"] = prev_admin
            elif "ADMIN_TOKEN" in os.environ:
                del os.environ["ADMIN_TOKEN"]

    def test_auth_token_expiration_and_cleanup(self):
        # 1. Sign up user
        res = self.client.post("/api/auth/signup", json={
            "email": f"expire_{database.secrets.token_hex(4)}@test.com", "password": "pass", "full_name": "Expiring User"
        }).json()
        token = res["token"]

        # Valid token works
        me_res = self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(me_res.status_code, 200)

        # 2. Artificially expire the token in database
        past_time = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
        conn = database.get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE auth_tokens SET expires_at = ? WHERE token = ?", (past_time, token))
        conn.commit()
        conn.close()

        # 3. GET /api/auth/me should now return 401 Unauthorized
        me_expired = self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(me_expired.status_code, 401)
        self.assertIsNone(database.get_user_by_token(token))

        # 4. Test cleanup_expired_tokens
        u_dummy = f"dummy_{database.secrets.token_hex(4)}@test.com"
        token_dummy = self.client.post("/api/auth/signup", json={
            "email": u_dummy, "password": "pass", "full_name": "Dummy User"
        }).json()["token"]

        conn = database.get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE auth_tokens SET expires_at = ? WHERE token = ?", (past_time, token_dummy))
        conn.commit()
        conn.close()

        cleaned = database.cleanup_expired_tokens()
        self.assertGreaterEqual(cleaned, 1)

        # 5. Legacy tokens without expires_at (NULL):
        # Recent legacy token (< 30 days) is accepted
        u_leg_recent = self.client.post("/api/auth/signup", json={
            "email": f"legrec_{database.secrets.token_hex(4)}@test.com", "password": "pass", "full_name": "Legacy Recent"
        }).json()
        tok_leg_recent = u_leg_recent["token"]
        conn = database.get_db()
        cursor = conn.cursor()
        recent_c = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
        cursor.execute("UPDATE auth_tokens SET expires_at = NULL, created_at = ? WHERE token = ?", (recent_c, tok_leg_recent))
        conn.commit()
        conn.close()
        self.assertIsNotNone(database.get_user_by_token(tok_leg_recent))

        # Expired legacy token (> 30 days) is rejected and invalidated
        u_leg_old = self.client.post("/api/auth/signup", json={
            "email": f"legold_{database.secrets.token_hex(4)}@test.com", "password": "pass", "full_name": "Legacy Old"
        }).json()
        tok_leg_old = u_leg_old["token"]
        conn = database.get_db()
        cursor = conn.cursor()
        old_c = (datetime.now(timezone.utc) - timedelta(days=35)).isoformat()
        cursor.execute("UPDATE auth_tokens SET expires_at = NULL, created_at = ? WHERE token = ?", (old_c, tok_leg_old))
        conn.commit()
        conn.close()
        self.assertIsNone(database.get_user_by_token(tok_leg_old))

        # Corrupted expires_at timestamp is rejected and deleted
        u_corrupt = self.client.post("/api/auth/signup", json={
            "email": f"corrupt_{database.secrets.token_hex(4)}@test.com", "password": "pass", "full_name": "Corrupt User"
        }).json()
        tok_corrupt = u_corrupt["token"]
        conn = database.get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE auth_tokens SET expires_at = 'invalid-timestamp-xyz' WHERE token = ?", (tok_corrupt,))
        conn.commit()
        conn.close()
        self.assertIsNone(database.get_user_by_token(tok_corrupt))

    def test_gemini_active_fallback_models_and_preference(self):
        # 1. Verify candidate models are active
        expected_models = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.1-flash-lite"]
        self.assertEqual(gemini_helper.DEFAULT_CANDIDATE_MODELS, expected_models)

        # 2. Verify model_name resolution prioritizes preferred model
        candidates = gemini_helper.resolve_candidate_models("gemini-3.5-flash")
        self.assertEqual(candidates[0], "gemini-3.5-flash")
        self.assertEqual(set(candidates), set(expected_models))

        custom = gemini_helper.resolve_candidate_models("custom-model")
        self.assertEqual(custom[0], "custom-model")

    def test_pinecone_singleton_client_and_index_caching(self):
        key = pinecone_helper.resolve_pinecone_api_key()
        if key:
            c1 = pinecone_helper.get_pinecone_client(key)
            c2 = pinecone_helper.get_pinecone_client(key)
            self.assertIs(c1, c2)

            idx1 = pinecone_helper.get_pinecone_index(key, "ayurveda-index")
            idx2 = pinecone_helper.get_pinecone_index(key, "ayurveda-index")
            self.assertIs(idx1, idx2)

    def test_chat_payload_model_name_and_cors(self):
        # 1. Verify ChatPayload accepts model_name
        payload = main.ChatPayload(
            messages=[main.ChatMessage(role="user", content="Namaste")],
            model_name="gemini-3.5-flash"
        )
        self.assertEqual(payload.model_name, "gemini-3.5-flash")

        # 2. Verify CORS middleware configuration prevents wildcard with credentials
        from fastapi.middleware.cors import CORSMiddleware
        for middleware in app.user_middleware:
            if middleware.cls == CORSMiddleware:
                allow_origins = middleware.kwargs.get("allow_origins", [])
                allow_credentials = middleware.kwargs.get("allow_credentials", False)
                if "*" in allow_origins:
                    self.assertFalse(allow_credentials, "allow_credentials must be False when allow_origins contains '*'")

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAyurvedaDoctorChatServer)
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    assert res.wasSuccessful(), "Server tests failed"
