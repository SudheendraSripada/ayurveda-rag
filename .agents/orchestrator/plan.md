# Project Plan: Ayurvedic RAG System

## Mission Overview
Deliver an Ayurvedic RAG platform incorporating:
1. Multi-User Authentication & Isolation (Register/Login/Logout, session/token management, botanical dark theme UI, strict user isolation).
2. Database-Backed Persistent Chat Storage (Users, sessions, chat history, citations, metadata persistence & retrieval).
3. Real-Time Token Streaming (Fast & progressive SSE/WebSocket streaming on `/api/chat`, Gemini integration, smooth markdown & citation rendering).
4. Enhanced Ayurvedic Model Intelligence & Scriptural Grounding (31 digitized scriptures, Tridosha root-cause diagnosis, Perplexity-style citations [1], [2] with interactive popovers).
5. Comprehensive automated test suite (Auth, isolation, DB persistence, streaming, and scriptural RAG).

## Execution Roadmap
1. **Phase 0: Survey & Discovery**
   - Explorer 1: Codebase architecture, backend framework (FastAPI/Express/Flask/Next), DB setup, dependencies, API endpoints.
   - Explorer 2: Existing frontend UI architecture, botanical dark theme, chat UI, auth UI, streaming client implementation, markdown/popover rendering.
   - Explorer 3: RAG pipeline, 31 digitized scriptures context aggregator, vector store / retrieval, prompt templates, Tridosha diagnostic engine, citation generator.
2. **Phase 1: Architecture Synthesis & Decomposition (PROJECT.md)**
   - Consolidate explorer findings.
   - Define exact milestones (M1: Auth & User Isolation, M2: DB-backed Session & Chat Persistence, M3: Real-Time SSE Token Streaming & Frontend Integration, M4: Ayurvedic Model Intelligence & Scriptural RAG Grounding).
   - Define formal interface contracts & code layout.
3. **Phase 2: Dual Track Execution**
   - E2E Testing Track: Design test harness, opaque-box tests (Tiers 1-4) covering Auth, DB isolation, Streaming, Scriptural retrieval, and Tridosha diagnosis.
   - Implementation Track: Milestone by milestone development using full iteration loop (Explorer -> Worker -> Reviewers -> Challengers -> Auditor -> Gate).
4. **Phase 3: Final E2E Verification & Adversarial Hardening**
   - Pass 100% E2E test suite.
   - Tier 5 Adversarial Coverage Hardening.
5. **Phase 4: Final Synthesis & Human Reporting**
