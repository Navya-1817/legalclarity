# app.py
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session, g, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_bcrypt import Bcrypt
import json
import sqlite3
import io
import os
import base64
from werkzeug.utils import secure_filename
from google.cloud import vision
from google.cloud import texttospeech

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, using system env vars

# --- AI Configuration ---
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID')  # Must be set via environment variable
GCP_LOCATION = "us-central1"

# Validate required environment variables
if not GCP_PROJECT_ID:
    print("⚠️  Warning: GCP_PROJECT_ID not set. Google Cloud features will not work.")
    print("   Create a .env file with: GCP_PROJECT_ID=your-actual-project-id")

# Initialize Vision API client
try:
    # Check if we have service account JSON as environment variable
    service_account_info = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
    if service_account_info:
        import json
        from google.oauth2 import service_account
        
        # Parse the JSON string
        service_account_dict = json.loads(service_account_info)
        credentials = service_account.Credentials.from_service_account_info(service_account_dict)
        
        vision_client = vision.ImageAnnotatorClient(credentials=credentials)
        tts_client = texttospeech.TextToSpeechClient(credentials=credentials)
    else:
        # Fall back to default credentials (service account file)
        vision_client = vision.ImageAnnotatorClient()
        tts_client = texttospeech.TextToSpeechClient()
except Exception as e:
    print(f"Warning: Google Cloud APIs not configured properly: {e}")
    vision_client = None
    tts_client = None
# --- End AI Configuration ---

# --- Language Support ---
LANGUAGES = {
    'en': {
        'name': 'English',
        'tts_code': 'en-US',
        'tts_voice': 'en-US-Neural2-C'
    },
    'hi': {
        'name': 'हिंदी',
        'tts_code': 'hi-IN',
        'tts_voice': 'hi-IN-Neural2-A'
    }
}

# Translation dictionary for UI elements
TRANSLATIONS = {
    'en': {
        'app_title': 'Legal Clarity',
        'dashboard': 'Dashboard',
        'login': 'Log In',
        'logout': 'Log Out',
        'register': 'Register',
        'analyze_document': 'Analyze Document',
        'upload_document': 'Upload Document',
        'paste_text': 'Paste Text',
        'summary': 'Summary',
        'listen': 'Listen',
        'my_documents': 'My Documents',
        'no_documents': 'No documents analyzed yet.',
        'document_analysis': 'Document Analysis',
        'important_clauses': 'Important Clauses',
        'language': 'Language'
    },
    'hi': {
        'app_title': 'कानूनी स्पष्टता',
        'dashboard': 'डैशबोर्ड',
        'login': 'लॉग इन',
        'logout': 'लॉग आउट',
        'register': 'पंजीकरण',
        'analyze_document': 'दस्तावेज़ का विश्लेषण',
        'upload_document': 'दस्तावेज़ अपलोड करें',
        'paste_text': 'टेक्स्ट पेस्ट करें',
        'summary': 'सारांश',
        'listen': 'सुनें',
        'my_documents': 'मेरे दस्तावेज़',
        'no_documents': 'अभी तक कोई दस्तावेज़ का विश्लेषण नहीं किया गया।',
        'document_analysis': 'दस्तावेज़ विश्लेषण',
        'important_clauses': 'महत्वपूर्ण खंड',
        'language': 'भाषा'
    }
}

def get_current_language():
    """Get the current language from session, default to English"""
    return session.get('language', 'en')

def get_translation(key):
    """Get translation for a key in the current language"""
    lang = get_current_language()
    return TRANSLATIONS.get(lang, {}).get(key, TRANSLATIONS['en'].get(key, key))

# --- End Language Support ---

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')  # Must be set via environment variable
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 10 * 1024 * 1024))  # Max upload size: 10MB
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'temp_uploads')  # Temporary storage for uploads

