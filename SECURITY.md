# Security Policy

## Supported Versions

We actively support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

### How to Report

**Email**: security@raptorflow.com

**PGP Key**: Available at https://raptorflow.com/.well-known/pgp-key.txt

**What to Include**:
1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if any)
5. Your name/handle (for credit)

### Response Timeline

| Stage | Timeline |
|-------|----------|
| **Initial Response** | Within 24 hours |
| **Triage & Validation** | Within 3 business days |
| **Fix Development** | Depends on severity (see below) |
| **Patch Release** | Depends on severity |
| **Public Disclosure** | 90 days after patch (coordinated) |

### Severity Classification

| Severity | Examples | Fix Timeline |
|----------|----------|--------------|
| **Critical** | Remote code execution, authentication bypass, full data breach | 24-48 hours |
| **High** | Privilege escalation, SQL injection, payment bypass | 3-7 days |
| **Medium** | Limited data exposure, CSRF, XSS | 14-30 days |
| **Low** | Information disclosure, minor configuration issues | 30-90 days |

## Vulnerability Disclosure Process

1. **Report Submitted**: You email security@raptorflow.com
2. **Acknowledgment**: We confirm receipt within 24 hours
3. **Investigation**: We validate and assess severity (3 days)
4. **Fix Development**: We develop and test a patch
5. **Patch Release**: We release a security update
6. **Credit**: We credit you in release notes (unless you prefer anonymity)
7. **Public Disclosure**: We publicly disclose 90 days after patch (or sooner with your consent)

## Security Measures

### Infrastructure
- **HTTPS Only**: TLS 1.3, HSTS enabled
- **DDoS Protection**: Cloud Load Balancer with rate limiting
- **Network Isolation**: VPC with private subnets
- **Secret Management**: Cloud Secret Manager (no secrets in code)

### Application
- **Input Validation**: All inputs validated with Pydantic/Zod
- **Output Encoding**: Auto-escaping in React, parameterized queries
- **Authentication**: JWT with Supabase Auth, JWKS validation
- **Authorization**: RBAC with org-scoped permissions
- **Rate Limiting**: Per IP, per user, per org
- **Audit Logging**: All sensitive operations logged

### Data
- **Encryption at Rest**: Google Cloud SQL and Storage
- **Encryption in Transit**: TLS for all connections
- **Field-Level Encryption**: For extra-sensitive PII
- **Backups**: Daily automated backups, tested quarterly
- **Data Minimization**: Only collect necessary data

### Development
- **Dependency Scanning**: Dependabot, npm audit, Safety
- **Code Scanning**: CodeQL, Bandit, ESLint security rules
- **Container Scanning**: Trivy for vulnerabilities
- **Secret Scanning**: GitHub secret scanning enabled
- **Pre-Commit Hooks**: Linting and security checks

### Operations
- **Monitoring**: Real-time alerts for security events
- **Incident Response**: 24/7 on-call rotation
- **Access Reviews**: Quarterly IAM permission audits
- **Security Training**: Annual training for all engineers

## Bug Bounty Program

**Status**: Coming Soon (Q2 2025)

We plan to launch a public bug bounty program with rewards ranging from $100 to $10,000 based on severity.

**Early Reporter Bonus**: Report vulnerabilities before the program launches and receive 2x rewards retroactively!

## Security Hall of Fame

We thank the following security researchers for responsibly disclosing vulnerabilities:

*(None yet - be the first!)*

## Security Updates

Subscribe to security notifications:
- **GitHub Security Advisories**: Watch this repository
- **Email**: security-updates@raptorflow.com (coming soon)
- **RSS**: https://raptorflow.com/security.rss (coming soon)

## Compliance & Certifications

| Standard | Status | Last Audit |
|----------|--------|------------|
| **OWASP Top 10** | Compliant | 2025-01 |
| **GDPR** | Compliant | 2025-01 |
| **SOC 2** | Planned Q3 2025 | N/A |
| **ISO 27001** | Planned Q4 2025 | N/A |

## Breach Notification

In the unlikely event of a data breach:

**Within 24 hours**:
- Contain the breach
- Assess scope and impact
- Notify internal teams

**Within 72 hours**:
- Notify affected users (if PII compromised)
- Notify supervisory authority (GDPR requirement for EU users)
- Post public incident report

**Within 30 days**:
- Publish detailed post-mortem
- Implement remediation measures
- Update security controls

## Contact

**Security Team**: security@raptorflow.com
**General Support**: support@raptorflow.com
**Legal**: legal@raptorflow.com

## Acknowledgments

We use and appreciate these open-source security tools:
- [Dependabot](https://github.com/dependabot)
- [CodeQL](https://codeql.github.com/)
- [Trivy](https://github.com/aquasecurity/trivy)
- [Bandit](https://github.com/PyCQA/bandit)
- [Safety](https://github.com/pyupio/safety)

---

**Last Updated**: 2025-01-20
**Version**: 1.0.0
