from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from sqlalchemy import text
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField
from wtforms.validators import InputRequired, Length, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_moment import Moment
import re
from datetime import datetime, timedelta
import os
import uuid
from PIL import Image
import html
from dotenv import load_dotenv
import logging
import sys
import socket
from nudenet import NudeDetector

# Configure logging to handle Windows pipe issues
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),  # Log to file to avoid pipe issues
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import Full XAI model only
CybercrimeXAIModel = None  # Initialize to None to prevent NameError if import fails
try:
    from xai_cybercrime_model import CybercrimeXAIModel
    XAI_AVAILABLE = True
    logger.info("Full XAI model imported successfully")
except Exception as e:
    logger.error(f"Full XAI model import failed ({e}). XAI features will be disabled.")
    XAI_AVAILABLE = False

# Import Phishing URL Detector
try:
    from phishing_detector import load_phishing_model, check_urls_in_message, extract_urls
    PHISHING_DETECTOR_AVAILABLE = True
except Exception as e:
    logger.error(f"Phishing detector import failed ({e}). Phishing detection disabled.")
    PHISHING_DETECTOR_AVAILABLE = False
    def check_urls_in_message(msg): return []
    def extract_urls(msg): return []

# Load environment variables
try:
    load_dotenv()
except Exception as e:
    logger.warning(f"Could not load .env file: {e}")

app = Flask(__name__)

# Security Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(32)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///social_media.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Security headers (adjust for development vs production)
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

# Create upload directory
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], 'posts')):
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'posts'))
if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], 'stories')):
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'stories'))
if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], 'profiles')):
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'profiles'))

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
socketio = SocketIO(app, cors_allowed_origins="*")
moment = Moment(app)

# Initialize NSFW detector
nsfw_detector = None
try:
    nsfw_detector = NudeDetector()
    print("✅ NSFW detector initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize NSFW detector: {e}")
    nsfw_detector = None

# Initialize Full XAI model
xai_model = None
if XAI_AVAILABLE:
    try:
        xai_model = CybercrimeXAIModel()
        
        # Load the trained model
        if xai_model.load_model():
            logger.info("Full XAI model loaded successfully")
        else:
            logger.error("Failed to load XAI model file")
            xai_model = None
            
    except Exception as e:
        logger.error(f"Error initializing XAI model: {e}")
        xai_model = None

# Initialize Phishing URL Detection model
phishing_model_loaded = False
if PHISHING_DETECTOR_AVAILABLE:
    try:
        phishing_model_loaded = load_phishing_model('phishing_rf_model.pkl')
    except Exception as e:
        logger.error(f"Error loading phishing model: {e}")

# Crime and payment-related keywords for detection
CRIME_KEYWORDS = [
    'kill', 'murder', 'bomb', 'terrorist', 'weapon', 'gun', 'knife', 'attack',
    'violence', 'threat', 'blackmail', 'ransom', 'kidnap', 'abuse', 'assault',
    'robbery', 'steal', 'fraud', 'scam', 'drug dealing', 'cocaine', 'heroin',
    'methamphetamine', 'illegal', 'criminal', 'crime', 'felony'
]

PAYMENT_KEYWORDS = [
    'send money', 'transfer money', 'bank account', 'credit card',
    'debit card', 'paypal', 'venmo', 'cashapp', 'zelle', 'wire transfer',
    'bitcoin', 'cryptocurrency', 'loan', 'borrow money', 'lend money',
    'cash advance', 'financial help', 'emergency money', 'urgent payment',
    'money order', 'western union', 'moneygram', 'gift card', 'prepaid card'
]

# Association tables for many-to-many relationships
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

post_likes = db.Table('post_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True)
)

# Database Models
class BlockedWord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False)  # profanity, hate_speech, custom, etc.
    severity = db.Column(db.Float, default=1.0)  # 0.1 to 2.0
    added_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(80), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    profile_pic = db.Column(db.String(200), default='default.jpg')
    is_private = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    stories = db.relationship('Story', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    messages = db.relationship('Message', backref='author', lazy='dynamic', cascade='all, delete-orphan', primaryjoin='User.id == Message.user_id')
    
    # Following relationships
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers_users', lazy='dynamic'), lazy='dynamic')
    
    # Liked posts
    liked_posts = db.relationship(
        'Post', secondary=post_likes,
        backref=db.backref('liked_by', lazy='dynamic'), lazy='dynamic')
    
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
    
    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    
    def followers_count(self):
        return self.followers_users.count()
    
    def following_count(self):
        return self.followed.count()
    
    def posts_count(self):
        return self.posts.count()
    
    def like_post(self, post):
        if not self.has_liked_post(post):
            self.liked_posts.append(post)
    
    def unlike_post(self, post):
        if self.has_liked_post(post):
            self.liked_posts.remove(post)
    
    def has_liked_post(self, post):
        return self.liked_posts.filter(post_likes.c.post_id == post.id).count() > 0

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.Text, nullable=True)
    image_filename = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_flagged = db.Column(db.Boolean, default=False)
    flagged_keywords = db.Column(db.String(500))
    is_nsfw = db.Column(db.Boolean, default=False)
    nsfw_confidence = db.Column(db.Float, default=0.0)
    
    # Relationships
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    def likes_count(self):
        return self.liked_by.count()
    
    def comments_count(self):
        return self.comments.count()
    
    @property
    def recent_comments(self):
        """Get the 2 most recent comments for this post"""
        return self.comments.order_by(Comment.timestamp.desc()).limit(2).all()

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String(200), nullable=False)
    text_content = db.Column(db.String(500), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=24))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    views_count = db.Column(db.Integer, default=0)
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    is_flagged = db.Column(db.Boolean, default=False)
    flagged_keywords = db.Column(db.String(500))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Make nullable for group chats
    room = db.Column(db.String(100), nullable=False)
    is_flagged = db.Column(db.Boolean, default=False)
    flagged_keywords = db.Column(db.String(500))
    is_read = db.Column(db.Boolean, default=False)
    
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')

class Hashtag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    posts_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PostHashtag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    hashtag_id = db.Column(db.Integer, db.ForeignKey('hashtag.id'), nullable=False)

# Forms
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[Length(max=35)])  # Made optional
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=20)])
    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError('Username already exists. Choose a different one.')
    
    def validate_email(self, email):
        if email.data and email.data.strip():  # Only validate if email is provided
            existing_user_email = User.query.filter_by(email=email.data).first()
            if existing_user_email:
                raise ValidationError('Email already exists. Choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=20)])
    submit = SubmitField('Login')

class PostForm(FlaskForm):
    caption = TextAreaField('Caption', validators=[Length(max=2200)])
    image = FileField('Photo/Video')
    location = StringField('Location', validators=[Length(max=100)])
    submit = SubmitField('Share')

class CommentForm(FlaskForm):
    content = StringField('Add a comment...', validators=[InputRequired(), Length(max=500)])
    submit = SubmitField('Post')

class ProfileForm(FlaskForm):
    bio = TextAreaField('Bio', validators=[Length(max=500)])
    profile_pic = FileField('Profile Picture')
    submit = SubmitField('Update Profile')

class AdminLoginForm(FlaskForm):
    username = StringField('Admin Username', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=20)])
    submit = SubmitField('Admin Login')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Admin decorator
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in first.', 'error')
            return redirect(url_for('admin_login'))
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def safe_log(message, level='info'):
    """Safe logging function to prevent encoding issues"""
    try:
        if level == 'error':
            logger.error(message)
        elif level == 'warning':
            logger.warning(message)
        else:
            logger.info(message)
    except Exception:
        pass  # Silently fail if logging fails

