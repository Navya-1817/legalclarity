# Google Cloud Run Deployment Guide

## Why Google Cloud Run is Better for Your App:

✅ **Free Tier**: 2 million requests per month free
✅ **Easy Database**: Cloud SQL or Firestore integration
✅ **Native Google Services**: Perfect for your Vision API and Vertex AI
✅ **Automatic Scaling**: Scales to zero when not in use
✅ **Simple Deployment**: One command deployment

## Prerequisites:

1. **Google Cloud Account**: Already have one (you have the service account)
2. **Google Cloud CLI**: Install from https://cloud.google.com/sdk/docs/install
3. **Docker**: Install Docker Desktop

## Step-by-Step Deployment:

### 1. Install Google Cloud CLI
```bash
# Download and install from: https://cloud.google.com/sdk/docs/install
```

### 2. Login and Set Project
```bash
gcloud auth login
gcloud config set project shining-sign-468814-i2
gcloud auth configure-docker
```

### 3. Enable Required APIs
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable vision.googleapis.com
gcloud services enable texttospeech.googleapis.com
```

### 4. Set Environment Variables
```bash
# Create a .env file (already exists, just verify):
FLASK_SECRET_KEY=your-secret-key
GCP_PROJECT_ID=shining-sign-468814-i2
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json
```

### 5. Deploy to Cloud Run
```bash
# Build and deploy in one command:
gcloud run deploy legalclarity \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="FLASK_SECRET_KEY=your-secret-key-here" \
  --set-env-vars="GCP_PROJECT_ID=shining-sign-468814-i2"
```

## Alternative: One-Click Deploy

Create this file and run the deploy script:

### deploy.sh (or deploy.bat for Windows)
```bash
#!/bin/bash
echo "🚀 Deploying Legal Clarity to Google Cloud Run..."

# Build and deploy
gcloud run deploy legalclarity \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --max-instances=10 \
  --memory=512Mi \
  --cpu=1 \
  --timeout=300 \
  --set-env-vars="FLASK_SECRET_KEY=03728b70e22e821ffd0208bae0c80cc9534fe75ce67a5355b046e99dd086272e" \
  --set-env-vars="GCP_PROJECT_ID=shining-sign-468814-i2"

echo "✅ Deployment complete!"
echo "🌐 Your app will be available at the URL shown above"
```

## Benefits Over Vercel:

1. **No Serverless Limitations**: Full Flask app support
2. **Persistent Storage**: Can use Cloud SQL for database
3. **Better Google Integration**: Native support for all Google APIs
4. **More Control**: Full container environment
5. **Better Debugging**: Real logs and monitoring

## Cost:

- **Free Tier**: 2M requests/month, 180,000 GB-seconds/month
- **After Free**: ~$0.000024 per request
- **Your app will likely stay in free tier**

## Next Steps:

1. Install Google Cloud CLI
2. Run the deploy command
3. Your app will be live at: `https://legalclarity-xxx-uc.a.run.app`

Would you like me to help you set this up?
