# Security Architecture

**Comprehensive security controls, threat model, and compliance measures**

## Security Principles

### Defense in Depth
Multiple layers of security controls to protect against breaches:
- Network security (TLS, VPC, firewall)
- Application security (input validation, CSRF, XSS)
- Data security (encryption at rest/transit, field-level encryption)
- Identity security (JWT, MFA, RBAC)
- Operational security (logging, monitoring, incident response)

### Least Privilege
Every component has minimal necessary permissions:
- Service accounts with scoped IAM roles
- Database users with specific grants
- API keys with resource-level scoping
- User roles with explicit permission matrices

### Security by Default
Secure configurations out of the box:
- HTTPS enforced, no HTTP fallback
- Strict CSP headers
- Rate limiting enabled
- Secrets never in code
- Audit logging for sensitive operations

## Threat Model

### Assets

| Asset | Classification | Protection |
|-------|----------------|------------|
| User credentials | Critical | Hashed (Supabase), never stored |
| Payment data | Critical | Tokenized (Razorpay), PCI-DSS delegated |
| Threat intelligence | High | Org-scoped, encrypted at rest |
| API keys | High | Hashed (bcrypt), scoped |
| Session tokens | High | Short-lived JWTs, httpOnly cookies |
| User PII | Medium | Field-level encryption, GDPR compliant |
| Logs | Low | Sanitized (no secrets), retained 90 days |

### Threat Actors

1. **External Attackers**
   - Motivation: Data theft, ransom, disruption
   - Vectors: SQL injection, XSS, credential stuffing
   - Mitigation: WAF, input validation, rate limiting

2. **Malicious Insiders**
   - Motivation: Data exfiltration, sabotage
   - Vectors: Privilege escalation, data dumps
   - Mitigation: RBAC, audit logs, access reviews

3. **Supply Chain Attacks**
   - Motivation: Compromise dependencies
   - Vectors: Malicious npm/pip packages
   - Mitigation: Dependency scanning, SRI, lockfiles

### Attack Vectors

| Vector | Likelihood | Impact | Mitigation |
|--------|------------|--------|------------|
| SQL Injection | Low | High | Parameterized queries, ORM |
| XSS | Low | Medium | CSP, sanitization, React auto-escaping |
| CSRF | Low | Medium | SameSite cookies, CSRF tokens |
| Auth bypass | Low | Critical | JWT validation, JWKS rotation |
| Rate abuse | Medium | Medium | Token bucket rate limiting |
| Data leak | Low | High | Org scoping, audit logs |
| DDoS | Medium | Medium | Cloud Load Balancer, rate limits |
| Credential stuffing | Medium | High | Rate limiting, MFA (future) |

## Transport Security

### TLS Configuration

**Minimum Version**: TLS 1.2
**Preferred Version**: TLS 1.3
**Cipher Suites**: Modern only (no CBC, no RC4)

```nginx
# Cloud Load Balancer configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
ssl_prefer_server_ciphers off;
```

### HSTS

**Header**: `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`

- **max-age**: 1 year (31536000 seconds)
- **includeSubDomains**: Apply to all subdomains
- **preload**: Submit to HSTS preload list

### Certificate Management

- **Provider**: Let's Encrypt (via Google Cloud)
- **Auto-renewal**: 30 days before expiry
- **Monitoring**: Alert if expiry < 14 days

## Application Security

### Security Headers

**Content Security Policy (CSP)**:
```
default-src 'self';
script-src 'self' 'unsafe-inline' 'unsafe-eval' https://checkout.razorpay.com;
connect-src 'self' https://api.razorpay.com https://*.supabase.co;
img-src 'self' data: https:;
style-src 'self' 'unsafe-inline';
font-src 'self' data:;
frame-src 'self' https://api.razorpay.com;
frame-ancestors 'none';
base-uri 'self';
form-action 'self';
```

