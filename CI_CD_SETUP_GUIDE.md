# CI/CD Setup Guide for RaptorFlow

This guide provides comprehensive documentation for the CI/CD pipeline setup for the RaptorFlow project.

## Overview

The RaptorFlow CI/CD pipeline consists of:

1. **Enhanced CI Pipeline** - Comprehensive testing, security scanning, and quality checks
2. **Enhanced CD Pipeline** - Automated deployment to staging and production environments
3. **Monitoring Pipeline** - Continuous monitoring and alerting for deployed services

## Prerequisites

### Required GitHub Secrets

Configure these secrets in your GitHub repository settings:

#### Core Infrastructure
- `GCP_PROJECT_ID` - Your Google Cloud Project ID
- `GCP_SA_KEY` - Service account key with appropriate permissions (JSON format)

#### API Keys
- `OPENAI_API_KEY` - OpenAI API key for testing
- `GEMINI_API_KEY` - Google Gemini API key for testing
- `TEST_SUPABASE_URL` - Supabase URL for testing
- `TEST_SUPABASE_KEY` - Supabase key for testing

#### Environment URLs
- `STAGING_BACKEND_URL` - Staging backend service URL
- `STAGING_FRONTEND_URL` - Staging frontend service URL
- `PRODUCTION_BACKEND_URL` - Production backend service URL
- `PRODUCTION_FRONTEND_URL` - Production frontend service URL

#### Monitoring & Notifications
- `SLACK_WEBHOOK` - Slack webhook URL for notifications
- `SONAR_TOKEN` - SonarCloud token for code quality analysis
- `LHCI_GITHUB_APP_TOKEN` - Lighthouse CI GitHub App token

#### Production Secrets
- `PRODUCTION_SUPABASE_URL`
- `PRODUCTION_SUPABASE_KEY`
- `PRODUCTION_OPENAI_API_KEY`
- `PRODUCTION_GEMINI_API_KEY`
- `PRODUCTION_RAZORPAY_KEY_ID`
- `PRODUCTION_RAZORPAY_KEY_SECRET`
- `PRODUCTION_JWT_SECRET`
- `PRODUCTION_ENCRYPTION_KEY`
- `PRODUCTION_SENTRY_DSN`

#### Staging Secrets
- `STAGING_SUPABASE_URL`
- `STAGING_SUPABASE_KEY`
- `STAGING_OPENAI_API_KEY`
- `STAGING_GEMINI_API_KEY`
- `STAGING_RAZORPAY_KEY_ID`
- `STAGING_RAZORPAY_KEY_SECRET`
- `STAGING_JWT_SECRET`
- `STAGING_ENCRYPTION_KEY`
- `STAGING_SENTRY_DSN`

### Google Cloud Setup

1. **Enable Required APIs:**
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable cloudscheduler.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

2. **Create Service Account:**
   ```bash
   gcloud iam service-accounts create raptorflow-cicd \
     --description="CI/CD Service Account" \
     --display-name="RaptorFlow CI/CD"
   ```

3. **Grant Permissions:**
   ```bash
   # Cloud Build permissions
   gcloud projects add-iam-policy-binding $PROJECT_ID \
     --member="serviceAccount:raptorflow-cicd@$PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/cloudbuild.builds.builder"
   
   # Cloud Run permissions
   gcloud projects add-iam-policy-binding $PROJECT_ID \
     --member="serviceAccount:raptorflow-cicd@$PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/run.admin"
   
   # Storage permissions for container registry
   gcloud projects add-iam-policy-binding $PROJECT_ID \
     --member="serviceAccount:raptorflow-cicd@$PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/storage.admin"
   ```

4. **Generate Service Account Key:**
   ```bash
   gcloud iam service-accounts keys create key.json \
     --iam-account=raptorflow-cicd@$PROJECT_ID.iam.gserviceaccount.com
   ```

## Pipeline Workflows

### 1. Enhanced CI Pipeline (`enhanced-ci.yml`)

**Triggers:**
- Push to `main`, `develop`, or `feature/*` branches
- Pull requests to `main` or `develop`

**Jobs:**

#### Code Quality Checks
- Python code formatting with `black` and `isort`
- Python linting with `flake8`
- TypeScript linting
- SonarCloud code analysis

#### Backend Tests
- Security checks with `safety` and `bandit`
- Type checking with `mypy`
- Unit tests with coverage reporting
- Integration tests
- Coverage upload to Codecov

#### Frontend Tests
- Security audit with `npm audit`
- Type checking with TypeScript
- Unit tests with Jest
- E2E tests with Playwright
- Build verification

#### Security Scan
- Trivy vulnerability scanner
- OWASP ZAP baseline scan
- Container security scanning

#### Performance Tests
- Lighthouse CI for performance testing
- Performance regression detection

#### Docker Build Test
- Multi-platform Docker builds
- Container health checks

### 2. Enhanced CD Pipeline (`enhanced-cd.yml`)

**Triggers:**
- Push to `main` branch (auto-deploy to staging)
- Tag pushes (auto-deploy to production)
- Manual workflow dispatch

**Jobs:**