# Validate required environment variables
if not app.secret_key:
    print("⚠️  Warning: FLASK_SECRET_KEY not set. Using insecure default for development.")
    print("   Create a .env file with: FLASK_SECRET_KEY=your-secret-key")
    app.secret_key = 'dev-only-insecure-key-change-this'

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DATABASE = os.getenv('DATABASE_PATH', 'database.db')
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# --- User Model for Flask-Login ---
class User(UserMixin):
    def __init__(self, id_, username, password_hash):
        self.id = id_
        self.username = username
        self.password_hash = password_hash

    @staticmethod
    def get(user_id):
        con = get_db()
        cur = con.execute('SELECT id, username, password_hash FROM users WHERE id = ?', (user_id,))
        row = cur.fetchone()
        if row:
            return User(*row)
        return None

    @staticmethod
    def get_by_username(username):
        con = get_db()
        cur = con.execute('SELECT id, username, password_hash FROM users WHERE username = ?', (username,))
        row = cur.fetchone()
        if row:
            return User(*row)
        return None

# --- DB Helpers ---
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def init_db():
    """Initialize the database with schema"""
    try:
        with sqlite3.connect(DATABASE) as conn:
            with open('schema.sql', 'r') as f:
                conn.executescript(f.read())
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

def ensure_db_exists():
    """Ensure database exists and is properly initialized"""
    if not os.path.exists(DATABASE):
        print("📁 Database not found. Creating...")
        init_db()
    else:
        # Check if tables exist
        try:
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
                if not cursor.fetchone():
                    print("📁 Database exists but tables missing. Initializing...")
                    init_db()
        except Exception as e:
            print(f"❌ Database check failed: {e}")
            init_db()

# Initialize database on startup
ensure_db_exists()

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.after_request
def add_cache_control(response):
    """Add cache control headers to prevent caching of sensitive pages"""
    if request.endpoint and any(endpoint in request.endpoint for endpoint in ['dashboard', 'view_analysis', 'logout']):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

@app.context_processor
def inject_language_data():
    """Make language data available to all templates"""
    return {
        'current_language': get_current_language(),
        'languages': LANGUAGES,
        'get_translation': get_translation
    }

def analyze_with_vertex_ai(document_text: str, language: str = 'en') -> dict:
    """
    Analyze document using Google Vertex AI
    Requires: pip install google-cloud-aiplatform
    """
    try:
        from google.cloud import aiplatform
        from vertexai.preview.generative_models import GenerativeModel
    except ImportError:
        raise Exception("Google Cloud AI Platform not installed. Run: pip install google-cloud-aiplatform")
    
    try:
        # Check if we have service account JSON as environment variable
        service_account_info = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
        if service_account_info:
            import json
            from google.oauth2 import service_account
            
            # Parse the JSON string
            service_account_dict = json.loads(service_account_info)
            credentials = service_account.Credentials.from_service_account_info(service_account_dict)
            
            aiplatform.init(project=GCP_PROJECT_ID, location=GCP_LOCATION, credentials=credentials)
        else:
            # Fall back to default credentials
            aiplatform.init(project=GCP_PROJECT_ID, location=GCP_LOCATION)
    except Exception as e:
        raise Exception(f"Failed to initialize Vertex AI. Check GCP_PROJECT_ID: {str(e)}")
    
    prompt_templates = {
        'en': f"""Analyze this legal document and provide a JSON response with:
1. "title": Brief document title
2. "summary": Plain English summary
3. "annotations": Array of important clauses with "text_to_highlight" and "explanation"

Document: {document_text}

Return only valid JSON:""",
        'hi': f"""इस कानूनी दस्तावेज़ का विश्लेषण करें और JSON प्रतिक्रिया प्रदान करें:
1. "title": संक्षिप्त दस्तावेज़ शीर्षक
2. "summary": सरल हिंदी सारांश
3. "annotations": "text_to_highlight" और "explanation" के साथ महत्वपूर्ण खंडों की सरणी

दस्तावेज़: {document_text}

केवल वैध JSON वापस करें:"""
    }
    
    try:
        model = GenerativeModel("gemini-pro")
        response = model.generate_content(prompt_templates[language])
        
        # Clean the response text to extract JSON
        response_text = response.text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Parse the JSON response
        result = json.loads(response_text)
        result['original_text'] = document_text
        return result
        
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON response from Vertex AI: {str(e)}")
    except Exception as e:
        raise Exception(f"Vertex AI analysis failed: {str(e)}")

