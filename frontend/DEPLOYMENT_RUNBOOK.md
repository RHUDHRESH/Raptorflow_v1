# 📖 Deployment Runbook

Step-by-step operational procedures for deploying RaptorFlow 2.0 to production.

---

## 🎯 Quick Reference

| Task | Duration | Risk | Owner |
|------|----------|------|-------|
| Pre-deployment validation | 15 min | Low | DevOps |
| Staging deployment | 10 min | Low | DevOps |
| Staging smoke tests | 10 min | Low | QA |
| Production deployment | 10 min | Medium | DevOps |
| Post-deployment validation | 20 min | Low | QA/DevOps |
| **Total** | **65 min** | - | - |

---

## ⚠️ Important Reminders

1. **Always deploy during low-traffic window** (2-4 AM UTC or similar)
2. **Have a rollback plan** (see rollback procedure)
3. **Monitor continuously** for 1 hour after deployment
4. **Keep team informed** via #deployments Slack channel
5. **Document everything** in deployment log

---

## 📋 Pre-Deployment (15 minutes)

### Step 1: Verify CI/CD Pipeline Status (5 min)

```bash
# 1a. Check GitHub Actions status
# Navigate to: https://github.com/raptorflow/frontend/actions

# Expected: All tests passing on main branch
# If failing: DO NOT PROCEED - fix failures first

# 1b. Verify build artifacts created
# Expected: deployment package in artifacts
```

### Step 2: Verify Environment & Secrets (5 min)

```bash
# 2a. Check production secrets configured
aws secretsmanager list-secrets \
  --filters Key=name,Values=raptorflow/prod \
  --region us-east-1

# Expected output should show:
# - raptorflow/prod/database-url
# - raptorflow/prod/api-secret
# - raptorflow/prod/auth-secret

# If missing: CREATE IMMEDIATELY
aws secretsmanager create-secret \
  --name raptorflow/prod/database-url \
  --secret-string "postgresql://..." \
  --region us-east-1

# 2b. Verify environment variables set
# For Vercel deployments
vercel env ls --prod

# Expected: All required vars configured (check DEPLOYMENT_GUIDE.md)

# 2c. Test database connection
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1"

# Expected output: (1 row selected)
```

### Step 3: Database Backup (5 min)

```bash
# 3a. Create manual backup before deployment
aws rds create-db-snapshot \
  --db-instance-identifier raptorflow-prod \
  --db-snapshot-identifier raptorflow-prod-pre-deploy-2024-01-15

# Wait for snapshot to complete
aws rds wait db-snapshot-available \
  --db-snapshot-identifier raptorflow-prod-pre-deploy-2024-01-15

# Expected: Snapshot status = AVAILABLE (2-5 minutes)

# 3b. Verify backup completion
aws rds describe-db-snapshots \
  --db-snapshot-identifier raptorflow-prod-pre-deploy-2024-01-15 \
  --query 'DBSnapshots[0].Status'

# Expected output: available
```

### ✅ Pre-Deployment Checklist

```
☐ All CI/CD tests passing
☐ Environment secrets configured
☐ Database connection verified
☐ Pre-deployment backup created
☐ Team notified in Slack
☐ Runbook printed/available
```

---

## 🎪 Staging Deployment (10 minutes)

### Step 4: Deploy to Staging (5 min)

#### For Vercel Deployments

```bash
# 4a. Deploy staging environment
vercel --prod --env staging

# Expected: Deployment URL provided
# Example: https://raptorflow-staging.vercel.app

# 4b. Wait for deployment to complete
# Check Vercel dashboard: https://vercel.com/dashboard/deployments

# Expected: Green checkmark, deployment ready
# Time: 2-5 minutes
```

#### For AWS ECS Deployments

```bash
# 4a. Update ECS task definition with new image
aws ecs register-task-definition \
  --cli-input-json file://task-definition-staging.json \
  --region us-east-1

# Expected: New task definition version created (e.g., raptorflow-staging:45)

# 4b. Update service with new task definition
TASK_DEF=$(aws ecs describe-task-definition \
  --task-definition raptorflow-staging \
  --region us-east-1 \
  --query 'taskDefinition.revision' --output text)

aws ecs update-service \
  --cluster raptorflow-staging \
  --service raptorflow-svc-staging \
  --task-definition raptorflow-staging:${TASK_DEF} \
  --force-new-deployment \
  --region us-east-1

# Expected: Service update initiated
# Time: 2-5 minutes

# 4c. Monitor deployment
aws ecs wait services-stable \
  --cluster raptorflow-staging \
  --services raptorflow-svc-staging \
  --region us-east-1

# Expected: Service reaches stable state
```

