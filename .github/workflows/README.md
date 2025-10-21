# GitHub Actions Workflows

## Quality Gates Workflow

The `quality-gates.yml` workflow runs automatically on:
- **Pull requests** to `main` or `develop` branches
- **Pushes** to `main` branch

### Jobs Overview

| Job | Description | Tools |
|-----|-------------|-------|
| **Backend Quality** | Python code quality checks | ruff, mypy, pytest |
| **Frontend Quality** | TypeScript/React code quality | tsc, eslint, prettier, jest |
| **Frontend E2E** | End-to-end testing | Playwright |
| **Security Scan** | Security vulnerability scanning | Bandit, Safety |

### Status Badges

Add these to your main README.md:

```markdown
![Quality Gates](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/Quality%20Gates/badge.svg)
```

### Requirements

**GitHub Secrets** (Settings > Secrets and variables > Actions):
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase service role key
- `CODECOV_TOKEN`: (Optional) For coverage tracking

### Local Testing

Before pushing, run these commands to catch issues early:

**Backend**:
```bash
cd backend
ruff check . && ruff format --check . && mypy . && pytest
```

**Frontend**:
```bash
cd frontend
npm run quality
```

### Troubleshooting

If checks fail:
1. Click on the failed job in the Actions tab
2. Review the error logs
3. Fix issues locally and push again
4. Tests must pass before merge is allowed

For more details, see [CI_CD_SETUP.md](../../CI_CD_SETUP.md)
