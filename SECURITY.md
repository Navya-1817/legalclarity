# 🔐 SECURITY GUIDE: Protecting Your API Keys

## ⚠️ NEVER COMMIT THESE TO GITHUB:
- `.env` files
- `service-account-key.json` 
- Any files containing API keys
- Database files with user data

## ✅ SAFE METHODS TO USE API KEYS:

### Method 1: Environment Variables (Recommended)

#### 1. Create `.env` file (already in .gitignore):
```bash
# .env (NEVER commit this file)
FLASK_SECRET_KEY=your-super-secret-key-here
GCP_PROJECT_ID=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json
```

#### 2. Your app already loads these safely:
```python
# app.py (this is safe to commit)
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', "your-gcp-project-id")
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key_change_in_production')
```

### Method 2: Cloud Platform Secrets (Production)

#### Google Cloud Secret Manager:
```bash
# Store secrets in Google Cloud
gcloud secrets create flask-secret-key --data-file=secret.txt
gcloud secrets create gcp-project-id --data-file=project.txt
```

#### Heroku Config Vars:
```bash
# Set environment variables in Heroku
heroku config:set FLASK_SECRET_KEY=your-secret-key
heroku config:set GCP_PROJECT_ID=your-project-id
```

### Method 3: GitHub Secrets (for CI/CD)
1. Go to your GitHub repo → Settings → Secrets and variables → Actions
2. Add secrets:
   - `FLASK_SECRET_KEY`
   - `GCP_PROJECT_ID` 
   - `GOOGLE_CREDENTIALS` (base64 encoded JSON)

## 🚀 DEPLOYMENT CHECKLIST:

### Before Pushing to GitHub:
- [ ] ✅ `.env` file is in `.gitignore`
- [ ] ✅ No hardcoded API keys in code
- [ ] ✅ Service account JSON not committed
- [ ] ✅ Database files excluded
- [ ] ✅ All secrets use environment variables

### For Production:
- [ ] Set environment variables on your hosting platform
- [ ] Use cloud secret management services
- [ ] Enable HTTPS
- [ ] Rotate keys regularly

## 🔍 CHECK YOUR CODE:
```bash
# Search for potential secrets before committing
grep -r "secret" --exclude-dir=.git .
grep -r "key" --exclude-dir=.git .
grep -r "password" --exclude-dir=.git .
```

## 🛡️ YOUR APP IS ALREADY SECURE!
Your LegalClarity app correctly uses:
- ✅ `os.getenv()` for all sensitive data
- ✅ `.env.example` for documentation
- ✅ `.gitignore` to exclude sensitive files
- ✅ Default fallback values for development

**Just remember: NEVER put real API keys in your code files!**