# File upload utilities
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(image_path, max_size=(800, 800)):
    """Process and resize uploaded images"""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Resize image while maintaining aspect ratio
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save processed image
            img.save(image_path, 'JPEG', quality=85, optimize=True)
    except Exception as e:
        safe_log(f"ERROR: Error processing image: {e}", 'error')

def detect_nsfw_content(image_path):
    """Detect NSFW content in uploaded images"""
    try:
        print(f"🔍 Starting NSFW detection for: {image_path}")
        
        if nsfw_detector is None:
            print("⚠️ NSFW detector not available - allowing upload")
            return False, 0.0
        
        # Only process image files
        if not image_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            print("📄 Not an image file - skipping NSFW detection")
            return False, 0.0
        
        # Check if file exists
        if not os.path.exists(image_path):
            print(f"❌ Image file not found: {image_path}")
            return False, 0.0
        
        print("🤖 Running NudeNet detection...")
        # Detect NSFW content
        results = nsfw_detector.detect(image_path)
        print(f"📊 Detection results: {results}")
        
        # Calculate NSFW confidence based on detected objects
        nsfw_confidence = 0.0
        nsfw_detected = False
        detected_labels = []
        
        # NudeNet returns a list of detected objects with labels and confidence scores
        for detection in results:
            label = detection.get('class', '').lower()
            confidence = detection.get('score', 0.0)
            detected_labels.append(f"{label}({confidence:.2f})")
            
            # Check for NSFW labels - more comprehensive list
            nsfw_labels = [
                'exposed_anus', 'exposed_armpits', 'exposed_belly', 'exposed_buttocks',
                'exposed_breast_f', 'exposed_breast_m', 'exposed_genitalia_f', 
                'exposed_genitalia_m', 'exposed_thighs_f', 'exposed_thighs_m',
                'male_breast_exposed', 'female_breast_exposed', 'buttocks_exposed',
                'male_genitalia_exposed', 'female_genitalia_exposed', 'anus_exposed'
            ]
            
            if label in nsfw_labels:
                nsfw_confidence = max(nsfw_confidence, confidence)
                print(f"🚨 NSFW content detected: {label} (confidence: {confidence:.3f})")
                if confidence > 0.3:  # Lower threshold for better detection
                    nsfw_detected = True
        
        print(f"🎯 Final NSFW result: {nsfw_detected}, max confidence: {nsfw_confidence:.3f}")
        print(f"🏷️ All detected labels: {detected_labels}")
        
        return nsfw_detected, nsfw_confidence
        
    except Exception as e:
        print(f"❌ ERROR in NSFW detection: {e}")
        import traceback
        traceback.print_exc()
        return False, 0.0

def extract_hashtags(text):
    """Extract hashtags from text"""
    if not text:
        return []
    return re.findall(r'#(\w+)', text)

def sanitize_input(text):
    """Sanitize user input to prevent XSS attacks"""
    if not text:
        return text
    # HTML escape the content
    return html.escape(text.strip())

def convert_numpy_to_python_scalars(obj):
    """Recursively convert numpy scalars in a dictionary/list to Python scalars."""
    import numpy as np
    if isinstance(obj, dict):
        return {k: convert_numpy_to_python_scalars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_to_python_scalars(elem) for elem in obj]
    elif isinstance(obj, np.generic):
        return obj.item()
    else:
        return obj

# Content Detection Functions
def detect_vulgar_content(text):
    """
    Detect vulgar, offensive, or inappropriate content in text
    Returns: (is_vulgar, vulgar_words, severity_score)
    """
    if not text:
        return False, [], 0.0
    
    text_lower = text.lower()
    
    # Get blocked words from database
    try:
        db_blocked_words = BlockedWord.query.filter_by(is_active=True).all()
        custom_blocked_words = [(word.word.lower(), word.severity) for word in db_blocked_words]
    except:
        custom_blocked_words = []
    
    # Default comprehensive list of vulgar/inappropriate words and patterns
    default_vulgar_words = [
        # Explicit profanity
        'fuck', 'shit', 'bitch', 'asshole', 'damn', 'hell', 'crap',
        'bastard', 'whore', 'slut', 'piss', 'cock', 'dick', 'pussy',
        'tits', 'boobs', 'ass', 'sex', 'porn', 'nude', 'naked',
        
        # Hate speech and slurs
        'nigger', 'faggot', 'retard', 'gay', 'homo', 'lesbian',
        'tranny', 'chink', 'spic', 'kike', 'wetback',
        
        # Threatening language
        'kill', 'murder', 'die', 'death', 'suicide', 'hurt', 'harm',
        'violence', 'beat', 'punch', 'stab', 'shoot',
        
        # Sexual content
        'horny', 'sexy', 'hot', 'bang', 'screw', 'orgasm',
        'masturbate', 'blowjob', 'handjob', 'anal',
        
        # Drug references
        'weed', 'marijuana', 'cocaine', 'heroin', 'meth', 'drugs',
        'high', 'stoned', 'drunk', 'alcohol',
        
        # Harassment terms
        'ugly', 'fat', 'stupid', 'idiot', 'loser', 'freak',
        'weird', 'creep', 'stalker', 'pervert'
    ]
    
    # Combine default and custom words
    vulgar_words = default_vulgar_words + [word for word, severity in custom_blocked_words]
    
    # Patterns for leetspeak and character substitution
    leetspeak_patterns = {
        'f*ck': 'fuck', 'sh*t': 'shit', 'b*tch': 'bitch',
        'f**k': 'fuck', 's**t': 'shit', 'a**': 'ass',
        'fuk': 'fuck', 'sht': 'shit', 'btch': 'bitch',
        'fck': 'fuck', 'dmn': 'damn', 'hll': 'hell',
        '@ss': 'ass', 'a$$': 'ass', 'sh!t': 'shit',
        'f@ck': 'fuck', 'b!tch': 'bitch', 'd@mn': 'damn'
    }
    
    # Check for leetspeak patterns
    for pattern, word in leetspeak_patterns.items():
        if pattern in text_lower:
            text_lower = text_lower.replace(pattern, word)
    
    # Find vulgar words in text
    found_vulgar = []
    severity_score = 0.0
    
    # Check default words
    for word in default_vulgar_words:
        if word in text_lower:
            found_vulgar.append(word)
            # Assign severity scores
            if word in ['fuck', 'shit', 'bitch', 'nigger', 'faggot', 'kill', 'murder']:
                severity_score += 1.0  # High severity
            elif word in ['damn', 'hell', 'crap', 'ass', 'gay', 'stupid']:
                severity_score += 0.5  # Medium severity
            else:
                severity_score += 0.3  # Low severity
    
    # Check custom words with their custom severity
    for word, custom_severity in custom_blocked_words:
        if word in text_lower:
            found_vulgar.append(word)
            severity_score += custom_severity
    
    # Check for repeated characters (like "fuuuuck")
    import re
    repeated_pattern = re.compile(r'(.)\1{2,}')
    if repeated_pattern.search(text_lower):
        for word in vulgar_words:
            # Create pattern with repeated characters
            pattern = ''.join([f'{char}+' for char in word])
            if re.search(pattern, text_lower):
                if word not in found_vulgar:
                    found_vulgar.append(word)
                    severity_score += 0.8
    
    # Check for spacing tricks (like "f u c k")
    spaced_text = re.sub(r'\s+', '', text_lower)
    for word in vulgar_words:
        if word in spaced_text and word not in found_vulgar:
            found_vulgar.append(word)
            severity_score += 0.7
    
    is_vulgar = len(found_vulgar) > 0 or severity_score > 0.5
    
    return is_vulgar, found_vulgar, severity_score

