# Railway Deployment (Free Alternative)

## Why Railway?
- **Free Tier**: $5 credit per month (enough for your app)
- **No Credit Card Required**: For hobby plan
- **Easy Deployment**: Connect GitHub and deploy
- **Supports Python/Flask**: Native support

## Steps:

1. **Go to Railway**: https://railway.app
2. **Sign up with GitHub**
3. **Create New Project** → **Deploy from GitHub repo**
4. **Select your repository**: navya-1817/legalclarity
5. **Set Environment Variables**:
   - `FLASK_SECRET_KEY`: `03728b70e22e821ffd0208bae0c80cc9534fe75ce67a5355b046e99dd086272e`
   - `GCP_PROJECT_ID`: `shining-sign-468814-i2`
   - `GOOGLE_CREDENTIALS_B64`: `[your base64 string from before]`
6. **Deploy**: Railway will automatically build and deploy

## Procfile for Railway
```
web: gunicorn --bind 0.0.0.0:$PORT app:app
```

## Alternative: Render.com
- Also free tier
- Similar process
- No credit card required
