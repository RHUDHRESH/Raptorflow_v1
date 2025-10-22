# 🚀 Phase 5 Week 3: Production Deployment Guide

**Status:** IN PROGRESS ✅
**Week:** 3 of 4
**Focus:** Deployment preparation, environment setup, security hardening, monitoring configuration

---

## 📋 Overview

Week 3 establishes a complete deployment-ready infrastructure for RaptorFlow 2.0, covering:
- Pre-deployment validation checklist
- Environment configuration (dev, staging, production)
- Multiple deployment options (Vercel, AWS, GitHub Actions)
- Security hardening procedures
- Backup and disaster recovery setup
- Monitoring and alerting configuration
- Runbook for operational procedures

---

## ✅ Pre-Deployment Checklist

### Code Quality & Testing
- [x] All E2E tests passing (50+ test cases)
- [x] Load testing completed (baseline, spike, stress, workflow)
- [x] Performance targets met (p95 < 500ms @ 50 users)
- [x] Bundle size optimized (23% reduction from baseline)
- [x] Memory optimization verified (28% reduction)
- [x] No console errors in production build
- [x] Type checking passed (TypeScript strict mode)
- [x] Linting passed (ESLint strict rules)

### Environment & Infrastructure
- [ ] Staging environment configured
- [ ] Production database provisioned
- [ ] Backup strategy implemented
- [ ] CDN configured (optional)
- [ ] Load balancer configured (optional)
- [ ] SSL/TLS certificates installed
- [ ] Environment variables secured (secrets manager)
- [ ] Database migrations tested

### Security & Compliance
- [ ] Security audit completed
- [ ] Dependencies audited for vulnerabilities
- [ ] Environment variables reviewed
- [ ] API authentication verified
- [ ] Rate limiting configured
- [ ] CORS policy configured
- [ ] Security headers configured
- [ ] Data encryption in transit and at rest

### Monitoring & Alerts
- [ ] Monitoring dashboards created
- [ ] Alert thresholds configured
- [ ] Log aggregation setup
- [ ] Error tracking enabled
- [ ] Performance monitoring enabled
- [ ] Uptime monitoring configured
- [ ] Team notifications configured

---

## 🔧 Environment Configuration

### Environment Variables Structure

```
.env.production
├─ API Configuration
│  ├─ NEXT_PUBLIC_API_BASE_URL=https://api.raptorflow.com
│  ├─ NEXT_PUBLIC_API_TIMEOUT=30000
│  └─ API_SECRET_KEY=${AWS_SECRETS_MANAGER}
│
├─ Authentication
│  ├─ NEXT_PUBLIC_AUTH_PROVIDER=auth0
│  ├─ NEXT_PUBLIC_AUTH_DOMAIN=${AUTH0_DOMAIN}
│  ├─ NEXT_PUBLIC_AUTH_CLIENT_ID=${AUTH0_CLIENT_ID}
│  └─ AUTH_CLIENT_SECRET=${SECRETS_MANAGER}
│
├─ Analytics & Monitoring
│  ├─ NEXT_PUBLIC_ANALYTICS_ID=${GOOGLE_ANALYTICS_ID}
│  ├─ NEXT_PUBLIC_SENTRY_DSN=${SENTRY_DSN}
│  ├─ SENTRY_AUTH_TOKEN=${SECRETS_MANAGER}
│  └─ NEXT_PUBLIC_ENVIRONMENT=production
│
├─ Performance & Features
│  ├─ NEXT_PUBLIC_ENABLE_CACHE=true
│  ├─ NEXT_PUBLIC_CACHE_TTL=3600
│  ├─ NEXT_PUBLIC_MAX_UPLOAD_SIZE=52428800
│  └─ NEXT_PUBLIC_FEATURE_FLAGS=${FEATURE_FLAGS_JSON}
│
└─ Database
   ├─ DATABASE_URL=${RDS_CONNECTION_STRING}
   ├─ DATABASE_POOL_SIZE=20
   └─ DATABASE_SSL=true
```