def detect_flagged_content(message):
    """Detect if message contains crime or payment-related keywords using XAI model"""
    if not message:
        return [], [], {}
    
    # Try XAI model first
    xai_result = {}
    xai_crime_keywords = []
    xai_payment_keywords = []
    
    if xai_model:
        try:
            # Get both LIME and SHAP explanations
            xai_result = xai_model.predict_with_explanation(message, explanation_type='both')
            xai_result = convert_numpy_to_python_scalars(xai_result)
            
            # Extract category and convert to our format
            category = xai_result['predicted_category']
            confidence = xai_result['confidence']
            
            # Map XAI categories to our crime/payment classification
            crime_categories = ['threats_violence', 'cyberbullying', 'illegal_drugs', 'weapons_trafficking']
            payment_categories = ['financial_fraud', 'phishing', 'identity_theft', 'romance_scam']
            
            if category in crime_categories:
                xai_crime_keywords = [category]
            elif category in payment_categories:
                xai_payment_keywords = [category]
                
        except Exception as e:
            safe_log(f"XAI model prediction failed: {e}", 'error')
    
    # ALWAYS run keyword-based detection as a safety net
    message_lower = message.lower()
    keyword_crime = []
    keyword_payment = []
    
    # Check for crime keywords
    for keyword in CRIME_KEYWORDS:
        if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', message_lower):
            keyword_crime.append(keyword)
    
    # Check for payment keywords
    for keyword in PAYMENT_KEYWORDS:
        if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', message_lower):
            keyword_payment.append(keyword)
    
    # Combine XAI and keyword results (union of both)
    combined_crime = list(set(xai_crime_keywords + keyword_crime))
    combined_payment = list(set(xai_payment_keywords + keyword_payment))
    
    return combined_crime, combined_payment, xai_result

def get_sender_warning_message(flag_type):
    """Get warning message for sender based on flag type"""
    if flag_type == 'crime':
        return "⚠️ WARNING: Your message contains potentially harmful content. Please reconsider sharing such content as it may violate our community guidelines and could result in account suspension."
    elif flag_type == 'payment':
        return "🚨 FINANCIAL SECURITY ALERT: Your message mentions financial transactions. Be cautious when sharing financial information online. Never share personal banking details or passwords."
    return "⚠️ Your message has been flagged for review."

def get_receiver_warning_message(flag_type):
    """Get warning message for receiver based on flag type"""
    if flag_type == 'crime':
        return "⚠️ SECURITY ALERT: The sender has shared potentially dangerous content. Please report this conversation if you feel unsafe or if the content violates community guidelines."
    elif flag_type == 'payment':
        return "💰 FINANCIAL SAFETY WARNING: Someone is discussing financial transactions with you. Be extremely cautious about sharing personal financial information, passwords, or sending money to people you don't know well."
    return "⚠️ This conversation has been flagged for potentially harmful content."

# Routes
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('feed'))
    return redirect(url_for('login'))

@app.route('/feed')
@login_required
def feed():
    # Get posts from followed users and own posts
    followed_users = current_user.followed.all()
    user_ids = [user.id for user in followed_users] + [current_user.id]
    
    # Base query for posts
    if current_user.is_admin:
        # Admin sees only NSFW detected posts
        query = Post.query.filter(Post.is_nsfw == True)
    else:
        # Regular users see only non-NSFW posts from followed users
        query = Post.query.filter(
            Post.user_id.in_(user_ids),
            Post.is_nsfw == False
        )
    
    # Order and limit results
    posts = query.order_by(Post.timestamp.desc()).limit(50).all()
    
    # Get active stories (non-expired)
    stories = Story.query.filter(
        Story.user_id.in_(user_ids),
        Story.expires_at > datetime.utcnow()
    ).order_by(Story.timestamp.desc()).all()
    
    return render_template('feed.html', posts=posts, stories=stories)

@app.route('/explore')
@login_required
def explore():
    # Get trending posts and hashtags (filter out NSFW posts)
    trending_posts = Post.query.filter(Post.is_nsfw == False).order_by(Post.timestamp.desc()).limit(50).all()
    trending_hashtags = Hashtag.query.order_by(Hashtag.posts_count.desc()).limit(20).all()
    
    return render_template('explore.html', posts=trending_posts, hashtags=trending_hashtags)

@app.route('/debug/nsfw-test')
@login_required
def debug_nsfw_test():
    """Debug endpoint to test NSFW detection"""
    if not current_user.is_admin:
        flash('Access denied. Admin only.', 'error')
        return redirect(url_for('feed'))
    
    return f"""
    <h2>NSFW Detection Debug Info</h2>
    <p><strong>NSFW Detector Status:</strong> {'✅ Initialized' if nsfw_detector else '❌ Not Available'}</p>
    <p><strong>Detection Threshold:</strong> 0.3 (30%)</p>
    <p><strong>Categories Detected:</strong></p>
    <ul>
        <li>exposed_breast_m (male chest)</li>
        <li>exposed_breast_f (female chest)</li>
        <li>exposed_genitalia_m/f</li>
        <li>exposed_buttocks</li>
        <li>And more...</li>
    </ul>
    <p><strong>How to Test:</strong></p>
    <ol>
        <li>Go to Upload page</li>
        <li>Upload a shirtless image</li>
        <li>Check console for debug messages</li>
        <li>Should see blocking message</li>
    </ol>
    <p><a href="/upload">Test Upload Now</a></p>
    """

@app.route('/community-guidelines')
def community_guidelines():
    """Community Guidelines page"""
    return render_template('community_guidelines.html')

@app.route('/people')
@login_required
def people():
    """People discovery page"""
    search_query = request.args.get('search', '')
    
    # Base query: all users except current user
    users_query = User.query.filter(User.id != current_user.id)
    
    # Apply search filter if provided
    if search_query:
        users_query = users_query.filter(
            User.username.contains(search_query)
        )
    
    # Get users with pagination
    page = request.args.get('page', 1, type=int)
    users = users_query.paginate(
        page=page, per_page=20, error_out=False
    )
    
    # For each user, get their latest 3 posts ordered by timestamp desc
    for user in users.items:
        user.recent_posts = user.posts.order_by(text('timestamp desc')).limit(3).all()
    
    return render_template('people.html', users=users, search_query=search_query)

