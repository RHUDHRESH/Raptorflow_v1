# CI/CD Quality Gates Setup

This document describes the automated quality gates configured for RaptorFlow ADAPT.

## Overview

Quality gates run automatically on every pull request to ensure code quality, type safety, and test coverage before merging to main.

## GitHub Actions Workflow

The project uses GitHub Actions for CI/CD. The workflow is defined in `.github/workflows/quality-gates.yml`.

### Jobs

#### 1. Backend Quality Checks
- **Linting**: Ruff (replaces flake8, black, and isort)
- **Type Checking**: mypy
- **Testing**: pytest with coverage reporting
- **Security**: Bandit and Safety checks

#### 2. Frontend Quality Checks
- **Type Checking**: TypeScript compiler (tsc --noEmit)
- **Linting**: ESLint with Next.js and TypeScript rules
- **Formatting**: Prettier
- **Unit Tests**: Jest with coverage reporting

#### 3. E2E Tests
- **Framework**: Playwright
- **Browser**: Chromium
- **Reports**: Uploaded as artifacts for debugging

#### 4. Security Scanning
- **Python**: Bandit (code scanning) and Safety (dependency scanning)
- **Reports**: Generated and uploaded as artifacts

## Local Development Commands

### Backend (Python)

```bash
cd backend

# Install dev dependencies
pip install -r requirements-dev.txt

# Run linter
ruff check .

# Fix auto-fixable lint issues
ruff check --fix .

# Check formatting
ruff format --check .

# Format code
ruff format .

# Run type checking
mypy . --config-file=../pyproject.toml

# Run tests
pytest

# Run tests with coverage
pytest --cov=. --cov-report=html --cov-report=term-missing

# Security checks
bandit -r .
safety check
```

### Frontend (TypeScript/React)

```bash
cd frontend

# Install dependencies
npm install

# Type check
npm run type-check

# Lint
npm run lint

# Fix linting issues
npm run lint:fix

# Check formatting
npm run format:check

# Format code
npm run format:write

# Run unit tests
npm test

# Run tests with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e

# Run E2E tests with UI
npm run test:e2e:ui

# Run all quality checks
npm run quality
```

## Configuration Files

### Backend

- **`backend/pyproject.toml`**: Configuration for ruff, mypy, pytest, and coverage
- **`backend/requirements-dev.txt`**: Development dependencies

### Frontend

- **`frontend/.eslintrc.json`**: ESLint configuration
- **`frontend/.prettierrc.json`**: Prettier configuration
- **`frontend/tsconfig.json`**: TypeScript configuration
- **`frontend/jest.config.js`**: Jest configuration
- **`frontend/playwright.config.ts`**: Playwright configuration

## Google Cloud Build Integration

You have two options for integrating quality gates with Google Cloud Build:

### Option 1: GitHub Triggers (Recommended)

Set up Cloud Build triggers that respond to GitHub events:

1. **Connect GitHub Repository**:
   ```bash
   # In Google Cloud Console
   # Navigate to Cloud Build > Triggers > Connect Repository
   # Select your GitHub repository
   ```

2. **Create PR Quality Gate Trigger**:
   - **Name**: `pr-quality-checks`
   - **Event**: Pull request
   - **Source**: Your GitHub repository
   - **Branch**: `^main$` (regex)
   - **Build configuration**: Cloud Build configuration file
   - **File location**: `.cloudbuild/quality-gates.yaml`

3. **Create the Cloud Build config** (`.cloudbuild/quality-gates.yaml`):
   ```yaml
   steps:
     # Backend checks
     - name: 'python:3.10'
       dir: 'backend'
       entrypoint: bash
       args:
         - '-c'
         - |
           pip install -r requirements.txt -r requirements-dev.txt
           ruff check .
           ruff format --check .
           mypy . --config-file=../pyproject.toml
           pytest --cov=. --cov-report=term-missing

     # Frontend checks
     - name: 'node:20'
       dir: 'frontend'
       entrypoint: bash
       args:
         - '-c'
         - |
           npm ci
           npm run type-check
           npm run lint
           npm run format:check
           npm run test:coverage

     # Security scanning
     - name: 'python:3.10'
       dir: 'backend'
       entrypoint: bash
       args:
         - '-c'
         - |
           pip install -r requirements-dev.txt
           bandit -r . || true
           safety check || true

   options:
     logging: CLOUD_LOGGING_ONLY
     machineType: 'E2_HIGHCPU_8'
   ```