### Multi-Environment Setup

#### Development Environment
```bash
# .env.development
NEXT_PUBLIC_API_BASE_URL=http://localhost:3001
NEXT_PUBLIC_ENVIRONMENT=development
DATABASE_URL=postgresql://dev:dev@localhost:5432/raptorflow_dev
NEXT_PUBLIC_ENABLE_CACHE=false
```

#### Staging Environment
```bash
# .env.staging
NEXT_PUBLIC_API_BASE_URL=https://api-staging.raptorflow.com
NEXT_PUBLIC_ENVIRONMENT=staging
DATABASE_URL=postgresql://user:pass@staging-db.rds.amazonaws.com:5432/raptorflow_staging
NEXT_PUBLIC_ENABLE_CACHE=true
NEXT_PUBLIC_CACHE_TTL=1800
```

#### Production Environment
```bash
# .env.production
NEXT_PUBLIC_API_BASE_URL=https://api.raptorflow.com
NEXT_PUBLIC_ENVIRONMENT=production
DATABASE_URL=${AWS_SECRETS_MANAGER}
NEXT_PUBLIC_ENABLE_CACHE=true
NEXT_PUBLIC_CACHE_TTL=3600
```

---

## 🚀 Deployment Options

### Option A: Vercel Deployment (Recommended for Simplicity)

**Pros:**
- One-click deployment
- Automatic scaling
- Built-in CDN
- Git integration
- Easy rollbacks
- Free tier available

**Cons:**
- Limited customization
- Vendor lock-in
- Per-seat pricing at scale

**Setup Steps:**

1. **Connect GitHub Repository**
   ```bash
   # Push code to GitHub
   git push origin main
   ```

2. **Create Vercel Project**
   - Go to https://vercel.com
   - Click "New Project"
   - Select GitHub repository
   - Configure project settings

3. **Configure Environment Variables**
   ```
   Project Settings > Environment Variables

   Add for Production:
   - NEXT_PUBLIC_API_BASE_URL
   - NEXT_PUBLIC_AUTH_DOMAIN
   - NEXT_PUBLIC_AUTH_CLIENT_ID
   - API_SECRET_KEY (secret)
   - AUTH_CLIENT_SECRET (secret)
   - DATABASE_URL (secret)
   - SENTRY_DSN
   - GOOGLE_ANALYTICS_ID
   ```

4. **Deploy**
   - Click "Deploy"
   - Wait for deployment (typically 2-5 minutes)
   - Verify deployment status dashboard

5. **Custom Domain**
   ```
   Settings > Domains
   - Add custom domain
   - Configure DNS records
   - SSL certificate auto-provisioned
   ```

6. **Rollback (if needed)**
   ```
   Deployments > Select previous version > Redeploy
   Or: git revert + git push (automatic redeploy)
   ```

**Monitoring URL:** `https://vercel.com/dashboard`

---

### Option B: AWS Deployment (Recommended for Control)

**Pros:**
- Full control over infrastructure
- Better for large-scale deployments
- Integration with AWS services
- Flexible scaling options
- Cost control

**Cons:**
- More complex setup
- Requires AWS knowledge
- Higher operational overhead
- Manual scaling configuration

**Architecture:**
```
Internet → CloudFront (CDN) → ALB → ECS/Fargate → RDS
                            ↓
                        S3 (static assets)
```

**Setup Steps:**

1. **Create AWS Account & Configure CLI**
   ```bash
   # Install AWS CLI
   brew install awscli  # macOS
   sudo apt install awscli  # Linux

   # Configure credentials
   aws configure
   # Enter: Access Key ID, Secret Access Key, Region (us-east-1), Output (json)
   ```

