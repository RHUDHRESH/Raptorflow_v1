# 🔒 Security Hardening Checklist

Comprehensive security configuration guide for RaptorFlow 2.0 production deployment.

---

## 📋 Overview

Security hardening covers:
- Application-level security
- Infrastructure security
- Authentication & Authorization
- Data protection
- API security
- Monitoring & incident response
- Compliance & auditing

---

## 🛡️ Application Security

### 1. Dependency Vulnerability Scanning

```bash
# 1a. Audit dependencies for vulnerabilities
npm audit

# Expected: 0 vulnerabilities
# If vulnerabilities found:
# Option 1: Update vulnerable package
npm update [package-name]

# Option 2: Audit fix
npm audit fix

# Option 3: Force audit fix (breaking changes possible)
npm audit fix --force

# 1b. Lock dependency versions
# Verify package-lock.json is committed
git add package-lock.json
git commit -m "Lock dependency versions"

# 1c. Set up dependabot
# GitHub Settings > Security & Analysis > Enable Dependabot
# This will auto-create PRs for security updates
```

### 2. Environment Variable Security

```bash
# 2a. Never commit secrets
cat >> .gitignore << 'EOF'
.env
.env.local
.env.production.local
.env.*.local
.env*.local
EOF

# 2b. Use environment variables for secrets
# Create separate files for each environment:
# - .env.development (with dummy values)
# - .env.staging (with AWS Secrets Manager references)
# - .env.production (with AWS Secrets Manager references)

# 2c. Store secrets in AWS Secrets Manager
# DO NOT store in environment variables!

# Example:
aws secretsmanager create-secret \
  --name raptorflow/prod/database-url \
  --secret-string "postgresql://user:pass@host/db" \
  --kms-key-id alias/aws/secretsmanager

# 2d. Retrieve secrets in application
# In production server initialization:
import { SecretsManager } from '@aws-sdk/client-secrets-manager';

const client = new SecretsManager();
const secret = await client.getSecretValue({
  SecretId: 'raptorflow/prod/database-url'
});
const DATABASE_URL = secret.SecretString;
```

### 3. TypeScript Strict Mode

```typescript
// tsconfig.json - Enable strict mode
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "strictBindCallApply": true,
    "strictFunctionTypes": true,
    "strictNullChecks": true,
    "strictPropertyInitialization": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  }
}
```

### 4. Content Security Policy (CSP)

```javascript
// next.config.js
module.exports = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self' https://api.raptorflow.com https://*.sentry.io"
          }
        ]
      }
    ];
  }
};

// Note: 'unsafe-inline' needed for styled-components
// Consider using nonce-based CSP in future:
// Generate random nonce for each request
// script-src 'nonce-[RANDOM_NONCE]'
```

### 5. CORS Configuration

```javascript
// pages/api/middleware/cors.ts
import { NextRequest, NextResponse } from 'next/server';

export function corsMiddleware(request: NextRequest) {
  const origin = request.headers.get('origin');

  // Allowed origins
  const allowedOrigins = [
    'https://raptorflow.com',
    'https://www.raptorflow.com',
    'https://app.raptorflow.com'
  ];

  if (allowedOrigins.includes(origin || '')) {
    // Add CORS headers
    const response = NextResponse.next();
    response.headers.set('Access-Control-Allow-Origin', origin || '');
    response.headers.set(
      'Access-Control-Allow-Methods',
      'GET, POST, PUT, DELETE, PATCH'
    );
    response.headers.set(
      'Access-Control-Allow-Headers',
      'Content-Type, Authorization'
    );
    response.headers.set(
      'Access-Control-Allow-Credentials',
      'true'
    );
    response.headers.set('Access-Control-Max-Age', '86400');
    return response;
  }

  // Reject request from unknown origin
  return new NextResponse(null, { status: 403 });
}
```

### 6. Input Validation & Sanitization

```typescript
// lib/validation.ts
import DOMPurify from 'isomorphic-dompurify';
import { z } from 'zod';

// Schema validation with zod
export const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password too short').max(128),
});

// HTML sanitization
export function sanitizeHTML(html: string): string {
  return DOMPurify.sanitize(html);
}

// SQL injection prevention (use parameterized queries)
// ❌ WRONG:
// const result = db.query(`SELECT * FROM users WHERE email = '${email}'`);

// ✅ CORRECT:
import { sql } from '@vercel/postgres';
const result = await sql`
  SELECT * FROM users WHERE email = ${email}