@app.route('/xai-dashboard')
@login_required
def xai_dashboard():
    """XAI Dashboard for viewing model insights and explanations"""
    return render_template('xai_dashboard.html')

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_post():
    form = PostForm()
    if form.validate_on_submit():
        if form.image.data:
            # Validate file
            if not allowed_file(form.image.data.filename):
                flash('Invalid file type. Please upload PNG, JPG, JPEG, GIF, MP4, or MOV files.', 'error')
                return render_template('upload.html', form=form)
            
            # Check file size (client-side validation backup)
            if len(form.image.data.read()) > app.config['MAX_CONTENT_LENGTH']:
                flash('File too large. Maximum size is 16MB.', 'error')
                return render_template('upload.html', form=form)
            
            # Reset file pointer after reading
            form.image.data.seek(0)
            
            # Generate unique filename with secure_filename
            original_filename = secure_filename(form.image.data.filename)
            file_extension = original_filename.rsplit('.', 1)[1].lower()
            filename = str(uuid.uuid4()) + '.' + file_extension
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'posts', filename)
            
            # Save file
            form.image.data.save(file_path)
            print(f"📁 File saved to: {file_path}")
            
            # Process image if it's an image file
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                print("🖼️ Processing image...")
                process_image(file_path)
            
            # Check for NSFW content in uploaded image
            print("🔍 Starting NSFW content check...")
            is_nsfw, nsfw_confidence = detect_nsfw_content(file_path)
            print(f"🎯 NSFW check complete: is_nsfw={is_nsfw}, confidence={nsfw_confidence}")
            
            # Check for crime-related content in caption
            crime_keywords, payment_keywords, xai_result = detect_flagged_content(form.caption.data or '')
            flagged_keywords = crime_keywords + payment_keywords
            is_flagged = len(flagged_keywords) > 0
            if is_flagged:
                print(f"⚠️ Flagged keywords detected: {', '.join(flagged_keywords)}")
            
            
            # Block post if NSFW content is detected
            if is_nsfw:
                print(f"🚫 BLOCKING POST - NSFW content detected with confidence {nsfw_confidence}")
                # Delete the uploaded file since we're blocking the post
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"🗑️ Deleted NSFW file: {file_path}")
                
                print(f"⚠️ NSFW post blocked for user {current_user.username}, confidence: {nsfw_confidence}")
                
                # Check if request is AJAX (for modal popup)
                if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': False,
                        'blocked': True,
                        'reason': 'nsfw',
                        'message': 'Your post has been blocked due to inappropriate content.',
                        'confidence': nsfw_confidence,
                        'show_modal': True
                    }), 400
                else:
                    flash('Your post has been blocked due to inappropriate content. Please upload appropriate images only.', 'error')
                    return render_template('upload.html', form=form)
            else:
                print("✅ Image passed NSFW check - proceeding with post creation")
            
            # Create post (only if not NSFW)
            post = Post(
                caption=form.caption.data,
                image_filename=filename,
                location=form.location.data,
                user_id=current_user.id,
                is_flagged=is_flagged,
                flagged_keywords=', '.join(flagged_keywords) if flagged_keywords else None,
                is_nsfw=is_nsfw,
                nsfw_confidence=nsfw_confidence
            )
            db.session.add(post)
            db.session.flush()  # Flush to get post.id before commit
            
            # Extract and save hashtags
            hashtags = extract_hashtags(form.caption.data or '')
            for tag_name in hashtags:
                hashtag = Hashtag.query.filter_by(name=tag_name.lower()).first()
                if not hashtag:
                    hashtag = Hashtag(name=tag_name.lower())
                    db.session.add(hashtag)
                    db.session.flush()  # Flush to get hashtag.id
                hashtag.posts_count += 1
                
                post_hashtag = PostHashtag(post_id=post.id, hashtag_id=hashtag.id)
                db.session.add(post_hashtag)
            
            try:
                db.session.commit()
                
                if is_flagged:
                    flash('Your post has been shared but flagged for review due to potentially harmful content.', 'warning')
                else:
                    flash('Your post has been shared successfully!', 'success')
                
                return redirect(url_for('feed'))
            except Exception as e:
                db.session.rollback()
                flash('Failed to share post. Please try again.', 'error')
                return render_template('upload.html', form=form)
        else:
            flash('Please select an image or video to upload.', 'error')
    
    return render_template('upload.html', form=form)

@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    # Filter NSFW posts when viewing other users' profiles
    if user.id == current_user.id:
        # Users can see their own NSFW posts
        posts = Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).all()
    else:
        # Hide NSFW posts when viewing other users' profiles
        posts = Post.query.filter_by(user_id=user.id, is_nsfw=False).order_by(Post.timestamp.desc()).all()
    
    # Check if current user is following this user
    is_following = current_user.is_following(user) if user != current_user else False
    
    return render_template('profile.html', user=user, posts=posts, is_following=is_following)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.bio = form.bio.data
        
        if form.profile_pic.data:
            # Generate unique filename for profile picture
            filename = str(uuid.uuid4()) + '.' + form.profile_pic.data.filename.rsplit('.', 1)[1].lower()
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'profiles', filename)
            
            # Save and process profile picture
            form.profile_pic.data.save(file_path)
            process_image(file_path, max_size=(400, 400))
            
            current_user.profile_pic = filename
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile', username=current_user.username))
    
    # Pre-populate form with current data
    form.bio.data = current_user.bio
    return render_template('edit_profile.html', form=form)