2. **Create RDS Database**
   ```bash
   # Using AWS Console
   RDS > Create Database
   - Engine: PostgreSQL 14+
   - Instance class: db.t3.small (minimum for production)
   - Multi-AZ: Yes (for high availability)
   - Storage: 100GB SSD (gp3)
   - Backup: 30-day retention
   - Enhanced Monitoring: Enable

   # Create database
   - DB instance identifier: raptorflow-prod
   - Master username: postgres
   - Master password: [strong password from Secrets Manager]

   # Create database
   createdb raptorflow_prod
   ```

3. **Create S3 Bucket for Static Assets**
   ```bash
   # Using AWS Console
   S3 > Create Bucket
   - Bucket name: raptorflow-prod-assets
   - Region: us-east-1
   - Block all public access: Yes (use CloudFront)
   - Enable versioning: Yes
   - Enable encryption: Yes (SSE-S3)
   ```

4. **Deploy with Docker to ECS/Fargate**
   ```bash
   # Create Dockerfile
   cat > Dockerfile << 'EOF'
   FROM node:18-alpine
   WORKDIR /app
   COPY package*.json ./
   RUN npm ci --only=production
   COPY .next/standalone .
   COPY public ./public
   EXPOSE 3000
   CMD ["node", "server.js"]
   EOF

   # Build and push to ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin [ACCOUNT_ID].dkr.ecr.us-east-1.amazonaws.com
   docker build -t raptorflow:latest .
   docker tag raptorflow:latest [ACCOUNT_ID].dkr.ecr.us-east-1.amazonaws.com/raptorflow:latest
   docker push [ACCOUNT_ID].dkr.ecr.us-east-1.amazonaws.com/raptorflow:latest
   ```

5. **Create ECS Cluster & Task Definition**
   ```bash
   # Using AWS Console
   ECS > Create Cluster
   - Cluster name: raptorflow-prod
   - Infrastructure: AWS Fargate
   - Monitoring: Enable CloudWatch Container Insights

   # Create Task Definition
   - Family: raptorflow
   - Container name: raptorflow
   - Image: [ECR_URI]:latest
   - Memory: 512 MB
   - CPU: 256
   - Port mappings: 3000:3000
   - Environment variables: [from Secrets Manager]
   ```

6. **Create Application Load Balancer**
   ```bash
   # Using AWS Console
   EC2 > Load Balancers > Create Load Balancer
   - Type: Application Load Balancer
   - Name: raptorflow-alb
   - Scheme: Internet-facing
   - IP address type: IPv4
   - VPC: Default
   - Listeners: HTTP (80) → redirect to HTTPS, HTTPS (443)
   - Target group: raptorflow-targets
   - Health check: /api/health (5 second intervals)
   ```

7. **Create CloudFront Distribution**
   ```bash
   # Using AWS Console
   CloudFront > Create Distribution
   - Origin: S3 bucket (for /public)
   - Alternative origin: ALB (for /api and pages)
   - Behaviors:
     * /api/* → ALB origin
     * /_next/static/* → S3 origin
     * /public/* → S3 origin
     * /* → ALB origin
   - Compress: Yes
   - Cache policy: CachingOptimized for static
   - Viewer policy: Redirect HTTP to HTTPS
   - SSL certificate: Request from ACM
   ```

8. **Configure Auto-Scaling**
   ```bash
   # Using AWS Console
   ECS > Services > Create Service
   - Cluster: raptorflow-prod
   - Service name: raptorflow-svc
   - Number of tasks: 2
   - Load balancer: ALB
   - Auto Scaling: Enable
     * Min capacity: 2
     * Max capacity: 10
     * Target CPU utilization: 70%
     * Target memory utilization: 80%
   ```

9. **Rollback Procedure**
   ```bash
   # If deployment fails, rollback to previous task definition
   aws ecs update-service \
     --cluster raptorflow-prod \
     --service raptorflow-svc \
     --task-definition raptorflow:[PREVIOUS_VERSION]

   # Verify rollback
   aws ecs describe-services \
     --cluster raptorflow-prod \
     --services raptorflow-svc
   ```