### Step 5: Staging Smoke Tests (5 min)

```bash
# 5a. Wait for deployment to stabilize (2 min)
sleep 120

# 5b. Run smoke tests against staging
npm run test:smoke -- \
  --base-url https://raptorflow-staging.vercel.app \
  --timeout 10000

# Expected output:
# ✓ Homepage loads (1200ms)
# ✓ Login page loads (800ms)
# ✓ API health check passes
# ✓ Database connectivity OK
# All tests: 6/6 passed ✅

# If tests fail: CHECK LOGS
# 5c. Check deployment logs
# For Vercel:
vercel logs

# For ECS:
aws logs tail /raptorflow/staging --follow --since 5m
```

### ✅ Staging Checklist

```
☐ Staging deployment completed
☐ Deployment URL available
☐ All smoke tests passing
☐ No errors in logs
☐ Basic features working manually
```

---

## 🚀 Production Deployment (10 minutes)

### Step 6: Deploy to Production (5 min)

#### For Vercel Deployments (Recommended)

```bash
# 6a. Deploy to production
vercel --prod

# Expected: Production deployment URL
# Example: https://raptorflow.com

# 6b. Monitor deployment
# Check Vercel dashboard: https://vercel.com/dashboard/deployments

# Expected: Green checkmark (2-5 minutes)
# Check production URL loads without errors

# 6c. Verify deployment using curl
for i in {1..5}; do
  curl -s -o /dev/null -w "HTTP %{http_code} - %{time_total}s\n" \
    https://raptorflow.com
  sleep 2
done

# Expected: HTTP 200 - consistent fast responses
```

#### For AWS ECS Deployments

```bash
# 6a. Get latest task definition
TASK_DEF=$(aws ecs describe-task-definition \
  --task-definition raptorflow \
  --region us-east-1 \
  --query 'taskDefinition.revision' --output text)

# 6b. Update production service with new task definition
aws ecs update-service \
  --cluster raptorflow-prod \
  --service raptorflow-svc \
  --task-definition raptorflow:${TASK_DEF} \
  --force-new-deployment \
  --region us-east-1

# Expected: Service update initiated

# 6c. Wait for deployment
aws ecs wait services-stable \
  --cluster raptorflow-prod \
  --services raptorflow-svc \
  --region us-east-1

# Time: 3-10 minutes depending on health check interval

# 6d. Monitor during deployment
watch -n 5 'aws ecs describe-services \
  --cluster raptorflow-prod \
  --services raptorflow-svc \
  --region us-east-1 \
  --query "services[0].{
    desiredCount:desiredCount,
    runningCount:runningCount,
    pendingCount:pendingCount,
    status:status
  }" --output table'

# Expected: Running count == desired count (2, 3, or more)
```

### Step 7: Production Health Checks (5 min)

```bash
# 7a. Check API health endpoint (health check)
curl -f https://api.raptorflow.com/health \
  -H "Authorization: Bearer ${HEALTH_CHECK_TOKEN}" \
  -w "\nHTTP Status: %{http_code}\n"

# Expected: 200 OK response with health data

# 7b. Check main domain
curl -I https://raptorflow.com \
  -w "\nHTTP Status: %{http_code}\n"

# Expected: 200 or 301 (if redirect)

# 7c. Check CloudFront/CDN
curl -I https://raptorflow.com \
  -H "Accept-Encoding: gzip" \
  | grep -E "X-Cache|Cache-Control"

# Expected: Cache headers present

# 7d. Check database from app
# Application should be able to query database
curl -s https://api.raptorflow.com/status \
  -H "Authorization: Bearer ${TOKEN}" \
  | jq '.database'

# Expected: { "connected": true, "status": "ok" }
```

### ✅ Production Deployment Checklist

```
☐ Production deployment initiated
☐ Deployment visible in Vercel/ECS
☐ Health check endpoint responding
☐ API endpoints responding
☐ Database query successful
☐ No 5xx errors in logs
☐ CDN cache working
```

---

## ✅ Post-Deployment Validation (20 minutes)

### Step 8: Automated Validation (10 min)