**Other Headers**:
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: no-referrer
Permissions-Policy: geolocation=(), camera=(), microphone=(), payment=(self)
X-XSS-Protection: 1; mode=block  # Legacy browsers
```

### Input Validation

**Backend (Pydantic)**:
```python
from pydantic import BaseModel, EmailStr, Field, validator

class UserCreate(BaseModel):
    email: EmailStr
    display_name: str = Field(min_length=1, max_length=100)

    @validator('display_name')
    def sanitize_name(cls, v):
        # Strip HTML tags
        return bleach.clean(v, tags=[], strip=True)
```

**Frontend (Zod)**:
```typescript
import { z } from 'zod';

const userSchema = z.object({
  email: z.string().email(),
  displayName: z.string().min(1).max(100),
});
```

### Output Encoding

**React Auto-Escaping**: Enabled by default
**Manual Escaping**: Use `DOMPurify` for user-generated HTML
**API Responses**: JSON (auto-escaped by FastAPI)

### SQL Injection Prevention

**ORM-Only**: All queries via SQLAlchemy ORM
**Parameterized Queries**: For rare raw SQL

```python
# ✅ GOOD: ORM
users = db.query(User).filter(User.email == email).all()

# ✅ GOOD: Parameterized
result = db.execute(text("SELECT * FROM users WHERE email = :email"), {"email": email})

# ❌ BAD: String interpolation (never do this!)
# result = db.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

### CSRF Protection

**API**: Not applicable (JWT in Authorization header, not cookies)
**Web Forms**: SameSite cookies + CSRF token for sensitive operations

```python
# FastAPI CSRF middleware
app.add_middleware(
    CSRFMiddleware,
    exempt_urls=["/api/v1/webhooks/*"],  # Webhooks use signature verification
)
```

## Authentication & Authorization

### JWT Validation

**Flow**:
1. User signs in via Supabase Auth
2. Supabase returns JWT (access_token)
3. Frontend sends: `Authorization: Bearer {token}`
4. API validates JWT signature against Supabase JWKS
5. API extracts claims: `sub`, `email`, `exp`
6. API loads user profile + memberships

**Implementation**:
```python
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
import httpx

SUPABASE_JWT_SECRET = get_secret("SUPABASE_JWT_SECRET")
JWKS_URL = f"{SUPABASE_URL}/.well-known/jwks.json"

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # Verify JWT
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(401, "Invalid token")

        # Load user
        user = await db.query(User).filter(User.auth_sub == sub).first()
        if not user:
            # First-time user, create profile
            user = await create_user_from_jwt(payload)

        return user
    except JWTError:
        raise HTTPException(401, "Invalid token")
```

### Role-Based Access Control (RBAC)

**Roles** (hierarchy: Owner > Admin > Editor > Viewer):
```python
from enum import IntEnum

class Role(IntEnum):
    VIEWER = 1
    EDITOR = 2
    ADMIN = 3
    OWNER = 4
```

**Permission Check**:
```python
async def require_role(min_role: Role):
    async def check(principal: Principal = Depends(get_principal)):
        if principal.role < min_role:
            raise HTTPException(403, f"Requires {min_role.name} role")
        return principal
    return check

@router.delete("/projects/{project_id}", dependencies=[Depends(require_role(Role.ADMIN))])
async def delete_project(project_id: UUID, principal: Principal):
    # principal.org_id is automatically available
    project = await get_project_in_org(project_id, principal.org_id)
    await db.delete(project)
```

### Multi-Tenancy Enforcement

**Organization Scoping** (automatic):
```python
async def get_principal(user: User = Depends(get_current_user), org_id: UUID = Header(...)):
    membership = await db.query(Membership).filter(
        Membership.user_id == user.id,
        Membership.org_id == org_id,
    ).first()

    if not membership:
        raise HTTPException(403, "Not a member of this organization")

    return Principal(
        user=user,
        org_id=org_id,
        role=membership.role,
    )

# Every query automatically includes org_id filter
projects = db.query(Project).filter(Project.org_id == principal.org_id).all()
```

### API Key Authentication