def analyze_with_ai(document_text: str) -> dict:
    """
    Main AI analysis function using Google Vertex AI
    """
    if not document_text or len(document_text.strip()) < 10:
        raise Exception("Document text is too short for analysis")
    
    lang = get_current_language()
    
    try:
        return analyze_with_vertex_ai(document_text, lang)
    except Exception as e:
        error_messages = {
            'en': f"AI analysis failed: {str(e)}",
            'hi': f"AI विश्लेषण असफल: {str(e)}"
        }
        raise Exception(error_messages.get(lang, error_messages['en']))

# --- Auth Routes ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        con = get_db()
        if User.get_by_username(username):
            flash('Username already exists.')
            return redirect(url_for('register'))
        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        con.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, pw_hash))
        con.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.get_by_username(username)
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    # Preserve language preference before clearing session
    user_language = session.get('language', 'en')
    
    # Clear all session data
    session.clear()
    
    # Logout the user
    logout_user()
    
    # Restore language preference
    session['language'] = user_language
    
    # Create response with cache control headers
    response = redirect(url_for('home'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    flash('You have been logged out successfully.')
    return response

# --- Home page (public) ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/set_language/<language>')
def set_language(language):
    """Set the user's preferred language"""
    if language in LANGUAGES:
        session['language'] = language
    # Redirect back to the page they came from, or dashboard if logged in, or home if not
    return redirect(request.referrer or (url_for('dashboard') if current_user.is_authenticated else url_for('home')))

def extract_text_from_image(image_file):
    """
    Extract text from an uploaded image file using Google Cloud Vision API.
    
    Args:
        image_file: The uploaded image file
        
    Returns:
        str: The extracted text from the image
    """
    if vision_client is None:
        raise Exception("Vision API not configured. Please set up Google Cloud credentials.")
    
    try:
        # Read the file content
        content = image_file.read()
        
        # Create an image object for the Vision API
        image = vision.Image(content=content)
        
        # Perform OCR on the image
        response = vision_client.text_detection(image=image)
        texts = response.text_annotations
        
        # Check if any text was found
        if not texts:
            return ""
            
        # The first text annotation contains all the text in the image
        full_text = texts[0].description
        
        # Check for errors
        if response.error.message:
            raise Exception(f"Vision API error: {response.error.message}")
            
        return full_text
        
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        raise e

@app.route('/analyze', methods=['POST'])
@login_required
def analyze_document():
    document_text = request.get_json().get('text', '')
    if not document_text:
        return jsonify({"error": "No text provided"}), 400

    analysis_result = analyze_with_ai(document_text)

    if analysis_result:
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO documents (title, original_text, analysis_json, user_id) VALUES (?, ?, ?, ?)',
                (
                    analysis_result.get('title', 'Untitled Document'),
                    analysis_result.get('original_text'),
                    json.dumps(analysis_result),
                    current_user.id
                )
            )
            new_doc_id = cursor.lastrowid # Get the ID of the new document
            conn.commit()
            print(f"Saved document with ID {new_doc_id} to database.")
            # Return the new ID so the frontend can redirect
            return jsonify({"success": True, "new_document_id": new_doc_id})
        except Exception as e:
            print(f"Database error: {e}")
            return jsonify({"error": "Could not save to database"}), 500
    else:
        return jsonify({"error": "Failed to analyze document"}), 500
        
@app.route('/analyze-document', methods=['POST'])
@login_required
def analyze_document_upload():
    """
    Handle document analysis from either text input or file upload.
    Uses Vision API for image uploads.
    """
    try:
        document_text = ""
        
        # Check if a file was uploaded
        if 'document' in request.files and request.files['document'].filename:
            file = request.files['document']
            
            # Validate file type
            if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                return jsonify({"error": "Only PNG, JPG, and JPEG files are allowed"}), 400
                
            try:
                # Extract text from the image
                document_text = extract_text_from_image(file)
                
                if not document_text:
                    return jsonify({"error": "Could not extract text from the image"}), 400
                    
            except Exception as e:
                print(f"Error during OCR: {e}")
                return jsonify({"error": "Failed to process the image"}), 500
                
        # Otherwise check for text input
        elif 'text' in request.form and request.form['text'].strip():
            document_text = request.form['text'].strip()
            
        else:
            return jsonify({"error": "No document or text provided"}), 400
            
        # Analyze the text with the AI
        analysis_result = analyze_with_ai(document_text)
        
        if analysis_result:
            try:
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO documents (title, original_text, analysis_json, user_id) VALUES (?, ?, ?, ?)',
                    (
                        analysis_result.get('title', 'Untitled Document'),
                        analysis_result.get('original_text'),
                        json.dumps(analysis_result),
                        current_user.id
                    )
                )
                new_doc_id = cursor.lastrowid
                conn.commit()
                print(f"Saved document with ID {new_doc_id} to database.")
                # Return the new ID so the frontend can redirect
                return jsonify({"success": True, "new_document_id": new_doc_id})
                
            except Exception as e:
                print(f"Database error: {e}")
                return jsonify({"error": "Could not save to database"}), 500
        else:
            return jsonify({"error": "Failed to analyze document"}), 500
            
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

