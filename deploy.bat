@echo off
echo 🚀 Deploying Legal Clarity to Google Cloud Run...

REM Check if gcloud is installed
gcloud version >nul 2>&1
if errorlevel 1 (
    echo ❌ Google Cloud CLI not found. Please install from: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)

REM Deploy to Cloud Run
gcloud run deploy legalclarity ^
  --source . ^
  --platform managed ^
  --region us-central1 ^
  --allow-unauthenticated ^
  --max-instances=10 ^
  --memory=512Mi ^
  --cpu=1 ^
  --timeout=300 ^
  --set-env-vars="FLASK_SECRET_KEY=03728b70e22e821ffd0208bae0c80cc9534fe75ce67a5355b046e99dd086272e" ^
  --set-env-vars="GCP_PROJECT_ID=shining-sign-468814-i2"

if errorlevel 1 (
    echo ❌ Deployment failed!
    pause
    exit /b 1
)

echo ✅ Deployment complete!
echo 🌐 Your app is now live!
pause
