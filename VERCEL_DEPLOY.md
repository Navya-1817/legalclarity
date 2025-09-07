# 🚀 Vercel Deployment Guide

## Step 1: Prepare Your Code (Already Done!)
Your code is already Vercel-ready because:
- ✅ Uses environment variables instead of hardcoded secrets
- ✅ `.gitignore` prevents uploading sensitive files
- ✅ No API keys exposed in code

## Step 2: Create Vercel Account
1. Go to https://vercel.com/
2. Sign up with GitHub
3. Connect your GitHub account

## Step 3: Deploy to Vercel

### Option A: Through Vercel Dashboard
1. Click "New Project" in Vercel
2. Import your GitHub repository
3. Vercel will automatically detect it's a Python app
4. Click "Deploy"

### Option B: Through Git Push
1. Push your code to GitHub:
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```
2. Vercel will auto-deploy when you push

## Step 4: Add Your API Keys (IMPORTANT!)
After deployment, go to:
1. **Vercel Dashboard** → Your Project → **Settings** → **Environment Variables**
2. Add these variables:

```
FLASK_SECRET_KEY = your-actual-secret-key-here
GCP_PROJECT_ID = your-google-cloud-project-id  
GOOGLE_APPLICATION_CREDENTIALS = {"type": "service_account", "project_id": "your-project"...}
```

**For Google credentials:** Copy your entire `service-account-key.json` content and paste it as the value.

## Step 5: Redeploy
After adding environment variables:
1. Go to **Deployments** tab
2. Click "..." on latest deployment
3. Click "Redeploy"

## 🎯 That's It!
Your app will be live at: `https://your-app-name.vercel.app`

## 🔧 Vercel Configuration (Optional)
Create `vercel.json` in your project root:
```json
{
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

## 🛡️ Security Notes:
- ✅ Your API keys are stored in Vercel's secure environment
- ✅ Not visible in your code or GitHub
- ✅ Only your deployed app can access them
- ✅ Vercel encrypts all environment variables

**Your app will work exactly like localhost, but available worldwide!**
