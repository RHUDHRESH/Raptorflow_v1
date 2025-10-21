# API Endpoints - Complete Reference

**Status**: Organizations, Users, Projects, Payments - IMPLEMENTED ✅
**Date**: 2025-01-20
**Version**: v1.0.0

---

## Overview

RaptorFlow API provides a comprehensive set of endpoints for managing:
- **User profiles** - Account management, settings
- **Organizations** - Multi-tenant workspace management
- **Members** - Team collaboration with RBAC
- **Projects** - Threat intelligence project containers
- **Payments** - Subscription billing via Razorpay

All endpoints require authentication via JWT token (except webhooks).
Organization-scoped endpoints require `X-Organization-ID` header.

---

## Authentication

### Headers Required

```http
# All authenticated endpoints
Authorization: Bearer <JWT_TOKEN>

# Organization-scoped endpoints
X-Organization-ID: <UUID>
```

### Getting a JWT Token

1. Sign up/sign in via Supabase Auth
2. Get JWT token from Supabase client
3. Include in Authorization header

---

## Base URL

```
Development: http://localhost:8000/api/v1
Production: https://api.raptorflow.com/api/v1
```

---

## User Endpoints

### GET /users/me

Get current user's profile.

**Authentication**: Required
**Organization Context**: Not required

**Response**: `UserProfileResponse`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "display_name": "John Doe",
  "avatar_url": "https://...",
  "created_at": "2024-01-20T10:00:00",
  "updated_at": "2024-01-20T10:00:00"
}
```

**Example**:
```bash
curl -H "Authorization: Bearer $JWT" \
  http://localhost:8000/api/v1/users/me
```

---

### PATCH /users/me

Update current user's profile.

**Authentication**: Required
**Organization Context**: Not required

**Request**: `UpdateProfileRequest`
```json
{
  "display_name": "Jane Doe",
  "avatar_url": "https://example.com/avatar.jpg",
  "bio": "Security researcher",
  "settings": {
    "theme": "dark",
    "notifications": true
  }
}
```

**Response**: `UserProfileResponse`

**Example**:
```bash
curl -X PATCH \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{"display_name": "Jane Doe"}' \
  http://localhost:8000/api/v1/users/me
```

---

### DELETE /users/me

Delete current user's account (GDPR-compliant anonymization).

**Authentication**: Required
**Organization Context**: Not required

**Restrictions**: User must not be the last owner of any organization.

**Response**: `204 No Content`

**Example**:
```bash
curl -X DELETE \
  -H "Authorization: Bearer $JWT" \
  http://localhost:8000/api/v1/users/me
```

---

### GET /users/me/organizations

List all organizations the current user belongs to.

**Authentication**: Required
**Organization Context**: Not required

**Response**: `List[UserOrganizationResponse]`
```json
[
  {
    "org_id": "uuid",
    "org_name": "Acme Security",
    "org_slug": "acme-security",
    "role": "OWNER",
    "joined_at": "2024-01-15T10:00:00",
    "invitation_status": "accepted"
  }
]
```

---

### GET /users/me/activity

Get current user's activity summary.

**Authentication**: Required
**Organization Context**: Not required

**Response**: `UserActivityResponse`
```json
{
  "total_organizations": 3,
  "total_projects_created": 12,
  "total_indicators_created": 450,
  "recent_logins": [
    "2024-01-20T10:00:00",
    "2024-01-19T15:30:00"
  ],
  "last_active_at": "2024-01-20T10:00:00"
}
```

---

### GET /users/{user_id}

Get user profile by ID (must be in same organization).

**Authentication**: Required
**Organization Context**: Required

**Response**: `UserProfileResponse`

---

## Organization Endpoints

### GET /organizations

List all organizations the current user belongs to.

**Authentication**: Required
**Organization Context**: Not required

**Response**: `List[OrganizationResponse]`
```json
[
  {
    "id": "uuid",
    "name": "Acme Security",
    "slug": "acme-security",
    "description": "Threat intelligence team",
    "settings": {},
    "created_at": "2024-01-15T10:00:00",
    "member_count": 5,
    "current_user_role": "OWNER"
  }
]
```

**Example**:
```bash
curl -H "Authorization: Bearer $JWT" \
  http://localhost:8000/api/v1/organizations
