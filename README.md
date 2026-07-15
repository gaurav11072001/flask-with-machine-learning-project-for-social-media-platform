# InstaShare - Instagram-Like Social Media Platform

A Flask-based social media platform inspired by Instagram with full photo/video sharing, real-time messaging, and advanced AI content monitoring. Share your moments, connect with friends, and discover amazing content while staying protected by our intelligent content filtering system.

## 🚀 Features

### Core Instagram-Like Functionality
- **Photo & Video Sharing**: Upload and share high-quality photos and videos
- **Feed System**: Personalized feed showing posts from followed users
- **User Profiles**: Complete profile pages with bio, follower/following counts
- **Likes & Comments**: Engage with posts through likes and comments
- **Follow System**: Follow/unfollow users to customize your feed
- **Stories**: 24-hour temporary content sharing (UI ready)
- **Explore Page**: Discover trending content and new users
- **Direct Messaging**: Private messaging between users
- **Hashtags**: Tag posts and discover content by topics

### Advanced Features
- **Real-time Updates**: WebSocket-powered live interactions
- **File Upload**: Support for images (JPG, PNG, GIF) and videos (MP4, MOV)
- **Image Processing**: Automatic image optimization and resizing
- **Responsive Design**: Mobile-first approach works on all devices
- **Modern UI**: Instagram-inspired interface with smooth animations

### Security Features (Silent Background Monitoring)
- **AI Content Monitoring**: Silent detection of harmful content
- **Crime Detection**: Background analysis of posts and comments
- **Content Flagging**: Automatic flagging without user disruption
- **Safety Logging**: Comprehensive security event tracking
- **Community Protection**: Proactive harmful content prevention

### Technical Features
- **WebSocket Communication**: Real-time bidirectional communication
- **SQLite Database**: Lightweight database for users and messages
- **Responsive Design**: Mobile-first approach with modern CSS
- **Form Validation**: Client and server-side validation
- **Password Security**: Bcrypt hashing for secure password storage

## 🛠️ Technology Stack

### Backend
- **Flask** - Python web framework
- **Flask-SocketIO** - WebSocket support
- **Flask-SQLAlchemy** - Database ORM
- **Flask-Login** - User session management
- **Flask-WTF** - Form handling and validation
- **Bcrypt** - Password hashing

### Frontend
- **Bootstrap 5** - CSS framework
- **Socket.IO** - Real-time communication
- **AOS** - Animate On Scroll library
- **Font Awesome** - Icon library
- **Custom CSS** - Modern styling and animations

### Database
- **SQLite** - Lightweight database for development

## 📦 Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Setup Instructions

1. **Clone or download the project files**
   ```bash
   # Navigate to your project directory
   cd d:\mc0012
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   ```bash
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser and visit**
   ```
   http://localhost:5000
   ```

## 🚦 Usage

### Getting Started

1. **Register a new account**
   - Visit the homepage and click "Get Started"
   - Fill in your username and password (minimum 8 characters)
   - Username must be 4-20 characters long

2. **Login to your account**
   - Use your credentials to sign in
   - You'll be redirected to the dashboard

3. **Start chatting**
   - Click on any available user to start a chat
   - Type messages in the chat input field
   - Messages are sent in real-time using WebSocket technology

### Crime Detection System

The AI-powered crime detection system monitors all conversations for:

- **Violence-related keywords**: kill, murder, attack, violence, etc.
- **Weapon mentions**: bomb, gun, knife, explosive, etc.
- **Criminal activities**: robbery, fraud, blackmail, kidnap, etc.
- **Illegal substances**: drugs, cocaine, heroin, etc.
- **Threatening language**: threat, harm, revenge, etc.

When harmful content is detected:
- ⚠️ **Instant Alert**: Modal popup appears with security warning
- 🚨 **Content Flagging**: Message is marked with warning indicator  
- 📱 **Browser Notification**: Desktop notification (if permissions granted)
- 📊 **Security Logging**: Event is logged for monitoring

### User Interface Features

#### Homepage
- Modern hero section with animated elements
- Feature showcase with security benefits
- Responsive design for all devices

#### Authentication
- Secure login/register forms with validation
- Password strength indicator
- Social login options (UI only)