**Generation**:
```python
import secrets
import hashlib

def create_api_key(org_id: UUID, name: str, scopes: list[str]):
    # Generate random key
    raw_key = f"rk_{secrets.token_urlsafe(32)}"

    # Hash for storage
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    # Store in DB
    api_key = APIKey(
        org_id=org_id,
        name=name,
        key_hash=key_hash,
        scopes=scopes,
        created_at=datetime.utcnow(),
    )
    db.add(api_key)

    # Return raw key ONCE (never show again)
    return raw_key
```

**Validation**:
```python
async def validate_api_key(api_key: str = Header(alias="X-API-Key")):
    if not api_key.startswith("rk_"):
        raise HTTPException(401, "Invalid API key format")

    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    db_key = await db.query(APIKey).filter(APIKey.key_hash == key_hash).first()

    if not db_key or db_key.revoked:
        raise HTTPException(401, "Invalid or revoked API key")

    # Update last_used_at
    db_key.last_used_at = datetime.utcnow()

    return db_key
```

## Data Protection

### Encryption at Rest

**Database**: Google Cloud SQL automatic encryption
**Object Storage**: Google Cloud Storage automatic encryption
**Secrets**: Secret Manager with Google-managed keys

**Field-Level Encryption** (for extra-sensitive data):
```python
from cryptography.fernet import Fernet

ENCRYPTION_KEY = get_secret("FIELD_ENCRYPTION_KEY")  # 32-byte key
cipher = Fernet(ENCRYPTION_KEY)

class User(Base):
    __tablename__ = "users"

    ssn_encrypted = Column(LargeBinary)  # Store encrypted

    @property
    def ssn(self):
        if self.ssn_encrypted:
            return cipher.decrypt(self.ssn_encrypted).decode()
        return None

    @ssn.setter
    def ssn(self, value):
        if value:
            self.ssn_encrypted = cipher.encrypt(value.encode())
```

### Encryption in Transit

- **External**: HTTPS with TLS 1.3
- **Internal** (service-to-service): TLS via Cloud Run internal traffic
- **Database**: SSL/TLS connection required

```python
DATABASE_URL = "postgresql://user:pass@host/db?sslmode=require"
```

### Data Sanitization

**Logs** (never log secrets):
```python
import structlog

# Configure structlog to redact sensitive fields
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        SanitizingProcessor(fields=["password", "api_key", "token"]),
        structlog.processors.JSONRenderer(),
    ]
)
```

**Database Exports** (mask PII):
```python
def export_users(org_id: UUID):
    users = db.query(User).filter(User.org_id == org_id).all()
    return [
        {
            "id": u.id,
            "email": mask_email(u.email),  # user@example.com → u***@example.com
            "created_at": u.created_at,
        }
        for u in users
    ]
```

## Rate Limiting

### Token Bucket Algorithm

**Per IP**:
- 100 requests per 15 minutes
- Burst: 20 requests

**Per User**:
- 1000 requests per hour
- Burst: 50 requests

**Per Organization** (based on plan):
- Free: 10,000 requests/month
- Pro: 100,000 requests/month
- Enterprise: Unlimited

**Implementation**:
```python
import aioredis
from fastapi import HTTPException

async def check_rate_limit(key: str, limit: int, window: int):
    """
    Token bucket rate limiting with Redis.

    Args:
        key: Rate limit key (e.g., "ip:1.2.3.4" or "user:uuid")
        limit: Max requests in window
        window: Time window in seconds
    """
    redis = await aioredis.from_url("redis://localhost")

    current = await redis.incr(key)
    if current == 1:
        await redis.expire(key, window)

    if current > limit:
        ttl = await redis.ttl(key)
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time()) + ttl),
                "Retry-After": str(ttl),
            },
        )

    return {
        "X-RateLimit-Limit": str(limit),
        "X-RateLimit-Remaining": str(limit - current),
        "X-RateLimit-Reset": str(int(time.time()) + window),
    }
```

### Cost-Based Rate Limiting (LLM Tokens)