```

---

### POST /organizations

Create new organization (current user becomes owner).

**Authentication**: Required
**Organization Context**: Not required

**Request**: `CreateOrganizationRequest`
```json
{
  "name": "Acme Security",
  "slug": "acme-security",
  "description": "Threat intelligence team"
}
```

**Validation**:
- `name`: 1-100 characters
- `slug`: 1-50 characters, lowercase alphanumeric + hyphens only
- `slug` must be unique globally

**Response**: `OrganizationResponse` (201 Created)

**Example**:
```bash
curl -X POST \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Security",
    "slug": "acme-security",
    "description": "Threat intelligence team"
  }' \
  http://localhost:8000/api/v1/organizations
```

---

### GET /organizations/{org_id}

Get organization details.

**Authentication**: Required
**Organization Context**: Not required (but user must be member)

**Response**: `OrganizationResponse`

---

### PATCH /organizations/{org_id}

Update organization details.

**Authentication**: Required
**Organization Context**: Required
**Permissions**: Admin or Owner

**Request**: `UpdateOrganizationRequest`
```json
{
  "name": "Updated Name",
  "description": "New description",
  "settings": {
    "timezone": "UTC",
    "default_sharing": "private"
  }
}
```

**Response**: `OrganizationResponse`

---

### DELETE /organizations/{org_id}

Delete organization (cascades to all related data).

**Authentication**: Required
**Organization Context**: Required
**Permissions**: Owner only

**Response**: `204 No Content`

---

## Member Management Endpoints

### GET /organizations/{org_id}/members

List all members of organization.

**Authentication**: Required
**Organization Context**: Required
**Permissions**: Any member can view

**Response**: `List[MemberResponse]`
```json
[
  {
    "user_id": "uuid",
    "email": "user@example.com",
    "display_name": "John Doe",
    "avatar_url": "https://...",
    "role": "EDITOR",
    "joined_at": "2024-01-15T10:00:00",
    "invitation_status": "accepted"
  }
]
```

---

### POST /organizations/{org_id}/members

Invite user to organization.

**Authentication**: Required
**Organization Context**: Required
**Permissions**: Admin or Owner

**Request**: `InviteMemberRequest`
```json
{
  "email": "newuser@example.com",
  "role": "EDITOR"
}
```

**Roles**: `VIEWER` (1), `EDITOR` (2), `ADMIN` (3), `OWNER` (4)

**Response**: `MemberResponse` (201 Created)

**Example**:
```bash
curl -X POST \
  -H "Authorization: Bearer $JWT" \
  -H "X-Organization-ID: $ORG_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "analyst@example.com",
    "role": "EDITOR"
  }' \
  http://localhost:8000/api/v1/organizations/$ORG_ID/members
```

---

### PATCH /organizations/{org_id}/members/{user_id}

Update member's role.

**Authentication**: Required
**Organization Context**: Required
**Permissions**: Admin or Owner

**Request**: `UpdateMemberRoleRequest`
```json
{
  "role": "ADMIN"
}
```

**Restrictions**:
- Cannot change own role
- Cannot remove last owner

**Response**: `MemberResponse`

---

### DELETE /organizations/{org_id}/members/{user_id}

Remove member from organization.

**Authentication**: Required
**Organization Context**: Required
**Permissions**: Admin or Owner (or self-removal)

**Restrictions**: Cannot remove last owner

**Response**: `204 No Content`

**Example** (self-removal):
```bash
curl -X DELETE \
  -H "Authorization: Bearer $JWT" \
  -H "X-Organization-ID: $ORG_ID" \
  http://localhost:8000/api/v1/organizations/$ORG_ID/members/$MY_USER_ID
```

---

## Project Endpoints

### GET /projects

List all projects in organization.

**Authentication**: Required
**Organization Context**: Required

**Query Parameters**:
- `include_archived` (bool): Include archived projects (default: false)

**Response**: `List[ProjectResponse]`
```json
[
  {
    "id": "uuid",
    "org_id": "uuid",
    "name": "APT28 Campaign Analysis",
    "description": "Tracking APT28 infrastructure",
    "tags": ["apt", "russia", "phishing"],
    "settings": {},
    "archived": false,
    "created_at": "2024-01-15T10:00:00",
    "updated_at": "2024-01-20T10:00:00",
    "created_by": "uuid",
    "indicator_count": 125,
    "threat_actor_count": 3
  }
]
```

**Example**:
```bash
curl -H "Authorization: Bearer $JWT" \
  -H "X-Organization-ID: $ORG_ID" \
  http://localhost:8000/api/v1/projects