```bash
# 8a. Run full E2E test suite against production
npm run test:e2e -- \
  --base-url https://raptorflow.com \
  --config playwright.config.prod.ts

# Expected: All 50+ tests passing
# Duration: 5-10 minutes

# 8b. Check monitoring dashboard
# Navigate to: CloudWatch/Datadog/etc dashboard
# Verify:
# - No spike in error rate
# - Response times normal (< 1000ms p95)
# - CPU/Memory usage normal
# - No alerts triggered

# 8c. Verify error tracking
# Check Sentry: https://sentry.io/raptorflow
# Expected: No new critical errors

# 8d. Check analytics
# Google Analytics should show:
# - Page views increasing (normal traffic)
# - User engagement normal
# - No unusual bounce rate
```

### Step 9: Manual Validation (10 min)

```bash
# 9a. Sign up and create account
# 1. Navigate to https://raptorflow.com/signup
# 2. Fill in registration form
# 3. Verify email received
# 4. Confirm email verification
# Expected: Account created successfully

# 9b. Login and test features
# 1. Login with test account
# 2. Navigate to workspace
# 3. Create/load a strategy
# 4. Submit analysis request
# Expected: All features functional

# 9c. Check mobile responsiveness
# 1. Open on iPhone/Android
# 2. Check design integrity
# 3. Test main workflows
# Expected: Mobile experience good

# 9d. Browser compatibility
# Test in:
# - Chrome (latest)
# - Firefox (latest)
# - Safari (latest)
# - Edge (latest)
# Expected: Works in all browsers

# 9e. Check email notifications
# 1. Create new account
# 2. Check email for welcome message
# 3. Trigger analysis
# 4. Check email for results
# Expected: All emails received and formatted correctly
```

### Step 10: Continuous Monitoring (10 min + ongoing)

```bash
# 10a. Set up tail monitoring
aws logs tail /raptorflow/prod --follow &
tail -f monitoring-dashboard.log &

# 10b. Check for errors
watch -n 2 'aws logs filter-log-events \
  --log-group-name /raptorflow/prod \
  --filter-pattern "ERROR" \
  --start-time $(($(date +%s)*1000 - 600000)) \
  --query "events | length(@)"'

# Expected: Error count < 10 in first 10 minutes

# 10c. Monitor error rate metric
aws cloudwatch get-metric-statistics \
  --namespace RaptorFlow \
  --metric-name ErrorRate \
  --start-time 2024-01-15T12:00:00Z \
  --end-time 2024-01-15T12:10:00Z \
  --period 60 \
  --statistics Average

# Expected: Average < 2%

# 10d. Check response time trending
aws cloudwatch get-metric-statistics \
  --namespace RaptorFlow \
  --metric-name ResponseTime \
  --start-time 2024-01-15T12:00:00Z \
  --end-time 2024-01-15T12:10:00Z \
  --period 60 \
  --statistics Average

# Expected: Average < 500ms
```

### ✅ Post-Deployment Checklist

```
☐ All E2E tests passing
☐ No new errors in logs
☐ Error rate < 2%
☐ Response times normal
☐ Sign up working
☐ Login working
☐ Features functioning
☐ Mobile working
☐ Emails sending
☐ Analytics tracking
☐ Monitoring dashboard updated
```

---

## 🔄 Rollback Procedure (Emergency)

**Use only if something goes wrong!**

### For Vercel

```bash
# 1. Identify previous working deployment
vercel deployments --prod | head -5

# Expected: List of recent deployments
# Example:
# raptorflow.com      ready 2024-01-15 15:32:10 UTC  [previous]
# raptorflow.com      ready 2024-01-15 15:27:03 UTC  [current-broken]

# 2. Redeploy previous version
vercel rollback

# OR manually:
PREVIOUS_URL="[URL from above]"
vercel alias set $PREVIOUS_URL raptorflow.com

# 3. Verify rollback
curl https://raptorflow.com/health

# Expected: Works correctly

# 4. Notify team
# Post in #deployments: "🔄 Rolled back to previous version due to [reason]"
```

### For AWS ECS

```bash
# 1. Get previous task definition
aws ecs describe-task-definition \
  --task-definition raptorflow \
  --region us-east-1 \
  --query 'taskDefinition.revision' \
  --output text

# Example output: 42 (current), 41 (previous)

# 2. Rollback to previous task definition
aws ecs update-service \
  --cluster raptorflow-prod \
  --service raptorflow-svc \
  --task-definition raptorflow:41 \
  --force-new-deployment \
  --region us-east-1

# 3. Wait for rollback
aws ecs wait services-stable \
  --cluster raptorflow-prod \
  --services raptorflow-svc \
  --region us-east-1

# Expected: Stable state reached (5-10 minutes)

# 4. Verify health
curl https://api.raptorflow.com/health

# Expected: 200 OK response
```

