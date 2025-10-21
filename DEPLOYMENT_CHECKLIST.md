# RaptorFlow GCP Deployment Checklist

## ✅ Pre-Deployment Checklist

### GCP Setup
- [ ] GCP account created with billing enabled
- [ ] GCP project created and noted (PROJECT_ID: _____________)
- [ ] gcloud CLI installed and authenticated
- [ ] Docker installed on local machine

### Enable GCP APIs
```bash
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### Set Up Secrets
Run the interactive script:
```bash
./setup-gcp-secrets.sh
```

Or manually create each secret:
- [ ] supabase-url
- [ ] supabase-key
- [ ] supabase-service-key
- [ ] openai-api-key
- [ ] gemini-api-key
- [ ] perplexity-api-key
- [ ] razorpay-key-id
- [ ] razorpay-key-secret
- [ ] razorpay-webhook-secret
- [ ] jwt-secret-key
- [ ] encryption-key

## GitHub Actions Setup

### Create Service Account
```bash
gcloud iam service-accounts create github-actions --display-name="GitHub Actions"
```

### Grant Permissions
```bash
PROJECT_ID=$(gcloud config get-value project)

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Create and Download Key
```bash
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions@$PROJECT_ID.iam.gserviceaccount.com
```

### Add GitHub Secrets
Go to: Repository → Settings → Secrets and variables → Actions

- [ ] `GCP_PROJECT_ID` = your-project-id
- [ ] `GCP_SA_KEY` = (paste entire contents of github-actions-key.json)

## Deployment Options

### Option 1: Manual Deployment via Cloud Build
```bash
gcloud builds submit --config cloudbuild.yaml
```

### Option 2: GitHub Actions
- [ ] Push to main branch
- [ ] Or manually trigger workflow in Actions tab

## Post-Deployment Verification

### Get Service URLs
```bash
# Backend
gcloud run services describe raptorflow-backend --region asia-south1 --format='value(status.url)'

# Frontend  
gcloud run services describe raptorflow-frontend --region asia-south1 --format='value(status.url)'
```

### Test Endpoints
- [ ] Backend health: `curl https://BACKEND_URL/health`
- [ ] Frontend accessible in browser
- [ ] API calls from frontend to backend work

## Monitoring & Logs

### View Logs
```bash
# Backend logs
gcloud run services logs read raptorflow-backend --region asia-south1 --limit 50

# Frontend logs
gcloud run services logs read raptorflow-frontend --region asia-south1 --limit 50
```

### Monitor Services
```bash
gcloud run services describe raptorflow-backend --region asia-south1
gcloud run services describe raptorflow-frontend --region asia-south1
```

## Cost Management

- [ ] Set up billing alerts in GCP Console
- [ ] Review Cloud Run pricing
- [ ] Consider setting min-instances=0 for non-production

## Security Verification

- [ ] All secrets in Secret Manager (not in code)
- [ ] .env files not committed to git
- [ ] Service accounts follow least privilege
- [ ] CORS properly configured
- [ ] Health checks working

## Optional Enhancements

- [ ] Configure custom domain
- [ ] Set up Cloud CDN
- [ ] Enable Cloud Armor
- [ ] Configure monitoring alerts
- [ ] Set up Cloud Logging
- [ ] Implement backup strategy

---

**Ready for deployment!** Follow the steps above in order.

For detailed instructions, see: `DEPLOY_TO_GCP.md`
For all changes made, see: `GCP_DEPLOYMENT_CHANGES.md`