`;

// XSS prevention (use React's built-in escaping)
// ❌ WRONG:
// <div dangerouslySetInnerHTML={{ __html: userContent }} />

// ✅ CORRECT:
// <div>{userContent}</div>  // Automatically escaped
```

### 7. API Rate Limiting

```typescript
// lib/rate-limit.ts
import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
});

export const rateLimit = new Ratelimit({
  redis: redis,
  limiter: Ratelimit.slidingWindow(100, '1 h'), // 100 requests per hour
});

// Use in API routes
// pages/api/analysis.ts
import { rateLimit } from '@/lib/rate-limit';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const { success } = await rateLimit.limit(req.ip || 'anonymous');

    if (!success) {
      return res.status(429).json({ error: 'Too many requests' });
    }

    // Process request...
  } catch (error) {
    return res.status(500).json({ error: 'Internal server error' });
  }
}
```

### 8. HTTPS & TLS Configuration

```bash
# 8a. Enforce HTTPS everywhere
# In next.config.js
module.exports = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=31536000; includeSubDomains; preload'
          }
        ]
      }
    ];
  },
  async redirects() {
    return [
      {
        source: '/:path*',
        destination: 'https://raptorflow.com/:path*',
        permanent: true,
      },
    ];
  }
};

# 8b. Configure TLS in AWS
# For ALB/CloudFront:
# - Use TLS 1.2 minimum
# - Use strong cipher suites
# - Disable old protocols (SSLv3, TLS 1.0, 1.1)

aws elbv2 modify-listener \
  --listener-arn arn:aws:elasticloadbalancing:... \
  --ssl-policy ELBSecurityPolicy-TLS-1-2-2017-01

# 8c. Verify SSL certificate
curl -I https://raptorflow.com | grep -i "ssl\|tls"
```

---

## 🔐 Authentication & Authorization

### 1. Authentication Implementation

```typescript
// lib/auth.ts
import { jwtVerify } from 'jose';
import { cookies } from 'next/headers';

const secret = new TextEncoder().encode(process.env.JWT_SECRET!);

export async function verifyAuth(token: string) {
  try {
    const verified = await jwtVerify(token, secret);
    return verified.payload as AuthPayload;
  } catch (error) {
    throw new Error('Invalid token');
  }
}

export async function getSession() {
  const cookieStore = cookies();
  const token = cookieStore.get('session')?.value;

  if (!token) {
    return null;
  }

  return verifyAuth(token);
}

// Middleware to protect routes
import { NextRequest, NextResponse } from 'next/server';

export async function authMiddleware(request: NextRequest) {
  const session = await getSession();

  if (!session && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}
```

### 2. OAuth2 Implementation

```typescript
// pages/api/auth/callback/[provider].ts
import { getProviders, signIn } from 'next-auth/react';
import GoogleProvider from 'next-auth/providers/google';
import { PrismaAdapter } from '@next-auth/prisma-adapter';
import prisma from '@/lib/prisma';

export const authOptions = {
  adapter: PrismaAdapter(prisma),
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      allowDangerousEmailAccountLinking: false,
    }),
  ],
  callbacks: {
    // Verify JWT token
    async jwt({ token, account }) {
      if (account) {
        token.accessToken = account.access_token;
      }
      return token;
    },
    // Add data to session
    async session({ session, token }) {
      session.accessToken = token.accessToken;
      return session;
    },
  },
  pages: {
    signIn: '/auth/signin',
    error: '/auth/error',
  },
};
```

### 3. Password Security

```typescript
// lib/password.ts
import bcrypt from 'bcrypt';

const SALT_ROUNDS = 12;

export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, SALT_ROUNDS);
}

export async function verifyPassword(
  password: string,
  hash: string
): Promise<boolean> {
  return bcrypt.compare(password, hash);
}

// Usage in registration
// pages/api/auth/register.ts
export async function register(email: string, password: string) {
  // 1. Validate password strength
  if (password.length < 12) {
    throw new Error('Password too weak');
  }

  // 2. Check if user exists
  const existing = await prisma.user.findUnique({ where: { email } });
  if (existing) {
    throw new Error('User already exists');
  }

  // 3. Hash password
  const hashedPassword = await hashPassword(password);

  // 4. Create user
  const user = await prisma.user.create({
    data: {
      email,
      password: hashedPassword,
    },
  });

  return user;
}
```

### 4. Session Security

