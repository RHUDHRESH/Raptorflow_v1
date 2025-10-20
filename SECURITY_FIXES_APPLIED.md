# Security Fixes Applied - RaptorFlow

This document summarizes the security fixes applied based on the red flags review (REG_FLAGS_REVIEW.md).

## Summary of Changes

All **5 critical security issues** identified in the review have been fixed:

1. ✅ **Wildcard CORS with credentials** (High)
2. ✅ **Supabase responses assumed to contain data** (Medium)
3. ✅ **Missing explicit tenant ownership checks** (High)
4. ✅ **Blocking Supabase calls inside async endpoints** (Medium)
5. ✅ **Intake path missing user attribution** (Medium)

---

## Detailed Fixes

### 1. Fixed Wildcard CORS with Credentials (High Priority)

**Location:** `backend/main.py:73-95`

**Problem:** The API enabled `allow_credentials=True` with `allow_origins=["*"]`, which browsers reject and encourages unsafe wildcard configurations in production.

**Fix Applied:**
- Replaced wildcard `["*"]` with explicit development origins
- Added common development URLs: `http://localhost:3000`, `http://localhost:5173` (Vite), and `127.0.0.1` variants
- Added security comment explaining why wildcard with credentials is dangerous
- Production configuration remains properly secured with explicit domain list

**Code Changes:**
```python
# SECURITY: Never use wildcard origins with credentials - browsers reject this
if os.getenv('ENVIRONMENT') == 'production':
    allowed_origins = [
        os.getenv('FRONTEND_URL', 'https://app.raptorflow.in'),
        "https://raptorflow.in"
    ]
else:
    # Default to explicit development origin instead of wildcard
    allowed_origins = [
        os.getenv('FRONTEND_URL', 'http://localhost:3000'),
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
```

---

### 2. Added Proper Error Handling for Supabase Responses (Medium Priority)

**Locations:**
- `backend/main.py:167-211` (intake endpoint)
- `backend/api/client.py:41-98` (client helper)

**Problem:** Multiple endpoints indexed into `result.data[0]` immediately after insert/select calls. If Supabase returns an error payload or empty list (common when RLS blocks the write), the API throws `IndexError`, leaking stack traces.

**Fix Applied:**
- Check for `.error` attribute before accessing data
- Verify `.data` is non-empty before indexing
- Return proper HTTP status codes (500 for DB errors, 403 for access denied)
- Log errors appropriately for debugging

**Code Changes:**
```python
# Check for errors and valid data
if hasattr(result, 'error') and result.error:
    logger.error(f"Database error creating business: {result.error}")
    raise HTTPException(status_code=500, detail="Failed to create business")

if not result.data or len(result.data) == 0:
    logger.error("Business insert returned no data")
    raise HTTPException(status_code=500, detail="Failed to create business")

business_id = result.data[0]['id']
```

**Also added user_id to all database inserts** for proper RLS enforcement.

---

### 3. Added Explicit Tenant Ownership Checks (High Priority)

**Locations:**
- `backend/main.py:219-251` (run_research)
- `backend/main.py:316-345` (analyze_positioning)
- `backend/main.py:402-445` (generate_icps)
- `backend/main.py:468-522` (create_move)

**Problem:** `run_research` and other endpoints fetch business by ID without verifying the authenticated user owns it, relying solely on comments that "RLS will handle this". If RLS is misconfigured or bypassed (e.g., via service-role keys), users could enumerate other tenants' data.

**Fix Applied:**
- Added explicit ownership verification in all business-related endpoints
- Compare `business.user_id` against `request.state.user_id` before processing
- Return 403 Forbidden when ownership doesn't match
- Added security logging for access attempts
- Added comment: "SECURITY: Explicit tenant ownership verification - Never rely solely on RLS"

**Code Changes:**
```python
# SECURITY: Explicit tenant ownership verification
# Never rely solely on RLS - verify in application layer
business_owner_id = biz.data.get('user_id')
if business_owner_id != user_id:
    logger.warning(f"Access denied: User {user_id} attempted to access business {business_id} owned by {business_owner_id}")
    raise HTTPException(status_code=403, detail="Access denied - you do not own this business")
```

**Endpoints Protected:**
- `/api/research/{business_id}` - Research analysis
- `/api/positioning/{business_id}` - Positioning generation
- `/api/icps/{business_id}` - ICP generation
- `/api/moves/{business_id}` - Campaign/move creation

---

### 4. Converted Blocking Supabase Calls to Async (Medium Priority)

**Locations:**
- `backend/main.py:1-4` (imports)
- `backend/main.py:101-109` (async helper)
- All critical endpoints updated to use async wrapper

**Problem:** All Supabase interactions call synchronous `.execute()` inside `async def` routes. These blocking calls tie up the event loop under load, leading to head-of-line blocking for other clients.

