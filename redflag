diff --git a/REG_FLAGS_REVIEW.md b/REG_FLAGS_REVIEW.md
new file mode 100644
index 0000000000000000000000000000000000000000..4e191b1c3de55fbbee8ad26a58a5d04ebc28d39f
--- /dev/null
+++ b/REG_FLAGS_REVIEW.md
@@ -0,0 +1,34 @@
+# RaptorFlow Red Flags Review
+
+## Summary
+- Highlighted CORS configuration that combines wildcard origins with credentialed requests, creating an easy misconfiguration target.
+- Identified brittle Supabase access patterns that assume happy-path responses and risk runtime crashes and blocking behaviour.
+- Flagged multi-tenant access control gaps where ownership checks rely on implicit database rules instead of explicit guards in the API layer.
+- Noted missing tenancy metadata in helper APIs, making downstream row-level policies unenforceable.
+
+## Findings
+
+### 1. Wildcard CORS with credentials (High)
+The API enables `allow_credentials=True` while leaving the default `allow_origins=["*"]`. Browsers will reject such responses and it encourages copying the unsafe wildcard configuration into production, undermining the stricter list below it.【F:backend/main.py†L74-L87】
+
+*Recommendation:* Default to an explicit development origin (e.g. `http://localhost:3000`) and fail fast if a wildcard slips into a credentialed deployment.
+
+### 2. Supabase responses assumed to contain data (Medium)
+Multiple endpoints index into `result.data[0]` immediately after `insert`/`select` calls. If Supabase returns an error payload or an empty list (common when RLS blocks the write), the API will throw `IndexError`, leaking stack traces and failing the request.【F:backend/main.py†L159-L170】【F:backend/api/client.py†L42-L66】
+
+*Recommendation:* Check for `.error` and that `.data` is a non-empty sequence before indexing; surface domain-specific errors to clients.
+
+### 3. Missing explicit tenant ownership checks (High)
+`run_research` fetches any business by ID and proceeds without verifying that the authenticated user owns it, relying solely on a comment that "RLS will handle this". If RLS is misconfigured or bypassed (e.g. via service-role keys), a user could enumerate other tenants' data.【F:backend/main.py†L197-L238】
+
+*Recommendation:* Compare `biz.data.get("user_id")` against `request.state.user_id` before continuing and return 403 when they differ.
+
+### 4. Blocking Supabase calls inside async endpoints (Medium)
+All Supabase interactions call the synchronous `.execute()` inside `async def` routes and websocket producers. These blocking calls tie up the event loop under load, leading to head-of-line blocking for other clients.【F:backend/main.py†L159-L178】【F:backend/api/client.py†L42-L152】
+
+*Recommendation:* Move database access to thread executors (e.g. `await run_in_threadpool(...)`) or adopt an async database client.
+
+### 5. Intake path misses user attribution (Medium)
+The API client helper that the frontend likely calls inserts businesses without persisting a `user_id`, making it impossible to enforce row-level security downstream. Subscriptions created alongside also lack user references.【F:backend/api/client.py†L36-L66】
+
+*Recommendation:* Thread authenticated user identifiers through the client helper and persist them alongside business/subscription rows.