```typescript
// Session configuration
// pages/api/auth/[...nextauth].ts

export const authOptions = {
  session: {
    strategy: 'jwt', // Use JWT instead of database sessions
    maxAge: 24 * 60 * 60, // 24 hours
    updateAge: 24 * 60 * 60, // Refresh every 24 hours
  },
  jwt: {
    secret: process.env.JWT_SECRET!,
    maxAge: 24 * 60 * 60,
  },
  // Secure cookie settings
  cookies: {
    sessionToken: {
      name: 'next-auth.session-token',
      options: {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 24 * 60 * 60,
        path: '/',
      },
    },
  },
};
```

### 5. Authorization Checks

```typescript
// middleware/requireAuth.ts
import { NextRequest, NextResponse } from 'next/server';
import { getSession } from '@/lib/auth';

export async function requireAuth(request: NextRequest) {
  const session = await getSession();

  if (!session) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // Check user role
  if (request.nextUrl.pathname.startsWith('/admin')) {
    if (session.user.role !== 'ADMIN') {
      return NextResponse.redirect(new URL('/unauthorized', request.url));
    }
  }

  return NextResponse.next();
}

// Usage in protected routes
// pages/api/admin/users.ts
import { requireAuth } from '@/middleware/requireAuth';

export default async function handler(req, res) {
  const session = await requireAuth(req);
  if (!session) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  // Admin endpoint
}
```

---

## 🗄️ Data Protection

### 1. Database Encryption

```bash
# 1a. Enable encryption at rest
aws rds modify-db-instance \
  --db-instance-identifier raptorflow-prod \
  --storage-encrypted \
  --kms-key-id arn:aws:kms:us-east-1:ACCOUNT:key/KEY_ID \
  --apply-immediately

# 1b. Enable encryption in transit
# Connection string format:
# postgresql://user:pass@host:5432/db?sslmode=require

# 1c. Verify encryption
aws rds describe-db-instances \
  --db-instance-identifier raptorflow-prod \
  --query 'DBInstances[0].StorageEncrypted'

# Expected output: true
```

### 2. Sensitive Data Redaction

```typescript
// lib/redact.ts
export function redactEmail(email: string): string {
  const [name, domain] = email.split('@');
  const redacted = name.substring(0, 2) + '*'.repeat(name.length - 2);
  return `${redacted}@${domain}`;
}

export function redactCreditCard(card: string): string {
  return card.replace(/\d(?=\d{4})/g, '*');
}

export function redactSSN(ssn: string): string {
  return '***-**-' + ssn.slice(-4);
}

// Usage in logging
logger.info('User login', {
  email: redactEmail(user.email),
  timestamp: new Date(),
});
```

### 3. Data Retention Policies

```typescript
// lib/retention.ts
export const RETENTION_POLICIES = {
  // Keep logs for 30 days
  LOGS: 30 * 24 * 60 * 60 * 1000,

  // Keep user activity for 90 days
  ACTIVITY: 90 * 24 * 60 * 60 * 1000,

  // Keep deleted user data for 30 days (for recovery)
  DELETED_USER: 30 * 24 * 60 * 60 * 1000,

  // Keep backups for 90 days
  BACKUPS: 90 * 24 * 60 * 60 * 1000,
};

// Scheduled job to delete expired data
// jobs/retention.ts
export async function cleanupExpiredData() {
  const thirtyDaysAgo = new Date(Date.now() - RETENTION_POLICIES.LOGS);

  await prisma.log.deleteMany({
    where: {
      createdAt: { lt: thirtyDaysAgo }
    }
  });
}

// Schedule with: node-cron or AWS Lambda
```

### 4. Data Privacy (GDPR)

```typescript
// GDPR compliance functions

export async function exportUserData(userId: string) {
  // Get all user data
  const user = await prisma.user.findUnique({
    where: { id: userId },
    include: {
      workspaces: true,
      strategies: true,
      analyses: true,
      logs: true,
    }
  });

  // Export to JSON
  return JSON.stringify(user, null, 2);
}

export async function deleteUserData(userId: string) {
  // Anonymous user data
  await prisma.user.update({
    where: { id: userId },
    data: {
      email: `deleted-${userId}@example.com`,
      name: 'Deleted User',
      // Don't delete, just anonymize
    }
  });

  // Delete related data
  await prisma.workspace.deleteMany({
    where: { userId }
  });
}

// Endpoint for GDPR requests
// pages/api/privacy/export.ts
export default async function handler(req, res) {
  const session = await getSession();
  if (!session) return res.status(401).json({ error: 'Unauthorized' });

  const data = await exportUserData(session.user.id);

  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Content-Disposition', 'attachment; filename="user-data.json"');
  res.send(data);
}
```