```

---

### POST /projects

Create new project.

**Authentication**: Required
**Organization Context**: Required
**Permissions**: Editor or higher

**Request**: `CreateProjectRequest`
```json
{
  "name": "APT28 Campaign Analysis",
  "description": "Tracking APT28 infrastructure and TTPs",
  "tags": ["apt", "russia", "phishing"],
  "settings": {
    "auto_enrich": true,
    "sharing": "org"
  }
}
```

**Response**: `ProjectResponse` (201 Created)

**Example**:
```bash
curl -X POST \
  -H "Authorization: Bearer $JWT" \
  -H "X-Organization-ID: $ORG_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "APT28 Campaign",
    "tags": ["apt", "russia"]
  }' \
  http://localhost:8000/api/v1/projects
```

---

### GET /projects/{project_id}

Get project details.

**Authentication**: Required
**Organization Context**: Required

**Response**: `ProjectResponse`

---

### PATCH /projects/{project_id}

Update project.

**Authentication**: Required
**Organization Context**: Required
**Permissions**: Editor or higher

**Request**: `UpdateProjectRequest`
```json
{
  "name": "Updated Name",
  "description": "Updated description",
  "tags": ["apt", "russia", "ukraine"],
  "archived": false
}
```

**Response**: `ProjectResponse`

---

### DELETE /projects/{project_id}

Delete project (cascades to all indicators, threat actors, etc.).

**Authentication**: Required
**Organization Context**: Required
**Permissions**: Admin or higher

**Response**: `204 No Content`

---

### GET /projects/{project_id}/stats

Get project statistics.

**Authentication**: Required
**Organization Context**: Required

**Response**: `ProjectStatsResponse`
```json
{
  "total_indicators": 125,
  "total_threat_actors": 3,
  "total_campaigns": 2,
  "recent_activity_count": 15,
  "risk_score": 8.5
}
```

---

### POST /projects/{project_id}/archive

Archive project (hide from default view but preserve data).

**Authentication**: Required
**Organization Context**: Required
**Permissions**: Admin or higher

**Response**: `ProjectResponse`

---

### POST /projects/{project_id}/unarchive

Unarchive project.

**Authentication**: Required
**Organization Context**: Required
**Permissions**: Admin or higher

**Response**: `ProjectResponse`

---

## Payment Endpoints

### POST /payments/create-order

Create Razorpay payment order for subscription.

**Authentication**: Required
**Organization Context**: Required
**Permissions**: Owner only

**Request**: `CreateOrderRequest`
```json
{
  "plan_id": "pro"
}
```

**Response**: `CreateOrderResponse`
```json
{
  "order_id": "order_xxx",
  "amount": 350000,
  "currency": "INR",
  "key": "rzp_test_xxx"
}
```

**Example**:
```bash
curl -X POST \
  -H "Authorization: Bearer $JWT" \
  -H "X-Organization-ID: $ORG_ID" \
  -H "Content-Type: application/json" \
  -d '{"plan_id": "pro"}' \
  http://localhost:8000/api/v1/payments/create-order
```

**Usage Flow**:
1. Call this endpoint to create order
2. Use returned `order_id` and `key` to initialize Razorpay checkout
3. After payment, verify signature via `/payments/verify`

---

### POST /payments/verify

Verify payment signature after checkout completes.

**Authentication**: Required
**Organization Context**: Required
**Permissions**: Owner only

**Request**: `VerifyPaymentRequest`
```json
{
  "razorpay_order_id": "order_xxx",
  "razorpay_payment_id": "pay_xxx",
  "razorpay_signature": "xxx"
}
```

**Response**:
```json
{
  "status": "success",
  "payment_id": "uuid"
}
```

---

### POST /payments/webhooks/razorpay

Razorpay webhook handler (called by Razorpay, not by client).

**Authentication**: Webhook signature verification
**Organization Context**: Not required

**Headers**:
```
X-Razorpay-Signature: <signature>
```

**Events Handled**:
- `payment.captured` - Activates subscription, creates ledger entries
- `payment.failed` - Marks payment as failed

**Response**: `{"status": "ok"}`

---

### GET /payments/history

Get payment history for organization.

**Authentication**: Required
**Organization Context**: Required
**Permissions**: Any member

**Response**: `List[PaymentHistoryItem]`
```json
[
  {
    "id": "uuid",
    "amount": 3500.00,
    "currency": "INR",
    "status": "captured",
    "method": "card",
    "created_at": "2024-01-15T10:00:00",
    "captured_at": "2024-01-15T10:00:30"
  }
]
```

**Example**:
```bash
curl -H "Authorization: Bearer $JWT" \
  -H "X-Organization-ID: $ORG_ID" \
  http://localhost:8000/api/v1/payments/history