### Option 2: Use GitHub Actions + Cloud Build for Deployment

Keep quality gates in GitHub Actions (already configured) and use Cloud Build only for deployment:

1. **Quality Gates**: Run in GitHub Actions (fast, free for public repos)
2. **Deployment**: Use existing `cloudbuild.yaml` for deployment to Cloud Run

**Deployment Trigger**:
- **Name**: `deploy-to-production`
- **Event**: Push to branch
- **Branch**: `^main$`
- **Build configuration**: `cloudbuild.yaml`
- **Substitution variables**:
  - `_SUPABASE_URL`: Your Supabase URL
  - `_SUPABASE_KEY`: Your Supabase key
  - `_BACKEND_URL`: Backend service URL

### Option 3: Pre-commit Hooks (Local Only)

For local quality enforcement, set up pre-commit hooks:

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml (see below)

# Install hooks
pre-commit install
```

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.1.0
    hooks:
      - id: prettier
        files: \\.(ts|tsx|js|jsx|json|css|md)$
```

## Setting Up GitHub Secrets

For the GitHub Actions workflow to work properly, configure these secrets in your GitHub repository:

1. Navigate to: **Settings > Secrets and variables > Actions**
2. Add the following secrets:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase service role key

## Branch Protection Rules

Recommended branch protection settings for `main`:

1. Navigate to: **Settings > Branches > Add rule**
2. Configure:
   - **Branch name pattern**: `main`
   - **Require a pull request before merging**: ✓
   - **Require approvals**: 1
   - **Require status checks to pass before merging**: ✓
     - Select all quality gate jobs:
       - `Backend Quality Checks`
       - `Frontend Quality Checks`
       - `Frontend E2E Tests`
       - `Security Scanning`
   - **Require conversation resolution before merging**: ✓
   - **Do not allow bypassing the above settings**: ✓

## Monitoring and Troubleshooting

### GitHub Actions

- View workflow runs: **Actions tab** in your GitHub repository
- Click on any workflow run to see detailed logs
- Download artifacts (test reports, coverage) from workflow run page

### Cloud Build

```bash
# List recent builds
gcloud builds list --limit=10

# View build logs
gcloud builds log <BUILD_ID>

# View build details
gcloud builds describe <BUILD_ID>
```

### Common Issues

#### mypy Type Errors
- Initially set to `continue-on-error: true` in GitHub Actions
- Fix incrementally and remove this flag when ready
- Use `# type: ignore` comments sparingly for legitimate cases

#### Test Failures
- Check test logs in GitHub Actions
- Run tests locally with `pytest -v` or `npm test` for debugging
- Ensure all environment variables are set

#### Coverage Drops
- Review coverage report in artifacts
- Add tests for uncovered code paths
- Set coverage thresholds in `pyproject.toml` or `jest.config.js`

## Metrics and Reporting

### Code Coverage

- **Backend**: Coverage reports in HTML format at `backend/htmlcov/`
- **Frontend**: Coverage reports at `frontend/coverage/`
- **Codecov Integration**: Optional, add `CODECOV_TOKEN` secret for tracking

### Quality Metrics Dashboard

Consider integrating:
- **Codecov**: Code coverage tracking
- **SonarCloud**: Code quality and security
- **Snyk**: Dependency vulnerability scanning

## Next Steps

1. **Install dependencies**:
   ```bash
   # Backend
   cd backend && pip install -r requirements-dev.txt

   # Frontend
   cd frontend && npm install
   ```

2. **Run quality checks locally** to ensure everything passes

3. **Push to GitHub** to trigger the workflow

4. **Set up branch protection** rules as described above

5. **Configure Cloud Build triggers** (optional) for deployment

6. **Monitor first PR** to ensure all checks pass

## Resources

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [ESLint Documentation](https://eslint.org/)
- [Playwright Documentation](https://playwright.dev/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Google Cloud Build Documentation](https://cloud.google.com/build/docs)