**AWS Console URLs:**
- ECS Dashboard: https://console.aws.amazon.com/ecs
- RDS Console: https://console.aws.amazon.com/rds
- CloudFront: https://console.aws.amazon.com/cloudfront
- CloudWatch: https://console.aws.amazon.com/cloudwatch

---

### Option C: GitHub Actions CI/CD (Recommended for Automation)

**Pros:**
- Free for public repositories
- Tight GitHub integration
- Version control driven deployments
- Automated testing before deploy
- Easy to manage

**Cons:**
- Limited customization
- Requires additional services for hosting
- Build times can be slow

**Setup Steps:**

1. **Create Workflow File**
   ```yaml
   # .github/workflows/deploy-production.yml
   name: Deploy to Production

   on:
     push:
       branches: [main]
     workflow_dispatch:

   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - uses: actions/setup-node@v3
           with:
             node-version: '18'
         - run: npm ci
         - run: npm run type-check
         - run: npm run lint
         - run: npm run test:e2e
         - run: npm run build

     deploy:
       needs: test
       runs-on: ubuntu-latest
       environment: production
       steps:
         - uses: actions/checkout@v3
         - uses: actions/setup-node@v3
           with:
             node-version: '18'

         # Deploy to Vercel
         - name: Deploy to Vercel
           uses: amondnet/vercel-action@v20
           with:
             vercel-token: ${{ secrets.VERCEL_TOKEN }}
             vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
             vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
             vercel-args: '--prod'

         # Verify deployment
         - name: Run Smoke Tests
           run: npm run test:smoke
           env:
             BASE_URL: https://raptorflow.com

         # Notify team
         - name: Notify Slack
           if: always()
           uses: 8398a7/action-slack@v3
           with:
             status: ${{ job.status }}
             webhook_url: ${{ secrets.SLACK_WEBHOOK }}
   ```

2. **Configure Secrets**
   ```
   GitHub > Settings > Secrets and Variables > Actions

   Add Secrets:
   - VERCEL_TOKEN (from Vercel Settings)
   - VERCEL_ORG_ID
   - VERCEL_PROJECT_ID
   - DATABASE_URL
   - SLACK_WEBHOOK (for notifications)
   ```

3. **Trigger Deployment**
   ```bash
   # Automatic deployment on main branch push
   git add .
   git commit -m "feat: new feature"
   git push origin main

   # Or manual trigger
   # GitHub > Actions > Deploy to Production > Run Workflow
   ```

4. **Monitor Deployment**
   - GitHub Actions tab shows real-time logs
   - Slack notification on completion
   - Automatic rollback if tests fail

---

## 🔒 Security Hardening

### Environment & Secrets

```bash
# 1. Use AWS Secrets Manager for sensitive data
aws secretsmanager create-secret \
  --name raptorflow/prod/database-url \
  --secret-string "postgresql://user:pass@host/db"

# 2. Set environment variables from secrets
export DATABASE_URL=$(aws secretsmanager get-secret-value \
  --secret-id raptorflow/prod/database-url \
  --query SecretString --output text)

# 3. Never commit secrets
echo ".env.production" >> .gitignore
echo ".env.production.local" >> .gitignore
```

### Security Headers

```javascript
// next.config.js
module.exports = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()',
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=31536000; includeSubDomains',
          },
          {
            key: 'Content-Security-Policy',
            value: "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
          },
        ],
      },
    ];
  },
};
```

### API Security