#### Dashboard
- User list with online status indicators
- Security status monitoring
- Modern sidebar navigation

#### Chat Interface
- Real-time messaging with typing indicators
- Message timestamps and status
- Security alerts and flagged content warnings
- Mobile-responsive chat interface

## 🔧 Configuration

### Environment Variables
You can create a `.env` file to configure the application:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///social_media.db
DEBUG=True
```

### Security Settings
The crime detection keywords can be modified in `app.py`:

```python
CRIME_KEYWORDS = [
    'kill', 'murder', 'bomb', 'terrorist', 'weapon', 
    # Add or remove keywords as needed
]
```

## 📁 Project Structure

```
d:\mc0012/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Homepage
│   ├── login.html       # Login page
│   ├── register.html    # Registration page
│   ├── dashboard.html   # User dashboard
│   └── chat.html        # Chat interface
└── static/              # Static files
    ├── css/
    │   └── style.css    # Custom CSS styles
    └── js/
        └── main.js      # JavaScript functionality
```

## 🔒 Security Features

### Crime Detection Algorithm
- **Keyword Matching**: Pattern-based detection of harmful terms
- **Threat Level Analysis**: Severity scoring system
- **Real-time Processing**: Instant analysis of all messages
- **False Positive Reduction**: Context-aware keyword matching

### Data Protection
- **Password Hashing**: Bcrypt encryption for all passwords
- **Session Security**: Flask-Login session management
- **CSRF Protection**: Flask-WTF form protection
- **Input Validation**: Server-side validation for all inputs

### Privacy Considerations
- **Local Storage**: All data stored locally in SQLite
- **No External APIs**: Crime detection runs locally
- **User Control**: Users can see flagged content warnings
- **Transparent Logging**: Security events logged for review

## 🎨 Customization

### Styling
Modify `static/css/style.css` to customize:
- Color scheme and themes
- Animation effects
- Layout and spacing
- Component styling

### Crime Detection
Update `app.py` to modify:
- Detection keywords and patterns
- Threat level thresholds
- Alert behavior
- Logging preferences

### UI Components
Edit templates in `templates/` to:
- Change page layouts
- Add new features
- Modify form fields
- Update navigation

## 🚀 Deployment

### Local Development
The application runs on `http://localhost:5000` by default for development.

### Production Deployment
For production deployment:

1. **Set environment variables**:
   ```bash
   export SECRET_KEY="your-production-secret-key"
   export DATABASE_URL="your-production-database-url"
   ```

2. **Use a production WSGI server**:
   ```bash
   pip install gunicorn
   gunicorn app:app
   ```

3. **Configure web server** (Nginx/Apache) for static files and reverse proxy

## 🐛 Troubleshooting

### Common Issues

**WebSocket Connection Failed**
- Check if port 5000 is available
- Verify firewall settings
- Try different browser or incognito mode

**Database Errors**
- Delete `social_media.db` and restart app
- Check file permissions in project directory
- Ensure SQLite is properly installed

**CSS/JS Not Loading**
- Clear browser cache
- Check file paths in templates
- Verify static files are in correct directories

**Crime Detection Not Working**
- Check browser console for JavaScript errors
- Verify Socket.IO connection is established
- Test with known trigger words

## 📝 License

This project is created for educational and demonstration purposes. Feel free to modify and use according to your needs.

## 🤝 Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support or questions:
- Check the troubleshooting section
- Review the code comments
- Test with minimal examples
- Check browser developer tools

## 🔮 Future Enhancements

Potential improvements:
- **Machine Learning**: Advanced AI models for better detection
- **Multi-language Support**: Detect harmful content in multiple languages
- **User Reporting**: Allow users to report suspicious content
- **Admin Dashboard**: Management interface for administrators
- **File Sharing**: Support for image and file sharing
- **Group Chats**: Multi-user chat rooms
- **Push Notifications**: Mobile app notifications
- **Voice/Video Chat**: WebRTC integration

---

**SecureChat** - Making online communication safer with AI-powered security! 🛡️💬#   f l a s k - w i t h - m a c h i n e - l e a r n i n g - p r o j e c t - f o r - s o c i a l - m e d i a - p l a t f o r m  
 