# --- Protected Routes ---
@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    # Fetch all documents for the current user, with the most recent ones first
    documents = conn.execute('SELECT id, created, title FROM documents WHERE user_id = ? ORDER BY created DESC', (current_user.id,)).fetchall()
    # Pass the list of documents to the dashboard template
    return render_template('dashboard.html', documents=documents)

@app.route('/analysis/<int:doc_id>')
@login_required
def view_analysis(doc_id):
    conn = get_db()
    # Fetch the specific document by its ID and the current user's ID
    doc = conn.execute('SELECT analysis_json FROM documents WHERE id = ? AND user_id = ?', (doc_id, current_user.id)).fetchone()
    
    if doc is None:
        flash('Document not found or access denied.')
        return redirect(url_for('dashboard'))
        
    # The analysis_json is a string, so we need to parse it back into a dictionary
    analysis_data = json.loads(doc['analysis_json'])
    
    # Pass this data to our existing results template
    return render_template('results.html', analysis_data=analysis_data)

@app.route('/text-to-speech', methods=['POST'])
@login_required
def text_to_speech():
    """
    Convert text to speech using Google Cloud Text-to-Speech API
    Supports both English and Hindi based on user's language preference
    
    Returns the audio file as a response that can be played in the browser
    """
    if tts_client is None:
        return jsonify({'error': 'Text-to-Speech API not configured. Please set up Google Cloud credentials.'}), 503
    
    try:
        # Get the text from the request
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
            
        # Get current language settings
        lang = get_current_language()
        lang_config = LANGUAGES.get(lang, LANGUAGES['en'])
        
        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # Build the voice request based on selected language
        voice = texttospeech.VoiceSelectionParams(
            language_code=lang_config['tts_code'],
            name=lang_config['tts_voice'],
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        
        # Select the type of audio file to return
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.9,  # Slightly slower than default for better comprehension
            pitch=0.0,  # Default pitch
            volume_gain_db=0.0  # Default volume
        )
        
        # Perform the text-to-speech request
        response = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # Create an in-memory bytes buffer
        audio_buffer = io.BytesIO(response.audio_content)
        audio_buffer.seek(0)
        
        # Return the audio as a file response
        return send_file(
            audio_buffer,
            mimetype='audio/mp3',
            as_attachment=False,
            download_name='summary.mp3'
        )
        
    except Exception as e:
        print(f"Error in text-to-speech: {e}")
        return jsonify({'error': str(e)}), 500

# Vercel compatibility
app = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)