### Database Rollback (if needed)

```bash
# 1. Stop application
aws ecs update-service \
  --cluster raptorflow-prod \
  --service raptorflow-svc \
  --desired-count 0 \
  --region us-east-1

# 2. Restore database from pre-deployment snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier raptorflow-prod-restored \
  --source-db-snapshot-identifier raptorflow-prod-pre-deploy-2024-01-15 \
  --region us-east-1

# 3. Wait for restoration (10-20 minutes)
aws rds wait db-instance-available \
  --db-instance-identifier raptorflow-prod-restored \
  --region us-east-1

# 4. Point app to restored database
# Update environment variable: DATABASE_URL
# Restart application

# 5. Verify
psql -h [restored-db-host] -U postgres -d raptorflow -c "SELECT COUNT(*) FROM users"

# Expected: Shows correct user count
```

---

## 📊 Deployment Log Template

```
DEPLOYMENT LOG
==============

Date: 2024-01-15
Time: 02:30 UTC
Operator: [Your Name]
Approval: [Manager Name]

PRE-DEPLOYMENT
☐ 02:30 - CI/CD pipeline verified PASSING
☐ 02:31 - Secrets verified CONFIGURED
☐ 02:32 - Database backup created: raptorflow-prod-pre-deploy-2024-01-15
☐ 02:35 - Team notified in #deployments

STAGING DEPLOYMENT
☐ 02:36 - Staging deployment initiated
☐ 02:41 - Staging deployment COMPLETE
☐ 02:42 - Smoke tests PASSING
☐ 02:47 - Staging validation PASSED

PRODUCTION DEPLOYMENT
☐ 02:48 - Production deployment initiated
☐ 02:53 - Production deployment COMPLETE
☐ 02:54 - Health checks PASSING
☐ 02:59 - Manual validation PASSED
☐ 03:09 - Full test suite PASSING

CONCLUSION
Status: ✅ SUCCESSFUL
Issues: NONE
Rollback needed: NO
Next check: 04:00 UTC

Notes:
- Everything deployed smoothly
- No errors detected
- Monitoring shows normal metrics
- Ready for next deployment window
```

---

## 🆘 Common Issues & Solutions

### Issue: Deployment stuck in progress

```bash
# Check task status
aws ecs describe-services \
  --cluster raptorflow-prod \
  --services raptorflow-svc \
  --region us-east-1

# If stuck > 15 minutes, cancel and retry
aws ecs update-service \
  --cluster raptorflow-prod \
  --service raptorflow-svc \
  --task-definition raptorflow:[PREVIOUS] \
  --force-new-deployment \
  --region us-east-1
```

### Issue: Health checks failing

```bash
# Check logs
aws logs tail /raptorflow/prod --follow

# Common causes:
# 1. Database not accessible
#    - Verify RDS security group
#    - Verify DATABASE_URL correct
# 2. API not starting
#    - Check application logs
#    - Verify all environment variables set
# 3. Health check endpoint broken
#    - Verify /health endpoint exists
#    - Check for 500 errors
```

### Issue: High error rate after deployment

```bash
# Check error logs
aws logs filter-log-events \
  --log-group-name /raptorflow/prod \
  --filter-pattern "ERROR" \
  --start-time $(($(date +%s)*1000 - 300000))

# Common causes:
# 1. Database migration not run
#    - Check migration status
#    - Run pending migrations manually
# 2. API dependency failed
#    - Check backend logs
#    - Verify backend deployed successfully
# 3. Environment variable missing
#    - Check all required vars set
#    - Reload environment

# IMMEDIATE ACTION: Rollback (see above)
```

---

## 📞 Escalation

If deployment fails and you can't resolve:

1. **Immediate (< 5 min):** Post in #incidents Slack channel
2. **2-minute window:** Rollback deployment (use procedure above)
3. **Once rolled back:** Investigate root cause
4. **Before retry:** Document and fix issue
5. **Next attempt:** After getting approval from tech lead

---

## 🎯 Success Criteria

Deployment is **successful** when:

✅ All CI/CD tests passing
✅ Staging deployment successful
✅ Staging smoke tests passing
✅ Production deployment complete
✅ Health checks passing
✅ E2E tests passing on production
✅ Error rate < 2%
✅ Response times normal
✅ Manual validation complete
✅ Monitoring shows no alerts
✅ Zero-knowledge users can navigate

---

**Last Updated:** Phase 5 Week 3
**Next Update:** After first production deployment