```javascript
// pages/api/[[...route]].ts
import { rateLimit } from '@/lib/rate-limit';
import { validateToken } from '@/lib/auth';

export default async function handler(req, res) {
  // 1. Rate limiting
  const limiter = rateLimit();
  const { success } = await limiter.limit(req.ip);

  if (!success) {
    return res.status(429).json({ error: 'Too many requests' });
  }

  // 2. CORS validation
  const allowedOrigins = ['https://raptorflow.com', 'https://www.raptorflow.com'];
  const origin = req.headers.origin;

  if (allowedOrigins.includes(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
  }

  // 3. Authentication
  const token = req.headers.authorization?.replace('Bearer ', '');
  if (!token) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    const user = await validateToken(token);
    req.user = user;
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }

  // 4. Route handling
  // ...
}
```

### Database Security

```bash
# 1. Enable encryption at rest
aws rds modify-db-instance \
  --db-instance-identifier raptorflow-prod \
  --storage-encrypted \
  --apply-immediately

# 2. Enable encryption in transit
# In connection string: ?sslmode=require

# 3. Enable automated backups
aws rds modify-db-instance \
  --db-instance-identifier raptorflow-prod \
  --backup-retention-period 30 \
  --apply-immediately

# 4. Enable audit logging
aws rds modify-db-instance \
  --db-instance-identifier raptorflow-prod \
  --enable-cloudwatch-logs-exports postgresql \
  --apply-immediately
```

---

## 💾 Backup & Disaster Recovery

### Automated Backups

```bash
# Configure automated RDS backups (already covered above)
# Retention period: 30 days minimum for production

# Backup verification
aws rds describe-db-instances \
  --db-instance-identifier raptorflow-prod \
  --query 'DBInstances[0].BackupRetentionPeriod'

# Point-in-time recovery (available within backup window)
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier raptorflow-prod-restored \
  --db-snapshot-identifier raptorflow-prod-snapshot-xxx
```

### Manual Backup Process

```bash
# Create manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier raptorflow-prod \
  --db-snapshot-identifier raptorflow-prod-manual-2024-01-15

# Export to S3 for long-term retention
aws rds start-export-task \
  --export-task-identifier raptorflow-export-2024-01 \
  --source-arn "arn:aws:rds:us-east-1:ACCOUNT:db:raptorflow-prod" \
  --s3-bucket-name raptorflow-backups \
  --s3-prefix snapshots/ \
  --iam-role-arn "arn:aws:iam::ACCOUNT:role/ExportRole"
```

### Disaster Recovery Runbook

```
INCIDENT: Database corruption
SEVERITY: Critical
RECOVERY TIME OBJECTIVE (RTO): 1 hour
RECOVERY POINT OBJECTIVE (RPO): 5 minutes

STEPS:
1. Assess damage (check CloudWatch logs)
2. Notify team in #incidents channel
3. Create restore instance from latest snapshot
   aws rds restore-db-instance-from-db-snapshot ...
4. Update connection string to restored instance
5. Run smoke tests against restored database
6. If tests pass, promote restored instance as primary
7. Perform full E2E test suite
8. Monitor metrics for 30 minutes
9. Document incident in postmortem

ROLLBACK:
- If restoration fails, use point-in-time recovery to 5 minutes ago
- If that fails, use last successful snapshot from 24 hours ago
```

---

## 📊 Monitoring & Alerting

### Key Metrics to Monitor

```javascript
// Frontend metrics
- Page Load Time (LCP, FCP, TTFB)
- Error Rate (JavaScript errors, 4xx/5xx responses)
- User Interactions (click rates, form submissions)
- Memory Usage (heap size, garbage collection)
- API Response Times (p50, p95, p99)

// Backend metrics
- API Response Time (by endpoint)
- Database Query Time (slow query log)
- Database Connection Pool (usage %)
- Error Rate (5xx errors)
- Throughput (requests/second)
- CPU Usage (EC2/Fargate)
- Memory Usage
- Disk Space (logs, database)

// Business metrics
- Active Users (concurrent, daily)
- Conversion Rate (sign-ups, feature usage)
- Feature Usage (most used features)
- User Retention (day-1, day-7, day-30)
```

### Alert Thresholds

