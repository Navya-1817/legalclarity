#!/usr/bin/env python3
"""
COMPLETE setup for LegalClarity
Creates .env file, initializes database, and validates everything works
"""
import os
import secrets
import sqlite3

def create_env_file():
    """Create .env file with user inputs"""
    print("🔐 Setting up environment variables...")
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        overwrite = input("Do you want to overwrite it? (y/n): ").lower()
        if overwrite != 'y':
            return False
    
    # Get user inputs with better defaults
    print("\nPress Enter to use safe defaults:")
    
    flask_secret = input("Flask secret key (Enter for random): ").strip()
    if not flask_secret:
        flask_secret = secrets.token_urlsafe(32)
        print(f"✅ Generated secure random key")
    
    gcp_project = input("GCP Project ID (Enter to skip for now): ").strip()
    if not gcp_project:
        gcp_project = ""
        print("⚠️  Skipping GCP setup - you can add this later")
    
    gcp_creds = input("GCP credentials file path (Enter for default): ").strip()
    if not gcp_creds:
        gcp_creds = "./service-account-key.json"
    
    # Create .env file
    env_content = f"""# LegalClarity Environment Variables
# This file is automatically excluded from Git

FLASK_SECRET_KEY={flask_secret}
FLASK_ENV=development
DATABASE_URL=sqlite:///database.db
MAX_CONTENT_LENGTH=10485760
UPLOAD_FOLDER=temp_uploads
"""
    
    if gcp_project:
        env_content += f"""
# Google Cloud Platform (optional - for AI features)
GCP_PROJECT_ID={gcp_project}
GOOGLE_APPLICATION_CREDENTIALS={gcp_creds}
"""
    else:
        env_content += """
# Google Cloud Platform (add these when you get GCP credentials)
# GCP_PROJECT_ID=your-project-id
# GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created successfully!")
    return True

def init_database():
    """Initialize the database"""
    print("\n📁 Setting up database...")
    
    try:
        # Create database and tables
        with sqlite3.connect('database.db') as conn:
            with open('schema.sql', 'r') as f:
                conn.executescript(f.read())
        
        print("✅ Database initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def test_app():
    """Test if the app can start"""
    print("\n🧪 Testing app startup...")
    
    try:
        # Try to import the app
        os.environ['TESTING'] = '1'  # Prevent actual startup
        import app
        print("✅ App imports successfully!")
        return True
    except Exception as e:
        print(f"❌ App test failed: {e}")
        return False

def validate_security():
    """Check security setup"""
    print("\n🔒 Validating security...")
    
    issues = []
    
    # Check .gitignore
    if not os.path.exists('.gitignore'):
        issues.append("❌ .gitignore missing")
    else:
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
        if '.env' not in gitignore_content:
            issues.append("❌ .env not in .gitignore")
        if '*.json' not in gitignore_content:
            issues.append("❌ *.json not in .gitignore")
    
    # Check .env exists
    if not os.path.exists('.env'):
        issues.append("❌ .env file missing")
    
    if issues:
        print("� Security issues found:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("✅ Security setup is correct!")
        return True

def main():
    print("🚀 LegalClarity Complete Setup")
    print("=" * 50)
    print("This will set up everything you need to run the app safely.\n")
    
    success_count = 0
    total_steps = 4
    
    # Step 1: Create .env file
    if create_env_file():
        success_count += 1
    
    # Step 2: Initialize database
    if init_database():
        success_count += 1
    
    # Step 3: Test app
    if test_app():
        success_count += 1
    
    # Step 4: Validate security
    if validate_security():
        success_count += 1
    
    print(f"\n📊 Setup Results: {success_count}/{total_steps} steps completed")
    
    if success_count == total_steps:
        print("\n🎉 Setup Complete! Your app is ready!")
        print("\n📝 Next steps:")
        print("1. Run: python app.py")
        print("2. Open: http://localhost:5000")
        print("3. Create an account and test the app")
        print("4. Add real GCP credentials to .env when ready")
        print("5. Deploy to Vercel/Heroku (see VERCEL_DEPLOY.md)")
        print("\n🔒 Security: Your .env file will NOT be uploaded to GitHub!")
    else:
        print("\n⚠️  Some issues found. Please fix them before proceeding.")

if __name__ == "__main__":
    main()