**Per Organization**:
- Free: 10,000 tokens/month
- Pro: 500,000 tokens/month
- Enterprise: Custom

**Implementation**:
```python
async def check_token_budget(org_id: UUID, tokens_needed: int):
    subscription = await get_subscription(org_id)
    usage = await get_token_usage_this_month(org_id)

    if usage + tokens_needed > subscription.plan.token_limit:
        raise HTTPException(402, "Token budget exceeded. Please upgrade.")

    # Reserve tokens
    await reserve_tokens(org_id, tokens_needed)
```

## Webhook Security

### Signature Verification (Razorpay)

```python
import hmac
import hashlib

def verify_razorpay_signature(body: bytes, signature: str):
    expected = hmac.new(
        RAZORPAY_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        raise HTTPException(401, "Invalid webhook signature")
```

### Replay Protection

```python
async def check_webhook_replay(event_id: str):
    key = f"webhook:{event_id}"
    redis = await get_redis()

    if await redis.exists(key):
        raise HTTPException(409, "Webhook already processed (replay)")

    # Mark as processed for 1 hour
    await redis.setex(key, 3600, "1")
```

### Idempotency

```python
@router.post("/webhooks/razorpay")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(...),
):
    body = await request.body()
    verify_razorpay_signature(body, x_razorpay_signature)

    event = json.loads(body)
    event_id = event['payload']['payment']['entity']['id']

    # Idempotency check
    await check_webhook_replay(event_id)

    # Process payment
    await process_payment_capture(event)

    return {"status": "ok"}
```

## Secrets Management

### Cloud Secret Manager

**Storage**:
```bash
# Store secret
echo -n "my-secret-value" | gcloud secrets create SECRET_NAME --data-file=-

# Grant access to service account
gcloud secrets add-iam-policy-binding SECRET_NAME \
  --member="serviceAccount:app@project.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

**Retrieval** (at runtime):
```python
from google.cloud import secretmanager

def get_secret(secret_id: str, version: str = "latest") -> str:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/{version}"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode('UTF-8')

# Use in app
OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
```

### Local Development

**Never commit secrets!**

```bash
# .env (gitignored)
DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-...