```

---

## Role-Based Access Control (RBAC)

### Role Hierarchy

```
VIEWER (1)   - Read-only access
  ↓
EDITOR (2)   - Create/edit projects and indicators
  ↓
ADMIN (3)    - Manage members, delete projects
  ↓
OWNER (4)    - Full control, billing, delete org
```

### Permission Matrix

| Action | Viewer | Editor | Admin | Owner |
|--------|--------|--------|-------|-------|
| View projects | ✅ | ✅ | ✅ | ✅ |
| View members | ✅ | ✅ | ✅ | ✅ |
| Create projects | ❌ | ✅ | ✅ | ✅ |
| Edit projects | ❌ | ✅ | ✅ | ✅ |
| Delete projects | ❌ | ❌ | ✅ | ✅ |
| Invite members | ❌ | ❌ | ✅ | ✅ |
| Change roles | ❌ | ❌ | ✅ | ✅ |
| Remove members | ❌ | ❌ | ✅ | ✅ |
| Manage billing | ❌ | ❌ | ❌ | ✅ |
| Delete organization | ❌ | ❌ | ❌ | ✅ |

---

## Error Responses

All errors follow a consistent format:

```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Organization slug already exists",
    "details": "...",
    "trace_id": "uuid"
  }
}
```

### Common Status Codes

- `400 Bad Request` - Invalid input data
- `401 Unauthorized` - Missing or invalid JWT token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource already exists
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Unexpected error
- `501 Not Implemented` - Feature not yet implemented

---

## Rate Limiting

Rate limits are applied per organization:

- **Free Plan**: 10,000 requests/month
- **Pro Plan**: 100,000 requests/month
- **Enterprise Plan**: Unlimited

Rate limit headers:
```
X-RateLimit-Limit: 10000
X-RateLimit-Remaining: 9850
X-RateLimit-Reset: 1705843200
```

When rate limit is exceeded: `429 Too Many Requests`

---

## API Versioning

Current version: `v1`

- Breaking changes will result in new version (v2)
- Old versions supported for 6 months after deprecation
- Version specified in URL: `/api/v1/...`

---

## Testing the API

### Local Development

1. Start the server:
```bash
uvicorn app.main:app --reload
```

2. Access interactive docs:
```
http://localhost:8000/docs
```

3. Try a request:
```bash
# Health check (no auth)
curl http://localhost:8000/health

# Get current user (requires JWT)
curl -H "Authorization: Bearer $JWT" \
  http://localhost:8000/api/v1/users/me
```

### Using the API Docs

Visit `/docs` in your browser to:
- View all endpoints with schemas
- Try requests interactively
- See example responses
- Download OpenAPI spec

---

## Next Steps

### Implemented ✅
- User profile management
- Organization CRUD
- Member management with RBAC
- Project management (structure ready)
- Payment integration

### TODO 🚧
- Project domain models (ThreatActor, Indicator, Campaign)
- API key management endpoints
- Rate limiting middleware
- Audit logging
- Webhook management
- File uploads (STIX, IOCs)

---

## References

- [Authentication Documentation](./AUTH_PAYMENTS_IMPLEMENTATION.md)
- [Database Schema](./database/schema-production.sql)
- [API Design Principles](./docs/01-architecture.md)
- [Security Best Practices](./docs/04-security.md)

---

**Last Updated**: 2025-01-20
**API Version**: v1.0.0
**OpenAPI Spec**: Available at `/docs` (development only)