#### Pre-deployment Checks
- Version generation
- Deployment decision logic
- Secret validation

#### Build and Push Images
- Multi-platform Docker builds
- SBOM generation
- Image tagging strategy

#### Deploy to Staging
- Cloud Run deployment
- Health checks
- Smoke tests
- Slack notifications

#### Deploy to Production
- Production deployment with higher resources
- Comprehensive health checks
- Production smoke tests
- Deployment records

#### Post-deployment Validation
- Performance testing
- Security validation
- Dashboard updates
- Image cleanup

### 3. Monitoring Pipeline (`monitoring.yml`)

**Triggers:**
- Scheduled every 5 minutes
- Manual dispatch
- Push to main branch

**Jobs:**

#### Health Monitoring
- Service health checks
- URL availability testing
- Alert on service failures

#### Performance Monitoring
- Cloud Run metrics collection
- Error rate monitoring
- Performance alerting

#### Security Monitoring
- Authentication failure monitoring
- Suspicious activity detection
- Security event alerting

#### Cost Monitoring
- Billing information checks
- Cost pattern analysis
- Cost alerting

#### Backup Monitoring
- Backup status verification
- Backup failure alerting

## Environment Configuration

### Staging Environment (`.env.staging`)
- Lower resource allocation
- Staging-specific API keys
- Debugging enabled
- Relaxed rate limiting

### Production Environment (`.env.production`)
- Higher resource allocation
- Production API keys
- Debugging disabled
- Strict rate limiting
- Enhanced security settings

## Testing Strategy

### Backend Testing
1. **Unit Tests** - Fast, isolated component tests
2. **Integration Tests** - API endpoint testing
3. **Security Tests** - Vulnerability scanning
4. **Performance Tests** - Load and stress testing

### Frontend Testing
1. **Unit Tests** - Component testing with Jest
2. **E2E Tests** - Full user journey testing with Playwright
3. **Performance Tests** - Lighthouse CI
4. **Security Tests** - Dependency scanning

## Deployment Strategy

### Blue-Green Deployment
- Zero-downtime deployments
- Immediate rollback capability
- Health check validation

### Canary Deployments (Future Enhancement)
- Gradual traffic shifting
- A/B testing capability
- Progressive rollout

## Monitoring and Alerting

### Metrics Collected
- Service health and availability
- Response times and error rates
- Resource utilization
- Security events
- Cost metrics

### Alert Channels
- Slack notifications
- GitHub issues (optional)
- Email alerts (optional)

## Security Best Practices

1. **Secret Management**
   - All secrets stored in GitHub Secrets
   - Environment-specific secret isolation
   - Regular secret rotation

2. **Container Security**
   - Multi-stage builds
   - Minimal base images
   - Vulnerability scanning
   - SBOM generation

3. **Network Security**
   - HTTPS enforcement
   - VPC isolation
   - Firewall rules

4. **Code Security**
   - Static code analysis
   - Dependency scanning
   - Security testing

## Troubleshooting

### Common Issues

#### Build Failures
1. Check dependency versions
2. Verify test configurations
3. Review build logs for specific errors

#### Deployment Failures
1. Verify service account permissions
2. Check environment variable configuration
3. Review Cloud Run service logs

#### Test Failures
1. Check test environment setup
2. Verify test data and mocks
3. Review test logs for specific failures

### Debugging Steps

1. **Check GitHub Actions Logs**
   - Review individual job logs
   - Check for error messages
   - Verify artifact uploads

2. **Check Cloud Run Logs**
   ```bash
   gcloud logs read "resource.type=cloud_run_revision" --limit=50
   ```

3. **Check Service Health**
   ```bash
   curl -f https://your-service-url/health
   ```

## Maintenance

### Regular Tasks
1. **Update Dependencies**
   - Regular dependency updates
   - Security patch applications
   - Base image updates

2. **Review and Optimize**
   - Pipeline performance review
   - Cost optimization
   - Resource allocation tuning

3. **Security Reviews**
   - Secret rotation
   - Permission audit
   - Security scan review

## Best Practices

1. **Commit Messages**
   - Use semantic versioning
   - Clear, descriptive messages
   - Reference issue numbers

2. **Branch Management**
   - Feature branches for development
   - Main branch for production-ready code
   - Develop branch for integration

3. **Release Management**
   - Tag releases with version numbers
   - Maintain release notes
   - Automated release notes generation

## Future Enhancements

1. **Advanced Testing**
   - Contract testing
   - Chaos engineering
   - Performance regression testing

2. **Advanced Deployment**
   - Canary deployments
   - Blue-green with traffic splitting
   - Multi-region deployments

3. **Enhanced Monitoring**
   - Custom dashboards
   - Advanced alerting rules
   - Predictive monitoring

4. **Security Enhancements**
   - Runtime security monitoring
   - Advanced threat detection
   - Compliance reporting

## Support

For issues or questions about the CI/CD pipeline:

1. Check this documentation
2. Review GitHub Actions logs
3. Check Google Cloud console
4. Contact the DevOps team

---

*Last updated: $(date)*
*Version: 1.0.0*