# .env.example (committed)
DATABASE_URL=postgresql://user:pass@localhost/db
OPENAI_API_KEY=sk-your-key-here
```

### Secret Rotation

**Quarterly Rotation**:
1. Generate new secret
2. Add as new version in Secret Manager
3. Deploy with new version
4. Wait 24 hours (grace period)
5. Revoke old version

## Audit Logging

### What to Log

**Authentication Events**:
- Login success/failure
- Logout
- Password reset
- MFA enrollment

**Authorization Events**:
- Permission denied (403)
- Role changes
- Org membership changes

**Data Access** (high-value only):
- Payment data access
- Bulk exports
- API key generation

**Administrative Actions**:
- User creation/deletion
- Org creation/deletion
- Plan changes
- Subscription changes

### Audit Log Schema

```sql
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    org_id UUID NOT NULL,
    user_id UUID,
    action TEXT NOT NULL,
    resource TEXT,
    resource_id TEXT,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_org_id ON audit_logs(org_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
```

### Implementation

```python
async def log_audit_event(
    org_id: UUID,
    user_id: UUID,
    action: str,
    resource: str = None,
    resource_id: str = None,
    details: dict = None,
    request: Request = None,
):
    audit_log = AuditLog(
        org_id=org_id,
        user_id=user_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        details=details,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None,
    )
    db.add(audit_log)
    await db.commit()

# Usage
await log_audit_event(
    org_id=principal.org_id,
    user_id=principal.user.id,
    action="payment.captured",
    resource="payment",
    resource_id=str(payment.id),
    details={"amount": payment.amount, "currency": payment.currency},
)
```

## Compliance

### GDPR

**Right to Access**:
```python
@router.get("/users/me/data-export")
async def export_user_data(principal: Principal):
    # Export all user data in machine-readable format
    return {
        "profile": await export_profile(principal.user.id),
        "projects": await export_projects(principal.user.id),
        "payments": await export_payments(principal.user.id),
    }
```

**Right to Erasure** ("Right to be Forgotten"):
```python
@router.delete("/users/me")
async def delete_user_account(principal: Principal):
    # Anonymize audit logs
    await anonymize_audit_logs(principal.user.id)

    # Delete user data
    await delete_user_projects(principal.user.id)
    await delete_user_memberships(principal.user.id)
    await delete_user_profile(principal.user.id)

    return {"status": "deleted"}
```

**Data Processing Agreement**: See [PRIVACY_POLICY.md](../PRIVACY_POLICY.md)

### PCI-DSS

**Scope Reduction**: All payment card data handled by Razorpay (PCI-DSS Level 1)

**Our Responsibilities**:
- ✅ Use HTTPS for Razorpay communication
- ✅ Never log card numbers
- ✅ Tokenize payments (Razorpay provides tokens)
- ✅ Secure webhooks with signature verification

## Security Monitoring

### Real-Time Alerts

**Critical** (Page immediately):
- Authentication bypass detected
- Unusual payment activity (>$10k in 1 hour)
- Database down
- 50x errors spike (>10% for 5 min)

**High** (Slack notification):
- Rate limit exceeded (>100 IPs in 1 hour)
- Failed login spike (>100 in 10 min)
- API key leaked (detected in public GitHub)
- Webhook signature failures

**Medium** (Daily digest):
- Dependency vulnerabilities found
- SSL certificate expiry <30 days
- Unusual token spend pattern

### Security Dashboards

**Metrics**:
- Failed login attempts (by IP, by user)
- 403 Forbidden rate (authorization failures)
- Rate limit violations
- Webhook failures
- API key usage by org

## Incident Response

### Incident Severity

| Level | Examples | Response Time |
|-------|----------|---------------|
| **P0 - Critical** | Data breach, auth bypass | 15 minutes |
| **P1 - High** | Payment processing down, DDoS | 1 hour |
| **P2 - Medium** | Non-critical feature broken | 4 hours |
| **P3 - Low** | Minor bug, performance degradation | 24 hours |

### Response Procedure

1. **Detect**: Alert fires → On-call engineer notified
2. **Assess**: Determine severity and scope
3. **Contain**: Isolate affected systems, revoke compromised credentials
4. **Investigate**: Collect logs, identify root cause
5. **Remediate**: Apply fix, verify resolution
6. **Communicate**: Update status page, notify affected users
7. **Post-Mortem**: Document incident, create action items

### Breach Notification

**Timeline**:
- **0-24 hours**: Internal notification, containment
- **24-72 hours**: User notification (if PII affected)
- **72 hours**: GDPR notification to supervisory authority (if EU users affected)

**Template**: See [SECURITY.md](../SECURITY.md#breach-notification)

## Security Checklist

### Pre-Deployment

- [ ] All secrets in Secret Manager (not in code)
- [ ] HTTPS enforced everywhere
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (ORM only)
- [ ] XSS prevention (auto-escaping)
- [ ] CSRF tokens for state-changing operations
- [ ] Audit logging for sensitive actions
- [ ] Error messages don't leak sensitive info

### Quarterly Review

- [ ] Rotate all secrets
- [ ] Review IAM permissions (remove unused)
- [ ] Update dependencies (npm audit, pip-audit)
- [ ] Review audit logs for anomalies
- [ ] Test backup restoration
- [ ] Review security alerts
- [ ] Penetration test (external)

### Annual Review

- [ ] Full security audit (external firm)
- [ ] GDPR compliance review
- [ ] Update privacy policy
- [ ] Review incident response plan
- [ ] Disaster recovery drill

---

**See Also**:
- [SECURITY.md](../SECURITY.md) - Security policy & reporting
- [05-accounts-billing.md](./05-accounts-billing.md) - RBAC details
- [09-runbook.md](./09-runbook.md) - Incident procedures
