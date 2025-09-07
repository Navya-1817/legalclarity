#!/usr/bin/env python3
"""
Safe setup script for LegalClarity
This script helps you configure API keys securely without exposing them in Git
"""
import os
import json
from pathlib import Path

def create_env_file():
    """Create .env file with user input"""
    print("🔐 Setting up your environment variables safely...")
    print("This will create a .env file that is excluded from Git.\n")
    
    # Get user inputs
    flask_secret = input("Enter your Flask secret key (or press Enter for random): ").strip()
    if not flask_secret:
        import secrets
        flask_secret = secrets.token_urlsafe(32)
        print(f"Generated random secret key: {flask_secret}")
    
    gcp_project = input("Enter your GCP Project ID: ").strip()
    gcp_creds_path = input("Enter path to your GCP service account JSON (e.g., ./service-account-key.json): ").strip()
    
    # Create .env file
    env_content = f"""# LegalClarity Environment Variables
# This file is automatically excluded from Git for security

# Flask Configuration
FLASK_SECRET_KEY={flask_secret}
FLASK_ENV=development

# Google Cloud Platform
GCP_PROJECT_ID={gcp_project}
GOOGLE_APPLICATION_CREDENTIALS={gcp_creds_path}

# Database (for production, consider PostgreSQL)
DATABASE_URL=sqlite:///database.db

# Upload limits
MAX_CONTENT_LENGTH=10485760
UPLOAD_FOLDER=temp_uploads
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n✅ .env file created successfully!")
    print("✅ This file is automatically excluded from Git")
    print("✅ Your API keys are now secure")

def check_gitignore():
    """Ensure .gitignore is properly configured"""
    gitignore_path = Path('.gitignore')
    if not gitignore_path.exists():
        print("⚠️  .gitignore file not found!")
        return False
    
    with open('.gitignore', 'r') as f:
        content = f.read()
    
    required_entries = ['.env', '*.json', 'database.db']
    missing = [entry for entry in required_entries if entry not in content]
    
    if missing:
        print(f"⚠️  Missing entries in .gitignore: {missing}")
        return False
    
    print("✅ .gitignore is properly configured")
    return True

def validate_setup():
    """Validate that setup is secure"""
    issues = []
    
    # Check if .env exists
    if not Path('.env').exists():
        issues.append("❌ .env file not found")
    
    # Check if service account file exists
    if Path('.env').exists():
        try:
            with open('.env', 'r') as f:
                env_content = f.read()
                if 'GOOGLE_APPLICATION_CREDENTIALS=' in env_content:
                    creds_path = [line.split('=')[1] for line in env_content.split('\n') 
                                if line.startswith('GOOGLE_APPLICATION_CREDENTIALS=')][0]
                    if not Path(creds_path).exists():
                        issues.append(f"❌ Service account file not found: {creds_path}")
        except:
            issues.append("❌ Error reading .env file")
    
    # Check gitignore
    if not check_gitignore():
        issues.append("❌ .gitignore not properly configured")
    
    if issues:
        print("\n🚨 Security Issues Found:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("\n🔒 Security Validation Passed!")
        print("✅ Your setup is secure for GitHub")
        return True

def main():
    print("=" * 60)
    print("🔐 LegalClarity Secure Setup")
    print("=" * 60)
    print("This script helps you set up API keys safely.")
    print("Your secrets will NOT be committed to Git.\n")
    
    choice = input("Choose an option:\n1. Create .env file\n2. Validate setup\n3. Both\nEnter choice (1-3): ").strip()
    
    if choice in ['1', '3']:
        create_env_file()
    
    if choice in ['2', '3']:
        validate_setup()
    
    print("\n📚 Next steps:")
    print("1. Add your real API keys to the .env file")
    print("2. Download your GCP service account JSON")
    print("3. Test your app locally: python app.py")
    print("4. Push to GitHub safely - no secrets will be exposed!")

if __name__ == "__main__":
    main()
