# Mindly Chairman's Council - Deployment Guide

## Production Deployment to Google Cloud Run

This guide explains how to deploy the Mindly Chairman's Council system to Google Cloud Run for production use.

## Prerequisites

1. **Google Cloud Account**: Active GCP project (mindly-health)
2. **GitHub Repository**: mindlyhealthin/mindly-chairmans-council
3. **Required APIs Enabled**:
   - Cloud Run API
   - Cloud Build API
   - Container Registry API
   - Cloud Logging API

4. **Environment Variables**: Set up the following secrets in GitHub:
   - `GCP_SA_KEY`: Service account key JSON (base64 encoded)
   - `OPENROUTER_API_KEY`: Valid OpenRouter API key

## Setup Steps

### Step 1: Create a GCP Service Account

```bash
gcloud iam service-accounts create mindly-chairman-council-sa \
  --display-name="Mindly Chairman's Council Service Account"

# Grant Cloud Run Admin role
gcloud projects add-iam-policy-binding mindly-health \
  --member="serviceAccount:mindly-chairman-council-sa@mindly-health.iam.gserviceaccount.com" \
  --role="roles/run.admin"

# Grant Container Registry Service Agent role
gcloud projects add-iam-policy-binding mindly-health \
  --member="serviceAccount:mindly-chairman-council-sa@mindly-health.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"
```

### Step 2: Create and Download Service Account Key

```bash
gcloud iam service-accounts keys create key.json \
  --iam-account=mindly-chairman-council-sa@mindly-health.iam.gserviceaccount.com

# Encode as base64 for GitHub secret
cat key.json | base64
```

### Step 3: Add GitHub Secrets

1. Go to GitHub Repository Settings > Secrets and variables > Actions
2. Add `GCP_SA_KEY` with the base64-encoded service account key
3. Add `OPENROUTER_API_KEY` with your OpenRouter API key

### Step 4: Deploy

#### Automated Deployment (Recommended)

Simply push to main branch:

```bash
git add .
git commit -m "Production deployment"
git push origin main
```

The GitHub Actions workflow `.github/workflows/deploy-cloud-run.yml` will automatically:
1. Build the Docker image
2. Push to Google Container Registry
3. Deploy to Cloud Run
4. Run health checks

#### Manual Deployment

```bash
# Build Docker image
docker build -t gcr.io/mindly-health/mindly-chairmans-council:latest .

# Push to GCR
gcloud auth configure-docker
docker push gcr.io/mindly-health/mindly-chairmans-council:latest

# Deploy to Cloud Run
gcloud run deploy mindly-chairmans-council \
  --image gcr.io/mindly-health/mindly-chairmans-council:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "OPENROUTER_API_KEY=your-key-here,FIREBASE_PROJECT_ID=mindly-health" \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60
```

## Post-Deployment Configuration

### Enable Authentication (Optional)

If you want to require authentication:

```bash
gcloud run services update mindly-chairmans-council \
  --no-allow-unauthenticated \
  --region us-central1
```

### Set Up Custom Domain

```bash
gcloud run domain-mappings create \
  --service=mindly-chairmans-council \
  --domain=api.mindly.health \
  --region=us-central1
```

## Monitoring & Logging

### View Logs

```bash
gcloud run logs read mindly-chairmans-council \
  --region=us-central1 \
  --limit=100 \
  --follow
```

### Monitor Performance

1. Go to Cloud Console > Cloud Run > mindly-chairmans-council
2. Check Metrics tab for:
   - Request count
   - Latency
   - Error rate
   - Instance count

## Components Deployed

### Backend API
- **Endpoint**: /api/council/query (POST)
- **Timeout**: 60 seconds
- **Memory**: 512MB
- **Authentication**: API Key (Bearer token)

### Key Features

1. **Firebase Firestore Integration**
   - Query persistence
   - Multi-tenant data isolation
   - Audit logging

2. **Healthcare Domain Support**
   - Psychiatry-specific models
   - HIPAA compliance settings
   - Clinical guidelines

3. **Authentication & Authorization**
   - Multi-tenant support
   - Role-based access control (RBAC)
   - Rate limiting per tenant

4. **Multi-Model AI Council**
   - OpenRouter integration
   - Model voting mechanism
   - Chairman consensus logic

## API Usage

### Authentication

```bash
curl -X POST https://mindly-chairmans-council.run.app/api/council/query \
  -H "Authorization: Bearer sk-chairmancouncil-{tenant_id}-{user_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What screening tools for depression?",
    "domain": "psychiatry",
    "context": {"patient_age": 35, "symptoms": [...]}
  }'
```

## Scaling & Performance

- **Auto-scaling**: Enabled (0-100 instances)
- **Max requests per instance**: 80
- **Concurrent requests**: Up to 1000
- **Memory per instance**: 512MB (adjustable)

## Troubleshooting

### Service Won't Deploy

1. Check service account permissions
2. Verify Dockerfile builds locally: `docker build .`
3. Check Cloud Build logs: `gcloud builds list`

### High Latency

1. Check OpenRouter API status
2. Monitor Firestore operations
3. Increase memory/CPU allocation

### Authentication Errors

1. Verify API key format: `sk-chairmancouncil-{tenant_id}-{user_id}`
2. Check tenant configuration in Firestore
3. Verify JWT token expiration

## Cost Optimization

- Cloud Run pricing: $0.00002400 per vCPU-second
- Estimated monthly cost for 1000 requests/day: ~$10-20
- Use min instances = 0 to reduce idle costs

## Next Steps

1. Set up monitoring alerts
2. Configure backup strategy for Firestore
3. Implement rate limiting per tenant
4. Enable HIPAA compliance features
5. Set up CI/CD for staging environment