---

## 🚨 Security Monitoring

### 1. Error Tracking (Sentry)

```typescript
// pages/_app.tsx
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NEXT_PUBLIC_ENVIRONMENT,
  tracesSampleRate: 1.0,
  beforeSend(event, hint) {
    // Filter sensitive data
    if (event.request) {
      delete event.request.headers?.authorization;
      delete event.request.cookies;
    }
    return event;
  },
});

// Usage
try {
  // Code
} catch (error) {
  Sentry.captureException(error, {
    tags: {
      'security': 'auth-failure',
    },
  });
}
```

### 2. Security Logging

```typescript
// lib/security-logger.ts
export class SecurityLogger {
  static logAuthAttempt(email: string, success: boolean, ip: string) {
    console.log({
      event: 'auth_attempt',
      email: redactEmail(email),
      success,
      ip,
      timestamp: new Date(),
    });
  }

  static logUnauthorizedAccess(userId: string, resource: string, ip: string) {
    console.log({
      event: 'unauthorized_access',
      userId,
      resource,
      ip,
      timestamp: new Date(),
    });
  }

  static logDataAccess(userId: string, dataType: string, action: string) {
    console.log({
      event: 'data_access',
      userId,
      dataType,
      action,
      timestamp: new Date(),
    });
  }
}
```

### 3. Intrusion Detection

```typescript
// lib/intrusion-detection.ts
import { rateLimit } from './rate-limit';

export class IntrusionDetection {
  // Track failed login attempts
  static async trackFailedLogin(email: string, ip: string) {
    // Store in Redis with expiry
    const key = `failed_login:${email}:${ip}`;
    const count = await redis.incr(key);
    await redis.expire(key, 15 * 60); // 15 minute window

    if (count > 5) {
      // Lock account
      await lockAccount(email);
      SecurityLogger.logSecurityEvent('account_locked_suspicious_activity', {
        email: redactEmail(email),
        ip,
        attempts: count,
      });
    }
  }

  // Detect suspicious patterns
  static async detectSuspiciousActivity(userId: string, action: string) {
    // Check if unusual for this user
    const userHistory = await getRecentActivity(userId, action);

    if (isUnusualPattern(userHistory)) {
      // Require re-authentication
      return {
        requiresReauth: true,
        reason: 'Unusual activity detected',
      };
    }
  }
}
```

---

## ✅ Security Checklist

### Before Production Deployment

```
DEPENDENCY SECURITY
☐ npm audit shows 0 vulnerabilities
☐ All critical/high vulnerabilities patched
☐ package-lock.json committed
☐ Dependabot enabled

ENVIRONMENT & SECRETS
☐ No secrets in .env files
☐ .env files in .gitignore
☐ All secrets in AWS Secrets Manager
☐ Secrets Manager policies configured
☐ KMS encryption enabled for secrets

APPLICATION SECURITY
☐ TypeScript strict mode enabled
☐ Content Security Policy configured
☐ CORS properly configured
☐ Input validation on all endpoints
☐ CSRF protection enabled
☐ Rate limiting configured

AUTHENTICATION
☐ OAuth2 properly configured
☐ Password hashing (bcrypt) implemented
☐ Session security configured
☐ JWT token validation working
☐ Authorization checks in place

DATA PROTECTION
☐ Database encryption enabled
☐ Encryption in transit (HTTPS/TLS)
☐ Sensitive data redaction in logs
☐ Data retention policies set
☐ GDPR compliance implemented

MONITORING
☐ Sentry error tracking enabled
☐ Security logging configured
☐ Intrusion detection enabled
☐ CloudWatch alerts configured
☐ Access logs enabled

INFRASTRUCTURE
☐ Security groups configured
☐ Database backups encrypted
☐ Backup retention policy set
☐ VPC security configured
☐ SSL certificate installed

TESTING
☐ Security tests written
☐ Penetration testing completed
☐ Vulnerability scanning scheduled
☐ Load testing shows no security issues
```

---

## 🔗 Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [AWS Security Best Practices](https://aws.amazon.com/architecture/security-identity-compliance/)

---

**Last Updated:** Phase 5 Week 3
**Version:** 1.0
**Compliance:** OWASP, AWS Security Best Practices
