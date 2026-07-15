# Flask Social Media Platform with Machine Learning

A Flask-based social media platform inspired by Instagram with advanced AI-powered content monitoring and security features.

## 🚀 Features

### Core Functionality
- **Photo & Video Sharing**: Upload and share high-quality photos and videos
- **Real-time Messaging**: Chat with friends in real-time
- **Personalized Feed**: See posts from people you follow
- **User Profiles**: Customizable profiles with bio and profile pictures
- **Social Interactions**: Like, comment, and engage with posts

### AI-Powered Security
- **NSFW Detection**: Automatic detection and filtering of inappropriate content
- **Phishing Detection**: Machine learning-based detection of malicious links and phishing attempts
- **Cybercrime Analysis**: Advanced analysis using machine learning models
- **Content Moderation**: Intelligent content filtering system

### Admin Features
- **Admin Dashboard**: Comprehensive admin panel for platform management
- **User Management**: Monitor and manage user accounts
- **Content Moderation Tools**: Review and moderate flagged content

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Machine Learning**: Scikit-learn, NLTK, TensorFlow/Keras
- **Frontend**: HTML, CSS, JavaScript

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/gaurav11072001/flask-with-machine-learning-project-for-social-media-platform.git
cd flask-with-machine-learning-project-for-social-media-platform
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download NLTK data:
```bash
python download_nltk_data.py
```

5. Initialize the database:
```bash
python migrate_database.py
```

6. Create an admin user:
```bash
python create_admin_user.py
```

## 🚀 Running the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 📁 Project Structure

```
.
├── app.py                          # Main application file
├── phishing_detector.py            # Phishing detection module
├── feature_analysis.py             # ML feature analysis
├── cybercrime_dataset.py           # Cybercrime dataset handler
├── instance/
│   └── social_media.db            # SQLite database
├── static/                         # Static files (CSS, JS, images)
└── templates/                      # HTML templates
```

## 🔒 Security Features

- Content warning system for sensitive content
- NSFW content detection and filtering
- Phishing link detection in posts and messages
- Admin moderation tools

## 📚 Documentation

- [Admin System Documentation](ADMIN_SYSTEM_DOCUMENTATION.md)
- [Chat Functionality Guide](CHAT_FUNCTIONALITY_GUIDE.md)
- [NSFW Detection Guide](NSFW_DETECTION_GUIDE.md)
- [Phishing Detection Guide](PHISHING_DETECTION_GUIDE.md)
- [Content Warning Implementation](CONTENT_WARNING_IMPLEMENTATION.md)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 👤 Author

**Gaurav**
- GitHub: [@gaurav11072001](https://github.com/gaurav11072001)

## 🙏 Acknowledgments

- Inspired by Instagram's user interface and functionality
- Machine learning models for content safety and security
