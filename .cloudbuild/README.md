# Cloud Build Configuration

This directory contains Google Cloud Build configuration files for running quality gates.

## Files

- **`quality-gates.yaml`**: Runs all quality checks (linting, type checking, tests, security)

## Setup Instructions

### 1. Connect Repository to Cloud Build

```bash
# Enable Cloud Build API
gcloud services enable cloudbuild.googleapis.com

# Connect your GitHub repository via the Cloud Console:
# https://console.cloud.google.com/cloud-build/triggers/connect
```

### 2. Create Quality Gates Trigger

**Via Console:**

1. Go to [Cloud Build Triggers](https://console.cloud.google.com/cloud-build/triggers)
2. Click "Create Trigger"
3. Configure:
   - **Name**: `pr-quality-checks`
   - **Event**: Pull request
   - **Source**: Your connected repository
   - **Base branch**: `^main$` (regex)
   - **Comment control**: Required (prevents spam)
   - **Build configuration**: Cloud Build configuration file
   - **Location**: `.cloudbuild/quality-gates.yaml`

**Via CLI:**

```bash
gcloud builds triggers create github \
  --name="pr-quality-checks" \
  --repo-name="YOUR_REPO" \
  --repo-owner="YOUR_GITHUB_USERNAME" \
  --pull-request-pattern="^main$" \
  --build-config=".cloudbuild/quality-gates.yaml" \
  --comment-control=COMMENTS_ENABLED \
  --substitutions=_SUPABASE_URL="YOUR_SUPABASE_URL",_SUPABASE_KEY="YOUR_SUPABASE_KEY"
```

### 3. Configure Substitution Variables

Add these substitution variables to your trigger:

| Variable | Description | Example |
|----------|-------------|---------|
| `_SUPABASE_URL` | Your Supabase project URL | `https://xxx.supabase.co` |
| `_SUPABASE_KEY` | Supabase service role key | `eyJ...` |
| `_BACKEND_URL` | Backend API URL for E2E tests | `http://localhost:8000` |
| `_ARTIFACTS_BUCKET` | GCS bucket for storing artifacts | `my-project-artifacts` |

### 4. Set Up Artifacts Storage (Optional)

Create a GCS bucket for storing test reports and coverage:

```bash
# Create bucket
gsutil mb -p YOUR_PROJECT_ID gs://your-artifacts-bucket

# Set lifecycle policy (optional - delete old reports after 30 days)
cat > lifecycle.json << EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 30}
      }
    ]
  }
}
EOF

gsutil lifecycle set lifecycle.json gs://your-artifacts-bucket
```

## Comparison: Cloud Build vs GitHub Actions

| Feature | Cloud Build | GitHub Actions |
|---------|-------------|----------------|
| **Speed** | Fast (GCP network) | Fast (GitHub infrastructure) |
| **Cost** | First 120 build-minutes/day free | Free for public repos, 2000 mins/month for private |
| **Integration** | Native GCP integration | Better GitHub integration |
| **Caching** | Manual setup required | Excellent built-in caching |
| **Secrets** | Secret Manager | GitHub Secrets |
| **Best for** | GCP-heavy workflows | GitHub-centric workflows |

## Recommended Approach

**Hybrid Model** (Best of Both Worlds):

1. **Quality Gates**: Use **GitHub Actions** (already configured in `.github/workflows/quality-gates.yml`)
   - Faster feedback on PRs
   - Better GitHub integration
   - Free for most use cases

2. **Deployment**: Use **Cloud Build** (your existing `cloudbuild.yaml`)
   - Only runs on merge to main
   - Native GCP service integration
   - Automatic deployment to Cloud Run

This way, you get:
- ✓ Fast quality checks on every PR (GitHub Actions)
- ✓ Seamless deployment to GCP (Cloud Build)
- ✓ Lower costs (fewer Cloud Build minutes used)
- ✓ Better developer experience

## Manual Trigger

Run quality checks manually:

```bash
# From repository root
gcloud builds submit \
  --config=.cloudbuild/quality-gates.yaml \
  --substitutions=_SUPABASE_URL="$SUPABASE_URL",_SUPABASE_KEY="$SUPABASE_KEY"
```

## Monitoring

View build history:

```bash
# List recent builds
gcloud builds list --limit=10

# View specific build
gcloud builds log <BUILD_ID>

# Follow build in real-time
gcloud builds log <BUILD_ID> --stream
```

## Troubleshooting

### Build Times Out

- Increase timeout in `quality-gates.yaml`:
  ```yaml
  timeout: '3600s'  # 60 minutes
  ```

### Out of Memory

- Use larger machine type:
  ```yaml
  options:
    machineType: 'E2_HIGHCPU_32'
  ```

### Slow npm install

- Consider using Cloud Build caching:
  ```yaml
  steps:
    - name: 'node:20'
      entrypoint: npm
      args: ['ci', '--cache', '.npm']
  ```

## Cost Optimization

1. **Use GitHub Actions for PRs** (free/cheap)
2. **Use Cloud Build only for deployments** (when needed)
3. **Enable artifact cleanup** (30-day lifecycle)
4. **Use appropriate machine types** (don't over-provision)

## Next Steps

1. ✓ Review the configuration files
2. ✓ Choose your CI/CD strategy (GitHub Actions, Cloud Build, or Hybrid)
3. ✓ Set up triggers if using Cloud Build
4. ✓ Configure secrets/substitution variables
5. ✓ Test with a sample PR

For more details, see [CI_CD_SETUP.md](../CI_CD_SETUP.md)
