# Production Deployment Checklist for LegalClarity

## 🔧 Configuration Required

### 1. Google Cloud Services Setup
- [ ] **Enable Vertex AI API** in your GCP project
- [ ] **Enable Vision API** in your GCP project  
- [ ] **Enable Text-to-Speech API** in your GCP project
- [ ] Create service account with proper permissions:
  - Vertex AI User
  - Cloud Vision API User
  - Cloud Text-to-Speech API User
- [ ] Download service account JSON key
- [ ] Set GOOGLE_APPLICATION_CREDENTIALS environment variable

### 2. Environment Variables
Copy `.env.example` to `.env` and configure:
```bash
# Required
FLASK_SECRET_KEY=your-super-secret-production-key
GCP_PROJECT_ID=your-actual-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### 3. AI Service Configuration
Your app uses **Google Vertex AI (Gemini Pro)** for document analysis:
- No additional API keys needed beyond GCP credentials
- Uses the same Google Cloud account as Vision & TTS APIs
- Supports both English and Hindi analysis

## 🚀 Deployment Options

### Option 1: Google Cloud Platform (Recommended)
```bash
# Install AI dependencies
pip install google-cloud-aiplatform

# Install Google Cloud CLI
# Deploy to App Engine
gcloud app deploy
```

### Option 2: Heroku
```bash
# Install AI dependencies
pip install -r requirements-ai.txt

# Install Heroku CLI
heroku create your-app-name
git push heroku main
```

### Option 3: VPS/Server
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-ai.txt

# Use gunicorn for production
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## 📋 Pre-Deployment Steps

1. **Install Vertex AI dependencies**:
   ```bash
   pip install google-cloud-aiplatform
   ```

2. **Test locally with real APIs**:
   ```bash
   python app.py
   ```

3. **Test all features**:
   - [ ] User registration/login
   - [ ] Document upload (image OCR)
   - [ ] **Vertex AI document analysis** ✨
   - [ ] Text-to-speech (English & Hindi)
   - [ ] Language switching
   - [ ] Document history

## ✅ Current Status
- ✅ Flask app structure
- ✅ User authentication
- ✅ Database setup
- ✅ Hindi language support
- ✅ OCR integration (needs GCP credentials)
- ✅ TTS integration (needs GCP credentials)
- ✅ **Vertex AI integration ready** (needs GCP credentials)
- ❌ Production configuration
- ❌ GCP service account setup
- ❌ Production server setup

## 🔥 Ready to Deploy?
**Yes!** You need:
1. Google Cloud Project with Vertex AI, Vision, and TTS APIs enabled
2. Service account JSON key with proper permissions
3. Environment variables configured
4. Deploy to your preferred platform

**One Google Cloud account handles everything** - OCR, AI analysis, and text-to-speech! 🎉
