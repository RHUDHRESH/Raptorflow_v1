# GitHub Repository Setup Guide for RaptorFlow

This comprehensive guide walks you through setting up a secure, production-ready GitHub repository for the RaptorFlow project.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Repository Initialization](#repository-initialization)
3. [Branch Protection Rules](#branch-protection-rules)
4. [Required Secrets](#required-secrets)
5. [Team and Access Management](#team-and-access-management)
6. [Security Settings](#security-settings)
7. [Integrations and Webhooks](#integrations-and-webhooks)
8. [Issue and Project Management](#issue-and-project-management)
9. [Release Management](#release-management)
10. [Compliance and Governance](#compliance-and-governance)

## 🚀 Prerequisites

### Required Tools
- GitHub account with appropriate permissions
- GitHub CLI (gh) installed
- Git configured on your local machine
- Google Cloud account and project
- Docker Hub account (optional)

### Initial Setup
```bash
# Install GitHub CLI
# macOS
brew install gh

# Ubuntu/Debian
sudo apt install gh

# Windows
# Download from https://cli.github.com/

# Authenticate with GitHub
gh auth login

# Verify installation
gh --version
```

## 🏗️ Repository Initialization

### 1. Create Repository Structure

```bash
# Initialize local repository
git init
git add .
git commit -m "Initial commit: RaptorFlow project setup"

# Create GitHub repository
gh repo create RHUDHRESH/Raptorflow_v1 \
  --public \
  --description "AI-powered marketing automation platform" \
  --source=. \
  --remote=origin \
  --push
```

### 2. Configure Repository Settings

#### Basic Settings
```bash
# Set repository topics
gh repo edit RHUDHRESH/Raptorflow_v1 \
  --add-topic "ai" \
  --add-topic "marketing" \
  --add-topic "automation" \
  --add-topic "fastapi" \
  --add-topic "nextjs" \
  --add-topic "cloud-run"

# Set default branch to main
gh repo edit RHUDHRESH/Raptorflow_v1 --default-branch main

# Enable issues and PR templates
gh repo edit RHUDHRESH/Raptorflow_v1 --enable-issues
gh repo edit RHUDHRESH/Raptorflow_v1 --enable-discussions
```

### 3. Create Essential Files

#### README.md Enhancement
```bash
# Create comprehensive README
cat > README.md << 'EOF'
# RaptorFlow: AI-Powered Marketing Automation Platform

[![CI/CD Pipeline](https://github.com/RHUDHRESH/Raptorflow_v1/actions/workflows/enhanced-ci.yml/badge.svg)](https://github.com/RHUDHRESH/Raptorflow_v1/actions/workflows/enhanced-ci.yml)
[![Deployment](https://github.com/RHUDHRESH/Raptorflow_v1/actions/workflows/enhanced-cd.yml/badge.svg)](https://github.com/RHUDHRESH/Raptorflow_v1/actions/workflows/enhanced-cd.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Security](https://img.shields.io/badge/security-checked-brightgreen)](SECURITY.md)

## 🚀 Overview

RaptorFlow is an advanced AI-powered marketing automation platform that helps businesses create, optimize, and scale their marketing efforts through intelligent content generation, strategic positioning, and automated workflows.

## ✨ Key Features

- **AI Content Generation**: Advanced content creation using multiple AI models
- **Strategic Positioning**: Intelligent market positioning analysis
- **Automated Workflows**: Streamlined marketing automation
- **Real-time Analytics**: Comprehensive performance monitoring
- **Multi-channel Integration**: Support for various marketing channels

## 🏗️ Architecture

- **Backend**: FastAPI with Python 3.11
- **Frontend**: Next.js 14 with TypeScript
- **Database**: Supabase (PostgreSQL)
- **Deployment**: Google Cloud Run
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker and Docker Compose
- Google Cloud account

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/RHUDHRESH/Raptorflow_v1.git
   cd Raptorflow_v1
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your API keys
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📚 Documentation

- [Architecture Overview](docs/01-architecture.md)
- [Local Development Setup](docs/02-setup-local.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Security Documentation](SECURITY.md)
- [API Documentation](API_ENDPOINTS_COMPLETE.md)

## 🔧 Development

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Testing
```bash
# Backend tests
cd backend && python -m pytest

# Frontend tests
cd frontend && npm test
```

## 🚀 Deployment

### Automated Deployment
- **Staging**: Automatically deployed on push to `main` branch
- **Production**: Deployed on tag push (v*.*.*)

### Manual Deployment
```bash
# Deploy to staging
./deploy.sh staging

# Deploy to production
./deploy.sh production
```

## 🔐 Security

- All secrets are stored in GitHub Secrets
- Environment variables are never committed
- Regular security scans with GitHub Advanced Security
- Dependency vulnerability scanning
- Code scanning with CodeQL

## 📊 Monitoring

- Application metrics via Prometheus
- Log aggregation with Google Cloud Logging
- Performance monitoring with Cloud Monitoring
- Health checks and alerting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📧 Email: support@raptorflow.com
- 💬 Discord: [Join our Discord](https://discord.gg/raptorflow)
- 📖 Documentation: [docs.raptorflow.com](https://docs.raptorflow.com)

## 🙏 Acknowledgments

- Thanks to all contributors who have helped build RaptorFlow
- Special thanks to our beta testers and early adopters
EOF
```

#### Contributing Guidelines
```bash
mkdir -p .github
cat > .github/CONTRIBUTING.md << 'EOF'
# Contributing to RaptorFlow

We love your input! We want to make contributing to RaptorFlow as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## Pull Requests

Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Any contributions you make will be under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using GitHub's issue tracker

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/RHUDHRESH/Raptorflow_v1/issues).

## Write bug reports with detail, background, and example logs

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Development Setup

1. Fork and clone the repository
2. Set up your development environment as described in README
3. Create a new branch: `git checkout -b your-branch-name`
4. Make your changes
5. Run tests: `npm test` (frontend) and `pytest` (backend)
6. Commit your changes: `git commit -m 'Add some feature'`
7. Push to the branch: `git push origin your-branch-name`
8. Submit a pull request

## License

By contributing, you agree that your contributions will be licensed under its MIT License.
EOF
```

#### Issue Templates
```bash
mkdir -p .github/ISSUE_TEMPLATE

# Bug Report Template
cat > .github/ISSUE_TEMPLATE/bug_report.md << 'EOF'
---
name: Bug Report
about: Create a report to help us improve
title: ''
labels: bug
assignees: ''
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
- OS: [e.g. Windows 10, macOS 12.0]
- Browser: [e.g. Chrome, Firefox]
- Version: [e.g. 22.0.1]

**Additional context**
Add any other context about the problem here.
EOF

# Feature Request Template
cat > .github/ISSUE_TEMPLATE/feature_request.md << 'EOF'
---
name: Feature Request
about: Suggest an idea for this project
title: ''
labels: enhancement
assignees: ''
---

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
EOF
```

## 🔒 Branch Protection Rules

### Configure Main Branch Protection

```bash
# Using GitHub CLI
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["ci/ci"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":2,"dismiss_stale_reviews":true,"require_code_owner_reviews":true}' \
  --field restrictions=null
```

### Protection Rules Configuration

1. **Required Status Checks**
   - `ci/ci` (CI pipeline must pass)
   - `security/sast` (Security scanning)
   - `license/cla` (CLA if required)

2. **Pull Request Requirements**
   - At least 2 approving reviews
   - Dismiss stale PR approvals when new commits are pushed
   - Require review from Code Owners
   - Require up-to-date branches before merging

3. **Branch Restrictions**
   - Prevent force pushes to main
   - Prevent deletions of main branch
   - Enforce admin restrictions

## 🔑 Required Secrets

### GitHub Secrets Setup

```bash
# Set up Google Cloud secrets
gh secret set GCP_PROJECT_ID --body "your-gcp-project-id"
gh secret set GCP_SA_KEY --body "$(cat path/to/service-account-key.json)"

# Set up API secrets
gh secret set OPENAI_API_KEY --body "your-openai-api-key"
gh secret set GEMINI_API_KEY --body "your-gemini-api-key"
gh secret set PERPLEXITY_API_KEY --body "your-perplexity-api-key"

# Set up payment secrets
gh secret set RAZORPAY_KEY_ID --body "your-razorpay-key-id"
gh secret set RAZORPAY_KEY_SECRET --body "your-razorpay-key-secret"

# Set up notification secrets
gh secret set SLACK_WEBHOOK --body "your-slack-webhook-url"

# Set up database secrets
gh secret set SUPABASE_URL --body "your-supabase-url"
gh secret set SUPABASE_KEY --body "your-supabase-anon-key"

# Set up environment URLs
gh secret set STAGING_BACKEND_URL --body "https://raptorflow-backend-staging-xxxxx.a.run.app"
gh secret set PRODUCTION_BACKEND_URL --body "https://raptorflow-backend-xxxxx.a.run.app"
```

### Environment-Specific Secrets

#### Development Environment
- `DEV_OPENAI_API_KEY`
- `DEV_SUPABASE_URL`
- `DEV_SUPABASE_KEY`

#### Staging Environment
- `STAGING_OPENAI_API_KEY`
- `STAGING_SUPABASE_URL`
- `STAGING_SUPABASE_KEY`

#### Production Environment
- `PROD_OPENAI_API_KEY`
- `PROD_SUPABASE_URL`
- `PROD_SUPABASE_KEY`

## 👥 Team and Access Management

### Create Teams

```bash
# Create development team
gh api orgs/RHUDHRESH/teams --method POST \
  --field name='raptorflow-developers' \
  --field description='RaptorFlow Development Team' \
  --field privacy='closed'

# Create admin team
gh api orgs/RHUDHRESH/teams --method POST \
  --field name='raptorflow-admins' \
  --field description='RaptorFlow Admin Team' \
  --field privacy='closed'
```

### Assign Repository Permissions

```bash
# Add teams to repository
gh api repos/RHUDHRESH/Raptorflow_v1/teams/raptorflow-developers --method PUT \
  --field permission='write'

gh api repos/RHUDHRESH/Raptorflow_v1/teams/raptorflow-admins --method PUT \
  --field permission='admin'
```

### Permission Levels

| Role | Permissions | Description |
|------|-------------|-------------|
| Admin | Full control | Manage settings, teams, and billing |
| Maintainer | Write + admin repo | Manage repository settings |
| Developer | Write | Push code, create PRs, manage issues |
| Reporter | Read | View code, create issues, comment |

## 🛡️ Security Settings

### Enable GitHub Advanced Security

```bash
# Enable security features
gh api repos/RHUDHRESH/Raptorflow_v1/security-and-analysis --method PUT \
  --field 'advanced_security={"status":"enabled"}' \
  --field 'secret_scanning={"status":"enabled"}' \
  --field 'secret_scanning_push_protection={"status":"enabled"}' \
  --field 'dependabot_security_updates={"status":"enabled"}'
```

### Security Policies

1. **Secret Scanning**
   - Enable secret scanning for all commits
   - Enable push protection for secrets
   - Custom patterns for API keys and tokens

2. **Dependency Scanning**
   - Enable Dependabot alerts
   - Automated security updates
   - Weekly vulnerability reports

3. **Code Scanning**
   - Enable CodeQL analysis
   - Custom security rules
   - SARIF upload for third-party tools

### Security Configuration Files

```bash
# Create Dependabot configuration
cat > .github/dependabot.yml << 'EOF'
version: 2
updates:
  # Monitor backend dependencies
  - package-ecosystem: "pip"
    directory: "/backend"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    open-pull-requests-limit: 5
    reviewers:
      - "security-team"
    assignees:
      - "security-team"

  # Monitor frontend dependencies
  - package-ecosystem: "npm"
    directory: "/frontend"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    open-pull-requests-limit: 5
    reviewers:
      - "frontend-team"
    assignees:
      - "frontend-team"

  # Monitor GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    open-pull-requests-limit: 3
    reviewers:
      - "devops-team"
EOF
```

## 🔗 Integrations and Webhooks

### Set Up Webhooks

```bash
# Create webhook for CI/CD notifications
gh api repos/RHUDHRESH/Raptorflow_v1/hooks --method POST \
  --field name='web' \
  --field active=true \
  --field events='["push","pull_request","release"]' \
  --field config='{"url":"https://your-ci-cd-webhook-url","content_type":"json"}'
```

### Required Integrations

1. **Google Cloud Platform**
   - Container Registry access
   - Cloud Run deployment
   - Monitoring integration

2. **Slack**
   - Build notifications
   - Deployment alerts
   - Security notifications

3. **SonarCloud** (Optional)
   - Code quality analysis
   - Technical debt tracking
   - Security hotspot detection

4. **Snyk** (Optional)
   - Vulnerability scanning
   - License compliance
   - Dependency monitoring

## 📋 Issue and Project Management

### Create Project Board

```bash
# Create project board
gh api orgs/RHUDHRESH/projects --method POST \
  --field name='RaptorFlow Development' \
  --field body='Main development board for RaptorFlow project'
```

### Issue Labels

```bash
# Create custom labels
gh label create "bug" --color "d73a4a" --description "Something isn't working"
gh label create "enhancement" --color "a2eeef" --description "New feature or request"
gh label create "documentation" --color "0075ca" --description "Improvements or additions to documentation"
gh label create "good first issue" --color "7057ff" --description "Good for newcomers"
gh label create "help wanted" --color "008672" --description "Extra attention is needed"
gh label create "security" --color "ee0701" --description "Security related issues"
gh label create "performance" --color "1d76db" --description "Performance related issues"
gh label create "urgent" --color "e11c21" --description "Urgent issues requiring immediate attention"
```

### Milestones

```bash
# Create milestones
gh api repos/RHUDHRESH/Raptorflow_v1/milestones --method POST \
  --field title='v1.0.0 - Initial Release' \
  --field description='First stable release of RaptorFlow' \
  --field due_on='2024-12-31T23:59:59Z'

gh api repos/RHUDHRESH/Raptorflow_v1/milestones --method POST \
  --field title='v1.1.0 - Enhanced Features' \
  --field description='Feature enhancements and improvements' \
  --field due_on='2025-01-31T23:59:59Z'
```

## 🚀 Release Management

### Semantic Versioning

Follow [Semantic Versioning](https://semver.org/) for releases:

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Process

1. **Create Release Branch**
   ```bash
   git checkout -b release/v1.0.0
   ```

2. **Update Version Numbers**
   - Update `package.json` version
   - Update backend version in `__init__.py`
   - Update changelog

3. **Create Release Tag**
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

4. **Create GitHub Release**
   ```bash
   gh release create v1.0.0 \
     --title "RaptorFlow v1.0.0" \
     --notes "Initial stable release of RaptorFlow" \
     --generate-notes
   ```

### Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Security scan completed
- [ ] Performance tests passed
- [ ] Staging deployment verified
- [ ] Rollback plan documented

## 📊 Compliance and Governance

### Code of Conduct

```bash
cat > CODE_OF_CONDUCT.md << 'EOF'
# Contributor Covenant Code of Conduct

## Our Pledge

We as members, contributors, and leaders pledge to make participation in our
community a harassment-free experience for everyone, regardless of age, body
size, visible or invisible disability, ethnicity, sex characteristics, gender
identity and expression, level of experience, education, socio-economic status,
nationality, personal appearance, race, religion, or sexual identity
and orientation.

## Our Standards

Examples of behavior that contributes to creating a positive environment
include:

* Using welcoming and inclusive language
* Being respectful of differing viewpoints and experiences
* Gracefully accepting constructive criticism
* Focusing on what is best for the community
* Showing empathy towards other community members

Examples of unacceptable behavior by participants include:

* The use of sexualized language or imagery and unwelcome sexual attention or
  advances
* Trolling, insulting/derogatory comments, and personal or political attacks
* Public or private harassment
* Publishing others' private information, such as a physical or electronic
  address, without explicit permission
* Other conduct which could reasonably be considered inappropriate in a
  professional setting

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported by contacting the project team at support@raptorflow.com. All
complaints will be reviewed and investigated and will result in a response that
is deemed necessary and appropriate to the circumstances. The project team is
obligated to maintain confidentiality with regard to the reporter of an incident.
Further details of specific enforcement policies may be posted separately.

Project maintainers who do not follow or enforce the Code of Conduct in good
faith may face temporary or permanent repercussions as determined by other
members of the project's leadership.
EOF
```

### License Management

```bash
# Add license file
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2024 RaptorFlow

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
```

### Documentation Standards

1. **API Documentation**: All endpoints documented with OpenAPI/Swagger
2. **Code Comments**: Critical business logic documented
3. **README Updates**: Keep README current with latest features
4. **Changelog**: Maintain detailed changelog for all releases

## 🔍 Monitoring and Maintenance

### Repository Health Monitoring

```bash
# Check repository health
gh repo view RHUDHRESH/Raptorflow_v1 --json name,description,isPrivate,defaultBranch,updatedAt

# Check recent activity
gh api repos/RHUDHRESH/Raptorflow_v1/activity

# Check issues and PRs
gh issue list --repo RHUDHRESH/Raptorflow_v1 --state open
gh pr list --repo RHUDHRESH/Raptorflow_v1 --state open
```

### Regular Maintenance Tasks

1. **Weekly**
   - Review and merge PRs
   - Update dependencies
   - Check security alerts
   - Review issue backlog

2. **Monthly**
   - Repository health check
   - Team permissions review
   - Documentation updates
   - Performance review

3. **Quarterly**
   - Security audit
   - License compliance check
   - Contribution statistics
   - Roadmap review

## 🚨 Emergency Procedures

### Security Incident Response

1. **Immediate Actions**
   - Identify affected repositories
   - Rotate exposed credentials
   - Assess impact scope

2. **Communication**
   - Notify security team
   - Update stakeholders
   - Document incident

3. **Remediation**
   - Patch vulnerabilities
   - Update security policies
   - Conduct post-mortem

### Rollback Procedures

```bash
# Emergency rollback to previous stable version
git checkout v1.0.0
git push -f origin main

# Redeploy stable version
./deploy.sh production --force
```

## 📞 Support and Contact

### Getting Help

- **Documentation**: [docs.raptorflow.com](https://docs.raptorflow.com)
- **Issues**: [GitHub Issues](https://github.com/RHUDHRESH/Raptorflow_v1/issues)
- **Discussions**: [GitHub Discussions](https://github.com/RHUDHRESH/Raptorflow_v1/discussions)
- **Email**: support@raptorflow.com

### Team Contacts

- **Project Lead**: [Project Lead Email]
- **DevOps**: [DevOps Team Email]
- **Security**: [Security Team Email]

---

This guide provides a comprehensive foundation for setting up and maintaining a secure, efficient GitHub repository for the RaptorFlow project. Regular updates and reviews are recommended to ensure the repository remains secure and follows best practices.