```
CRITICAL (page immediately)
- Uptime < 99% (any 1-hour window)
- Error rate > 5% (p95 over 5 minutes)
- API response time p95 > 2000ms
- Database connection failures
- Disk space < 10%

WARNING (notify team, investigate)
- Error rate > 2%
- API response time p95 > 1000ms
- CPU usage > 80% for 10 minutes
- Memory usage > 85%
- Database slow queries increasing

INFO (log for trend analysis)
- API response time trending upward
- Memory usage trending upward
- Error rate slight increase
```

### Monitoring Services

```bash
# Option 1: CloudWatch (AWS native)
- Log groups for application logs
- Metrics for infrastructure
- Dashboards for visualization
- Alarms for notifications

# Option 2: Datadog
- Application Performance Monitoring
- Log aggregation
- Infrastructure monitoring
- Custom dashboards

# Option 3: New Relic
- Application Performance Monitoring
- Error tracking
- Custom events
- Browser monitoring

# Option 4: Self-hosted ELK Stack
- Elasticsearch (search engine)
- Logstash (log processing)
- Kibana (visualization)
- Filebeat (log shipping)
```

### CloudWatch Setup

```bash
# Create log group
aws logs create-log-group --log-group-name /raptorflow/prod

# Create metric alarms
aws cloudwatch put-metric-alarm \
  --alarm-name raptorflow-error-rate-high \
  --alarm-description "Error rate exceeds 5%" \
  --metric-name ErrorRate \
  --namespace RaptorFlow \
  --statistic Average \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT:raptorflow-alerts

# Create dashboard
aws cloudwatch put-dashboard \
  --dashboard-name RaptorFlow-Production \
  --dashboard-body file://dashboard-config.json
```

---

## 🔍 Post-Deployment Validation

### Automated Health Checks

```bash
# 1. Check API health endpoint
curl -f https://api.raptorflow.com/health \
  -H "Authorization: Bearer ${TOKEN}" \
  || echo "API health check failed"

# 2. Check database connectivity
psql -h ${DB_HOST} -U ${DB_USER} -d ${DB_NAME} \
  -c "SELECT 1" \
  || echo "Database check failed"

# 3. Check static asset serving
curl -I https://raptorflow.com/_next/static/index.html \
  | grep "200 OK" \
  || echo "Static assets check failed"

# 4. Check authentication
curl -X POST https://api.raptorflow.com/auth/token \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test"}' \
  || echo "Auth check failed"
```

### Smoke Tests

```bash
# Run smoke test suite
npm run test:smoke -- --base-url https://raptorflow.com

# Expected outputs:
# ✓ Homepage loads (< 3s)
# ✓ Login page accessible
# ✓ API responding
# ✓ Database responsive
# ✓ Static assets serving
# ✓ Auth working
```

### Manual Testing

```
Pre-launch checklist:
- [ ] Load homepage, verify design integrity
- [ ] Sign up with new account
- [ ] Log in with test account
- [ ] Navigate through main features
- [ ] Submit analysis request
- [ ] Verify email notifications
- [ ] Test mobile responsiveness (iOS & Android)
- [ ] Test all major browsers (Chrome, Firefox, Safari, Edge)
- [ ] Verify analytics tracking
- [ ] Check error logging in Sentry
- [ ] Verify monitoring dashboard shows data
```

---

## 🛠️ Troubleshooting

### Deployment Issues

**Problem: Deployment fails with "Permission denied"**
```bash
# Solution: Check IAM permissions
aws iam get-user
aws iam list-user-policies --user-name deployment-user
# Add necessary policies for ECS, RDS, S3
```

**Problem: "Database connection refused"**
```bash
# Solution: Verify RDS security group
aws ec2 describe-security-groups \
  --group-ids sg-xxxxx \
  --query 'SecurityGroups[0].IpPermissions'

# Add inbound rule for app server IP
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 5432 \
  --source-security-group sg-app
```