**Fix Applied:**
- Added `run_in_threadpool` import from `fastapi.concurrency`
- Created `async_db_query()` helper function to wrap blocking Supabase calls
- Updated all critical endpoints to use async wrapper for database operations
- Prevents event loop blocking under concurrent load

**Code Changes:**
```python
from fastapi.concurrency import run_in_threadpool

async def async_db_query(query_fn):
    """
    Execute blocking Supabase query in thread pool to avoid blocking event loop.

    Usage: result = await async_db_query(lambda: supabase.table('x').select('*').execute())
    """
    return await run_in_threadpool(query_fn)

# Usage in endpoints:
biz = await async_db_query(
    lambda: supabase.table('businesses').select('*').eq('id', business_id).single().execute()
)
```

**Endpoints Updated:**
- `/api/intake` - Business creation
- `/api/research/{business_id}` - Research queries
- `/api/positioning/{business_id}` - Positioning queries
- `/api/icps/{business_id}` - ICP queries
- `/api/moves/{business_id}` - Move queries

---

### 5. Added User Attribution to Intake Path (Medium Priority)

**Locations:**
- `backend/main.py:166-211` (create_business endpoint)
- `backend/api/client.py:23-98` (intake_business helper)

**Problem:** The API client helper inserts businesses and subscriptions without persisting a `user_id`, making it impossible to enforce row-level security downstream.

**Fix Applied:**
- Added `user_id` parameter to `intake_business()` function signature
- Persist `user_id` in both `businesses` and `subscriptions` table inserts
- Updated main.py endpoint to pass `user_id` from request state
- Enhanced error messages to indicate RLS-related failures

**Code Changes:**

In `backend/api/client.py`:
```python
async def intake_business(
    self,
    name: str,
    industry: str,
    location: str,
    description: str,
    goals: str,
    user_id: Optional[str] = None  # Add user_id parameter
) -> Dict[str, Any]:
    # ...
    result = supabase.table('businesses').insert({
        'name': name,
        'industry': industry,
        'location': location,
        'description': description,
        'goals': {'text': goals},
        'user_id': user_id  # Persist user attribution
    }).execute()
```

In `backend/main.py`:
```python
# Save business (async to avoid blocking event loop)
result = await async_db_query(lambda: supabase.table('businesses').insert({
    'name': intake.name,
    'industry': intake.industry,
    'location': intake.location,
    'description': intake.description,
    'goals': {'text': intake.goals},
    'user_id': user_id  # Add user_id for RLS
}).execute())
```

---

## Security Improvements Summary

### Defense in Depth
- **Application-layer authorization** now complements database-level RLS
- **Explicit ownership checks** prevent tenant data enumeration
- **Proper error handling** prevents information leakage via stack traces

### Performance Improvements
- **Async database operations** prevent event loop blocking
- **Better scalability** under concurrent load
- **Improved responsiveness** for all clients

### Audit Trail
- **Security logging** for all access denial attempts
- **User attribution** on all data modifications
- **Enhanced debugging** capabilities

### Configuration Security
- **No wildcard CORS** with credentials
- **Explicit origin lists** for development and production
- **Environment-based configuration** prevents misconfiguration

---

## Testing Recommendations

1. **Test RLS Policies:** Verify that row-level security policies work correctly with user_id
2. **Test Ownership Checks:** Attempt to access another user's business (should return 403)
3. **Test CORS:** Verify CORS configuration works with your frontend
4. **Load Testing:** Verify async improvements under concurrent load
5. **Error Handling:** Test with misconfigured Supabase to verify error messages

---

## Migration Notes

### Database Schema
Ensure these columns exist:
- `businesses.user_id` (UUID, foreign key to auth.users)
- `subscriptions.user_id` (UUID, foreign key to auth.users)

### Row-Level Security Policies
Update RLS policies to enforce user ownership:
```sql
-- Example RLS policy for businesses table
CREATE POLICY "Users can only access their own businesses"
ON businesses
FOR ALL
USING (auth.uid() = user_id);
```

### Environment Variables
Ensure these are set:
- `ENVIRONMENT` - Set to "production" in production
- `FRONTEND_URL` - Your frontend URL (development and production)

---

## Files Modified

1. `backend/main.py` - Main API file with all endpoint fixes
2. `backend/api/client.py` - Client helper with user attribution fixes

---

## Verification

All fixes have been applied and are ready for testing. The codebase now follows security best practices:

- ✅ No wildcard CORS with credentials
- ✅ Explicit tenant ownership verification
- ✅ Proper error handling for all database operations
- ✅ Async/await for non-blocking database calls
- ✅ User attribution throughout the data flow

**Status:** All identified security issues have been resolved.