def safe_log(message, level='debug'):
    """Safe logging function to handle Windows pipe issues"""
    try:
        if level == 'debug':
            logger.debug(message)
        elif level == 'info':
            logger.info(message)
        elif level == 'warning':
            logger.warning(message)
        elif level == 'error':
            logger.error(message)
    except (OSError, IOError):
        # Silently ignore pipe errors to prevent crashes
        pass

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        safe_log(f"LOGIN: Login attempt for username: '{form.username.data}'")
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            safe_log(f"LOGIN: User found: {user.username}, ID: {user.id}")
            password_check = check_password_hash(user.password, form.password.data)
            safe_log(f"LOGIN: Password check result: {password_check}")
            if password_check:
                login_user(user)
                safe_log(f"LOGIN: Login successful for user: {user.username}")
                return redirect(url_for('feed'))
            else:
                safe_log(f"LOGIN: Password incorrect for user: {user.username}")
        else:
            safe_log(f"LOGIN: No user found with username: '{form.username.data}'")
        flash('Invalid username or password', 'error')
    else:
        if form.errors:
            safe_log(f"LOGIN: Login form validation errors: {form.errors}")
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            hashed_password = generate_password_hash(form.password.data)
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                password=hashed_password
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful!', 'success')
            safe_log(f"REGISTER: User '{form.username.data}' registered successfully with email '{form.email.data}'")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            safe_log(f"REGISTER: Registration failed: {e}", 'error')
            flash('Registration failed. Please try again.', 'error')
    else:
        # Log form errors for debugging
        if form.errors:
            safe_log(f"REGISTER: Form validation errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'error')
    
    return render_template('register.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    # Redirect to feed for Instagram-like experience
    return redirect(url_for('feed'))

@app.route('/follow/<username>')
@login_required
def follow(username):
    try:
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User not found.', 'error')
            return redirect(url_for('feed'))
        if user == current_user:
            flash('You cannot follow yourself!', 'error')
            return redirect(url_for('profile', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f'You are now following {username}!', 'success')
        return redirect(url_for('profile', username=username))
    except Exception as e:
        db.session.rollback()
        flash('Failed to follow user. Please try again.', 'error')
        return redirect(url_for('profile', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    try:
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User not found.', 'error')
            return redirect(url_for('feed'))
        if user == current_user:
            flash('You cannot unfollow yourself!', 'error')
            return redirect(url_for('profile', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You are no longer following {username}.', 'success')
        return redirect(url_for('profile', username=username))
    except Exception as e:
        db.session.rollback()
        flash('Failed to unfollow user. Please try again.', 'error')
        return redirect(url_for('profile', username=username))

@app.route('/api/follow/<username>', methods=['POST'])
@login_required
def toggle_follow_api(username):
    """AJAX endpoint for follow/unfollow actions"""
    try:
        user = User.query.filter_by(username=username).first()
        if user is None:
            return jsonify({'error': 'User not found'}), 404
        if user == current_user:
            return jsonify({'error': 'You cannot follow yourself'}), 400
        
        is_following = current_user.is_following(user)
        if is_following:
            current_user.unfollow(user)
            action = 'unfollowed'
        else:
            current_user.follow(user)
            action = 'followed'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'action': action,
            'is_following': not is_following,
            'followers_count': user.followers_count(),
            'message': f'You {action} {username}'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update follow status'}), 500

@app.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        if current_user.has_liked_post(post):
            current_user.unlike_post(post)
            liked = False
        else:
            current_user.like_post(post)
            liked = True
        db.session.commit()
        return jsonify({
            'liked': liked,
            'likes_count': post.likes_count()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update like status'}), 500

@app.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        content = request.json.get('content', '').strip()
        
        if not content:
            return jsonify({'error': 'Comment cannot be empty'}), 400
        
        if len(content) > 500:
            return jsonify({'error': 'Comment too long. Maximum 500 characters.'}), 400
        
        # Check for vulgar/inappropriate content in comment
        is_vulgar, vulgar_words, severity_score = detect_vulgar_content(content)
        
        # Block comment if vulgar content is detected
        if is_vulgar:
            print(f"🚫 BLOCKING COMMENT - Vulgar content detected: {vulgar_words}, severity: {severity_score}")
            return jsonify({
                'error': 'Your comment contains inappropriate content and cannot be posted. Please keep comments respectful and appropriate.',
                'blocked': True,
                'reason': 'inappropriate_content'
            }), 400
        
        # Check for crime-related content in comment (silent detection)
        crime_keywords, payment_keywords, xai_result = detect_flagged_content(content)
        flagged_keywords = crime_keywords + payment_keywords
        is_flagged = len(flagged_keywords) > 0
        
        comment = Comment(
            content=content,
            user_id=current_user.id,
            post_id=post_id,
            is_flagged=is_flagged,
            flagged_keywords=', '.join(flagged_keywords) if flagged_keywords else None
        )
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'username': current_user.username,
                'timestamp': comment.timestamp.strftime('%Y-%m-%d %H:%M'),
                'is_flagged': is_flagged
            },
            'comments_count': post.comments_count()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add comment'}), 500

@app.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    """Delete a post by the user who created it"""
    try:
        post = Post.query.get_or_404(post_id)
        
        # Check if the current user owns this post or is an admin
        if post.user_id != current_user.id and not current_user.is_admin:
            return jsonify({'error': 'You can only delete your own posts'}), 403
        
        print(f"🗑️ User {current_user.username} deleting post {post_id}")
        
        # Delete associated image file
        if post.image_filename:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'posts', post.image_filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🗑️ Deleted image file: {file_path}")
            else:
                print(f"⚠️ Image file not found: {file_path}")
        
        # Delete the post from database
        db.session.delete(post)
        db.session.commit()
        
        print(f"✅ Post {post_id} deleted successfully")
        return jsonify({'success': True, 'message': 'Post deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error deleting post {post_id}: {e}")
        return jsonify({'error': 'Failed to delete post'}), 500

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/chat/<username>')
@login_required
def chat(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found')
        return redirect(url_for('dashboard'))
    
    # Check if connected (follower or following)
    # Only allow chat if I follow them OR they follow me
    if not (current_user.id == user.id or current_user.is_following(user) or user.is_following(current_user)):
        flash('You can only message users you follow or who follow you.', 'warning')
        return redirect(url_for('profile', username=username))
    
    # Create room name (sorted usernames to ensure consistency)
    room_users = sorted([current_user.username, username])
    room_name = f"{room_users[0]}_{room_users[1]}"
    
    # Get chat history - filter based on admin status
    if current_user.is_admin:
        # Admin sees only flagged/spam messages for moderation
        messages = Message.query.filter_by(room=room_name, is_flagged=True).order_by(Message.timestamp).all()
        chat_mode = 'admin_moderation'
    else:
        # Regular users see all non-flagged messages
        messages = Message.query.filter_by(room=room_name, is_flagged=False).order_by(Message.timestamp).all()
        chat_mode = 'normal'
    
    return render_template('chat.html', user=user, room=room_name, messages=messages, chat_mode=chat_mode)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/api/users')
@login_required
def get_users():
    """API endpoint to get all users for chat functionality"""
    try:
        users = User.query.filter(User.id != current_user.id).all()
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'posts_count': user.posts_count(),
                'followers_count': user.followers_count(),
                'following_count': user.following_count()
            })
        return jsonify(users_data)
    except Exception as e:
        return jsonify({'error': 'Failed to load users'}), 500

@app.route('/api/suggestions')
@login_required
def get_suggestions():
    """API endpoint to get user suggestions for following"""
    try:
        # Get users that current user is not following and excluding self
        followed_user_ids = [user.id for user in current_user.followed.all()]
        suggestions = User.query.filter(
            User.id != current_user.id,
            ~User.id.in_(followed_user_ids)
        ).limit(5).all()
        
        suggestions_data = []
        for user in suggestions:
            suggestions_data.append({
                'id': user.id,
                'username': user.username,
                'posts_count': user.posts_count(),
                'followers_count': user.followers_count(),
                'following_count': user.following_count(),
                'bio': user.bio or 'No bio available',
                'profile_pic': user.profile_pic,
                'is_following': current_user.is_following(user)
            })
        return jsonify(suggestions_data)
    except Exception as e:
        return jsonify({'error': 'Failed to load suggestions'}), 500

@app.route('/api/current-user')
@login_required
def get_current_user():
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'bio': current_user.bio,
        'profile_pic': current_user.profile_pic
    })

@app.route('/api/xai-insights')
@login_required
def get_xai_insights():
    """Get XAI model insights and explanations"""
    if not xai_model:
        return jsonify({'error': 'XAI model not available'}), 404
    
    try:
        insights = xai_model.get_model_insights()
        return jsonify({
            'model_available': True,
            'insights': insights,
            'model_info': {
                'accuracy': 'Model trained with 92.2% accuracy',
                'categories': insights['model_params']['classes'],
                'feature_count': insights['model_params']['n_features']
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/xai-predict', methods=['POST'])
@login_required
def xai_predict():
    """Get XAI prediction for a specific text"""
    if not xai_model:
        return jsonify({'error': 'XAI model not available'}), 404
    
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'Text is required'}), 400
    
    try:
        result = xai_model.predict_with_explanation(text, explanation_type='both')
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/xai-performance')
@login_required
def get_xai_performance():
    """Get comprehensive XAI model performance metrics"""
    if not xai_model:
        return jsonify({'error': 'XAI model not available'}), 404
    
    try:
        from xai_performance_metrics import load_and_analyze_model
        
        # Load and analyze model performance
        result = load_and_analyze_model()
        if not result:
            return jsonify({'error': 'Could not analyze model performance'}), 500
        
        analyzer, performance_data = result
        
        # Get additional analysis
        performance_summary = analyzer.generate_performance_summary()
        threat_detection_stats = analyzer.get_threat_detection_stats()
        
        return jsonify({
            'performance_metrics': performance_data,
            'performance_summary': performance_summary,
            'threat_detection_stats': threat_detection_stats,
            'timestamp': performance_data.get('timestamp')
        })
        
    except Exception as e:
        return jsonify({'error': f'Performance analysis failed: {str(e)}'}), 500

@app.route('/api/chat-history/<username>')
@login_required
def get_chat_history(username):
    """API endpoint to get chat history with a specific user"""
    try:
        # Create room name (sorted usernames to ensure consistency)
        room_users = sorted([current_user.username, username])
        room_name = f"{room_users[0]}_{room_users[1]}"
        
        # Get messages from database - filter based on admin status
        if current_user.is_admin:
            # Admin sees only flagged/spam messages
            messages = Message.query.filter_by(room=room_name, is_flagged=True).order_by(Message.timestamp).all()
        else:
            # Regular users see all non-flagged messages
            messages = Message.query.filter_by(room=room_name, is_flagged=False).order_by(Message.timestamp).all()
        
        messages_data = []
        for message in messages:
            messages_data.append({
                'id': message.id,
                'username': message.author.username,
                'message': message.content,
                'timestamp': message.timestamp.strftime('%H:%M'),
                'is_flagged': message.is_flagged,
                'date': message.timestamp.strftime('%Y-%m-%d')
            })
        
        return jsonify({
            'room': room_name,
            'messages': messages_data
        })
    except Exception as e:
        safe_log(f"ERROR: Error loading chat history: {e}", 'error')
        return jsonify({'error': 'Failed to load chat history'}), 500

# ==================== ADMIN ROUTES ====================

@app.route('/admin/messages')
@login_required
@admin_required
def admin_messages():
    """Redirect to chat monitor since it works better for flagged messages"""
    return redirect(url_for('admin_chat_monitor'))

@app.route('/admin/chat-monitor')
@login_required
@admin_required
def admin_chat_monitor():
    """Admin chat monitoring - real-time view of flagged messages"""
    # Get all flagged messages grouped by room
    flagged_messages = Message.query.filter_by(is_flagged=True).order_by(Message.timestamp.desc()).all()
    
    # Group messages by room for better organization
    rooms_data = {}
    for message in flagged_messages:
        room = message.room
        if room not in rooms_data:
            rooms_data[room] = {
                'room_name': room,
                'participants': room.split('_'),
                'messages': [],
                'latest_message': None,
                'flagged_count': 0
            }
        
        rooms_data[room]['messages'].append(message)
        rooms_data[room]['flagged_count'] += 1
        if not rooms_data[room]['latest_message'] or message.timestamp > rooms_data[room]['latest_message'].timestamp:
            rooms_data[room]['latest_message'] = message
    
    # Convert to list and sort by latest activity
    rooms_list = list(rooms_data.values())
    rooms_list.sort(key=lambda x: x['latest_message'].timestamp if x['latest_message'] else datetime.min, reverse=True)
    
    return render_template('admin/chat_monitor.html', rooms=rooms_list)

@app.route('/admin/blocked-words')
@login_required
@admin_required
def admin_blocked_words():
    """Admin page for managing blocked words"""
    blocked_words = BlockedWord.query.order_by(BlockedWord.created_at.desc()).all()
    return render_template('admin/blocked_words.html', blocked_words=blocked_words)

@app.route('/admin/add-blocked-word', methods=['POST'])
@login_required
@admin_required
def add_blocked_word():
    """Add a new blocked word"""
    try:
        word = request.json.get('word', '').strip().lower()
        category = request.json.get('category', 'custom')
        severity = float(request.json.get('severity', 1.0))
        
        if not word:
            return jsonify({'error': 'Word cannot be empty'}), 400
        
        if len(word) > 100:
            return jsonify({'error': 'Word too long. Maximum 100 characters.'}), 400
        
        if severity < 0.1 or severity > 2.0:
            return jsonify({'error': 'Severity must be between 0.1 and 2.0'}), 400
        
        # Check if word already exists
        existing = BlockedWord.query.filter_by(word=word).first()
        if existing:
            return jsonify({'error': 'This word is already in the blocked list'}), 400
        
        # Add new blocked word
        blocked_word = BlockedWord(
            word=word,
            category=category,
            severity=severity,
            added_by=current_user.id
        )
        db.session.add(blocked_word)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Word "{word}" added to blocked list',
            'word': {
                'id': blocked_word.id,
                'word': blocked_word.word,
                'category': blocked_word.category,
                'severity': blocked_word.severity,
                'created_at': blocked_word.created_at.strftime('%Y-%m-%d %H:%M')
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Error adding word: {str(e)}'}), 500

@app.route('/admin/toggle-blocked-word/<int:word_id>', methods=['POST'])
@login_required
@admin_required
def toggle_blocked_word(word_id):
    """Toggle active status of a blocked word"""
    try:
        blocked_word = BlockedWord.query.get_or_404(word_id)
        blocked_word.is_active = not blocked_word.is_active
        db.session.commit()
        
        status = "activated" if blocked_word.is_active else "deactivated"
        return jsonify({
            'success': True,
            'message': f'Word "{blocked_word.word}" {status}',
            'is_active': blocked_word.is_active
        })
        
    except Exception as e:
        return jsonify({'error': f'Error toggling word: {str(e)}'}), 500

@app.route('/admin/delete-blocked-word/<int:word_id>', methods=['POST'])
@login_required
@admin_required
def delete_blocked_word(word_id):
    """Delete a blocked word"""
    try:
        blocked_word = BlockedWord.query.get_or_404(word_id)
        word_text = blocked_word.word
        db.session.delete(blocked_word)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Word "{word_text}" deleted from blocked list'
        })
        
    except Exception as e:
        return jsonify({'error': f'Error deleting word: {str(e)}'}), 500

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    form = AdminLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.is_admin and check_password_hash(user.password, form.password.data):
            login_user(user)
            safe_log(f"ADMIN: Admin login successful for user: {user.username}")
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'error')
            safe_log(f"ADMIN: Failed admin login attempt for username: {form.username.data}")
    return render_template('admin/login.html', form=form)

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard with overview statistics"""
    # Get system statistics
    total_users = User.query.count()
    total_posts = Post.query.count()
    total_comments = Comment.query.count()
    total_messages = Message.query.count()
    flagged_posts = Post.query.filter_by(is_flagged=True).count()
    flagged_comments = Comment.query.filter_by(is_flagged=True).count()
    flagged_messages = Message.query.filter_by(is_flagged=True).count()
    
    # Recent activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_users = User.query.filter(User.created_at >= week_ago).count()
    recent_posts = Post.query.filter(Post.timestamp >= week_ago).count()
    recent_flagged = (Post.query.filter(Post.timestamp >= week_ago, Post.is_flagged == True).count() +
                     Comment.query.filter(Comment.timestamp >= week_ago, Comment.is_flagged == True).count() +
                     Message.query.filter(Message.timestamp >= week_ago, Message.is_flagged == True).count())
    
    # Latest flagged content
    latest_flagged_posts = Post.query.filter_by(is_flagged=True).order_by(Post.timestamp.desc()).limit(5).all()
    latest_flagged_messages = Message.query.filter_by(is_flagged=True).order_by(Message.timestamp.desc()).limit(5).all()
    
    stats = {
        'total_users': total_users,
        'total_posts': total_posts,
        'total_comments': total_comments,
        'total_messages': total_messages,
        'flagged_posts': flagged_posts,
        'flagged_comments': flagged_comments,
        'flagged_messages': flagged_messages,
        'recent_users': recent_users,
        'recent_posts': recent_posts,
        'recent_flagged': recent_flagged,
        'latest_flagged_posts': latest_flagged_posts,
        'latest_flagged_messages': latest_flagged_messages
    }
    
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/admin/users')
@admin_required
def admin_users():
    """Admin user management page"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = User.query
    if search:
        query = query.filter(User.username.contains(search) | User.email.contains(search))
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/users.html', users=users, search=search)

@app.route('/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_user_admin(user_id):
    """Toggle admin status for a user"""
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('Cannot modify your own admin status', 'error')
        return redirect(url_for('admin_users'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    action = 'granted' if user.is_admin else 'revoked'
    flash(f'Admin privileges {action} for {user.username}', 'success')
    safe_log(f"ADMIN: Admin privileges {action} for user {user.username} by {current_user.username}")
    
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete a user account"""
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('Cannot delete your own account', 'error')
        return redirect(url_for('admin_users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {username} has been deleted', 'success')
    safe_log(f"ADMIN: User {username} deleted by admin {current_user.username}")
    
    return redirect(url_for('admin_users'))

@app.route('/admin/posts')
@admin_required
def admin_posts():
    """Admin post management page"""
    page = request.args.get('page', 1, type=int)
    show_flagged = request.args.get('flagged', '', type=str) == 'true'
    
    query = Post.query
    if show_flagged:
        query = query.filter_by(is_flagged=True)
    
    posts = query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/posts.html', posts=posts, show_flagged=show_flagged)

@app.route('/admin/posts/<int:post_id>/delete', methods=['POST'])
@admin_required
def admin_delete_post(post_id):
    """Delete a post"""
    post = Post.query.get_or_404(post_id)
    
    # Get author username before deletion to avoid DetachedInstanceError
    author_username = post.author.username
    
    # Delete associated file
    if post.image_filename:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'posts', post.image_filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    db.session.delete(post)
    db.session.commit()
    
    flash('Post has been deleted', 'success')
    safe_log(f"ADMIN: Post {post_id} by {author_username} deleted by admin {current_user.username}")
    
    return redirect(url_for('admin_posts'))

@app.route('/admin/posts/<int:post_id>/toggle-flag', methods=['POST'])
@admin_required
def admin_toggle_post_flag(post_id):
    """Toggle flagged status of a post"""
    post = Post.query.get_or_404(post_id)
    post.is_flagged = not post.is_flagged
    db.session.commit()
    
    
    # Get author username before deletion to avoid DetachedInstanceError
    author_username = message.author.username
    
    db.session.delete(message)
    db.session.commit()
    
    flash('Message has been deleted', 'success')
    safe_log(f"ADMIN: Message {message_id} by {author_username} deleted by admin {current_user.username}")
    
    return redirect(url_for('admin_messages'))

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    """Admin analytics and reporting page"""
    # Get comprehensive analytics data
    
    # User analytics
    total_users = User.query.count()
    admin_users = User.query.filter_by(is_admin=True).count()
    
    # Content analytics
    total_posts = Post.query.count()
    total_comments = Comment.query.count()
    total_messages = Message.query.count()
    
    # Flagged content analytics
    flagged_posts = Post.query.filter_by(is_flagged=True).count()
    flagged_comments = Comment.query.filter_by(is_flagged=True).count()
    flagged_messages = Message.query.filter_by(is_flagged=True).count()
    
    # Time-based analytics (last 30 days)
    month_ago = datetime.utcnow() - timedelta(days=30)
    
    # Daily user registrations (last 7 days)
    daily_users = []
    for i in range(7):
        day = datetime.utcnow() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        count = User.query.filter(
            User.created_at >= day_start,
            User.created_at < day_end
        ).count()
        
        daily_users.append({
            'date': day_start.strftime('%Y-%m-%d'),
            'count': count
        })
    
    # Daily flagged content (last 7 days)
    daily_flagged = []
    for i in range(7):
        day = datetime.utcnow() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        posts_count = Post.query.filter(
            Post.timestamp >= day_start,
            Post.timestamp < day_end,
            Post.is_flagged == True
        ).count()
        
        messages_count = Message.query.filter(
            Message.timestamp >= day_start,
            Message.timestamp < day_end,
            Message.is_flagged == True
        ).count()
        
        daily_flagged.append({
            'date': day_start.strftime('%Y-%m-%d'),
            'count': posts_count + messages_count
        })
    
    # XAI Model performance (if available)
    model_stats = {}
    if xai_model:
        try:
            # Get model insights
            insights = xai_model.get_model_insights()
            model_stats = {
                'available': True,
                'accuracy': '92.2%',  # From your model
                'categories': insights.get('model_params', {}).get('classes', []),
                'feature_count': insights.get('model_params', {}).get('n_features', 0)
            }
        except Exception as e:
            model_stats = {'available': False, 'error': str(e)}
    else:
        model_stats = {'available': False}
    
    analytics = {
        'users': {
            'total': total_users,
            'admins': admin_users,
            'daily_registrations': daily_users
        },
        'content': {
            'total_posts': total_posts,
            'total_comments': total_comments,
            'total_messages': total_messages,
            'flagged_posts': flagged_posts,
            'flagged_comments': flagged_comments,
            'flagged_messages': flagged_messages,
            'daily_flagged': daily_flagged
        },
        'model': model_stats
    }
    
    return render_template('admin/analytics.html', analytics=analytics)

@app.route('/admin/system')
@admin_required
def admin_system():
    """Admin system information and maintenance"""
    import psutil
    import platform
    
    # System information
    system_info = {
        'platform': platform.system(),
        'platform_release': platform.release(),
        'platform_version': platform.version(),
        'python_version': platform.python_version(),
        'cpu_count': psutil.cpu_count(),
        'memory_total': f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
        'memory_available': f"{psutil.virtual_memory().available / (1024**3):.2f} GB",
        'disk_usage': f"{psutil.disk_usage('/').percent}%"
    }
    
    # Database statistics
    db_stats = {
        'database_url': app.config['SQLALCHEMY_DATABASE_URI'],
        'tables': {
            'users': User.query.count(),
            'posts': Post.query.count(),
            'comments': Comment.query.count(),
            'messages': Message.query.count(),
            'hashtags': Hashtag.query.count()
        }
    }
    
    # XAI Model status
    xai_status = {
        'available': xai_model is not None,
        'model_file': 'xai_cybercrime_model.pkl',
        'lime_available': hasattr(xai_model, 'lime_explainer') if xai_model else False,
        'shap_available': hasattr(xai_model, 'shap_explainer') if xai_model else False
    }
    
    return render_template('admin/system.html', 
                         system_info=system_info, 
                         db_stats=db_stats, 
                         xai_status=xai_status)

# Socket Events
@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    safe_log(f"SOCKETIO: User {username} joining room {room}")
    join_room(room)
    emit('status', {'msg': username + ' has entered the chat.'}, room=room)
    safe_log(f"SOCKETIO: User {username} successfully joined room {room}")

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('status', {'msg': username + ' has left the chat.'}, room=room)

@socketio.on('message')
def handle_message(data):
    try:
        room = sanitize_input(data.get('room', ''))
        message_content = sanitize_input(data.get('message', ''))
        
        safe_log(f"SOCKETIO: Received message - Room: {room}, Message: {message_content}, From: {current_user.username}")
        
        if not room or not message_content:
            safe_log(f"SOCKETIO: Message rejected - Empty room or message")
            return
        
        if len(message_content) > 1000:  # Limit message length
            return
        
        # Content detection with XAI (crime/suspicious activity)
        crime_keywords, payment_keywords, xai_result = detect_flagged_content(message_content)
        all_flagged_keywords = crime_keywords + payment_keywords
        is_flagged = len(all_flagged_keywords) > 0
        flag_type = 'crime' if crime_keywords else 'payment' if payment_keywords else None
        
        # Only flag messages with crime/suspicious activity keywords
        if flag_type not in ['crime', 'payment']:
            is_flagged = False

        # ── Phishing URL Detection ──────────────────────────────────
        phishing_results = check_urls_in_message(message_content)
        phishing_urls = [r for r in phishing_results if r.get('is_phishing')]
        has_phishing_url = len(phishing_urls) > 0

        # If any URL is flagged as phishing, also mark the message as flagged
        if has_phishing_url:
            is_flagged = True
            if not flag_type:
                flag_type = 'phishing'
        # ────────────────────────────────────────────────────────────

        room_users = room.split('_')
        recipient_username = None
        if len(room_users) == 2:
            recipient_username = room_users[1] if room_users[0] == current_user.username else room_users[0]
        
        recipient = User.query.filter_by(username=recipient_username).first() if recipient_username else None
        
        # Save message to database
        message = Message(
            content=message_content,
            user_id=current_user.id,
            recipient_id=recipient.id if recipient else None,
            room=room,
            is_flagged=is_flagged,
            flagged_keywords=', '.join(all_flagged_keywords) if all_flagged_keywords else None
        )
        db.session.add(message)
        db.session.commit()
        
        message_data = {
            'username': current_user.username,
            'message': message_content,
            'timestamp': message.timestamp.strftime('%H:%M'),
            'is_flagged': is_flagged,
            'flagged_keywords': all_flagged_keywords,
            'flag_type': flag_type,
            'xai_prediction': xai_result.get('predicted_category') if xai_result else None,
            'xai_confidence': xai_result.get('confidence') if xai_result else None,
            'xai_explanation': xai_result.get('explanations') if xai_result else None,
            # Phishing scan results
            'phishing_results': phishing_results,
            'has_phishing_url': has_phishing_url,
        }
        
        safe_log(f"SOCKETIO: Emitting message to room {room}: {message_data}")
        emit('message', message_data, room=room)
        safe_log(f"SOCKETIO: Message emitted successfully to room {room}")
        
        # If flagged content detected, send different alerts
        if is_flagged:
            # Alert for sender (prevention/warning)
            sender_alert = {
                'type': 'sender_warning',
                'flag_type': flag_type,
                'message': get_sender_warning_message(flag_type) if flag_type in ['crime', 'payment'] else '⚠️ Phishing URL detected in your message!',
                'keywords': all_flagged_keywords,
                'username': current_user.username,
                'xai_prediction': xai_result.get('predicted_category') if xai_result else None,
                'xai_confidence': xai_result.get('confidence') if xai_result else None,
                'xai_explanation': xai_result.get('explanations', {}).get('lime') if xai_result else None,
                'phishing_results': phishing_results,
            }
            emit('sender_warning', sender_alert, room=request.sid)
            
            # Alert for receiver (caution/awareness)
            if recipient:
                receiver_alert = {
                    'type': 'receiver_warning',
                    'flag_type': flag_type,
                    'message': get_receiver_warning_message(flag_type) if flag_type in ['crime', 'payment'] else '🚨 A phishing link was detected in this message!',
                    'keywords': all_flagged_keywords,
                    'sender_username': current_user.username,
                    'xai_prediction': xai_result.get('predicted_category') if xai_result else None,
                    'xai_confidence': xai_result.get('confidence') if xai_result else None,
                    'xai_explanation': xai_result.get('explanations', {}).get('lime') if xai_result else None,
                    'phishing_results': phishing_results,
                }
                emit('receiver_warning', receiver_alert, room=room, include_self=False)

        # Send dedicated phishing alert to RECEIVER only (even if no other flag)
        if has_phishing_url and recipient:
            phishing_alert = {
                'type': 'phishing_alert',
                'phishing_urls': phishing_urls,
                'sender_username': current_user.username,
            }
            emit('phishing_alert', phishing_alert, room=room, include_self=False)

    except Exception as e:
        db.session.rollback()
        safe_log(f"ERROR: Error handling message: {e}", 'error')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Find and print local IP address
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print("\n" + "="*50)
        print(f"🚀 Server is running!")
        print(f"🔗 Local:   http://127.0.0.1:5000")
        print(f"🌐 Network: http://{local_ip}:5000")
        print("="*50 + "\n")
    except Exception:
        print("\n🚀 Server starting on http://0.0.0.0:5000\n")

    # Configure for Windows compatibility
    socketio.run(
        app, 
        debug=True, 
        host='0.0.0.0', 
        port=5000,
        use_reloader=False,  # Disable reloader to prevent pipe issues on Windows
        log_output=False     # Disable SocketIO logging to prevent pipe conflicts
    )