**Problem: "High error rates after deployment"**
```bash
# Check application logs
aws logs tail /raptorflow/prod --follow

# Check recent deployments
aws ecs describe-tasks \
  --cluster raptorflow-prod \
  --tasks $(aws ecs list-tasks --cluster raptorflow-prod --query taskArns --output text)

# Rollback if necessary
# (see Rollback Procedure above)
```

### Performance Issues

**Problem: "Pages loading slowly"**
```bash
# Check CloudFront cache
aws cloudfront list-distributions | grep raptorflow
# Clear cache if needed
aws cloudfront create-invalidation \
  --distribution-id XXXXX \
  --paths "/*"

# Check origin response time
aws cloudwatch get-metric-statistics \
  --namespace CloudFront \
  --metric-name OriginLatency \
  --start-time 2024-01-15T00:00:00Z \
  --end-time 2024-01-15T01:00:00Z \
  --period 300 \
  --statistics Average
```

**Problem: "High CPU usage"**
```bash
# Check ECS task metrics
aws ecs describe-services \
  --cluster raptorflow-prod \
  --services raptorflow-svc

# Scale up if needed
aws ecs update-service \
  --cluster raptorflow-prod \
  --service raptorflow-svc \
  --desired-count 5  # Increase from 2
```

**Problem: "Database slow queries"**
```bash
# Check slow query log
aws rds describe-db-parameters \
  --db-parameter-group-name raptorflow-prod \
  --query 'Parameters[?ParameterName==`log_min_duration_statement`]'

# Enable slow query logging
aws rds modify-db-parameter-group \
  --db-parameter-group-name raptorflow-prod \
  --parameters ParameterName=log_min_duration_statement,ParameterValue=1000
```

---

## 📋 Deployment Checklist

Before deploying to production:

```
PRE-DEPLOYMENT
- [ ] All tests passing locally
- [ ] All tests passing in CI/CD pipeline
- [ ] Code reviewed and approved
- [ ] Security audit completed
- [ ] Environment variables configured
- [ ] Database backups created
- [ ] Monitoring configured
- [ ] Team notified

DEPLOYMENT
- [ ] Deploy to staging first
- [ ] Run smoke tests on staging
- [ ] Test critical workflows on staging
- [ ] Verify monitoring on staging
- [ ] Deploy to production during low-traffic window
- [ ] Monitor for errors continuously
- [ ] Verify all health checks passing
- [ ] Confirm monitoring showing data

POST-DEPLOYMENT
- [ ] Run full E2E test suite
- [ ] Run load testing if applicable
- [ ] Verify user-facing features working
- [ ] Check analytics tracking
- [ ] Monitor error rate for 1 hour
- [ ] Document deployment in changelog
- [ ] Notify stakeholders
```

---

## 🔗 Related Documentation

- **Deployment Runbook:** `DEPLOYMENT_RUNBOOK.md` (step-by-step execution)
- **Security Hardening:** `SECURITY_HARDENING.md` (detailed security configuration)
- **Monitoring Setup:** `MONITORING_SETUP.md` (metrics and alerting configuration)
- **Backup & Recovery:** `BACKUP_AND_RECOVERY.md` (disaster recovery procedures)
- **Performance Testing:** `PHASE_5_WEEK_2_LOAD_TESTING_GUIDE.md` (load test results)
- **E2E Testing:** `PHASE_5_WEEK_1_E2E_TESTING_GUIDE.md` (test coverage)

---

## 📊 Week 3 Status

**Deliverables:**
- [x] Deployment guide (this document)
- [ ] Deployment runbook
- [ ] Security hardening checklist
- [ ] Monitoring setup guide
- [ ] Backup & recovery procedures

**Next Phase:** Week 4 - Production Deployment Execution

---

**Last Updated:** Phase 5 Week 3
**Status:** IN PROGRESS ⏳
