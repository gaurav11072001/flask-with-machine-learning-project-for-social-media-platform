// Main JavaScript file for SecureChat
// Initialize AOS (Animate On Scroll)
document.addEventListener('DOMContentLoaded', function () {
    AOS.init({
        duration: 800,
        easing: 'ease-in-out',
        once: true,
        offset: 100
    });
});

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const href = this.getAttribute('href');
        // Only process valid selectors (not just '#' or empty)
        if (href && href.length > 1 && href !== '#') {
            try {
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            } catch (error) {
                console.warn('Invalid selector:', href, error);
            }
        }
    });
});

// Navbar scroll effect
window.addEventListener('scroll', function () {
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    }
});

// Form validation utilities
class FormValidator {
    static validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    static validatePassword(password) {
        // At least 8 characters, 1 uppercase, 1 lowercase, 1 number
        const minLength = password.length >= 8;
        const hasUpper = /[A-Z]/.test(password);
        const hasLower = /[a-z]/.test(password);
        const hasNumber = /\d/.test(password);

        return {
            valid: minLength && hasUpper && hasLower && hasNumber,
            strength: (minLength ? 25 : 0) + (hasUpper ? 25 : 0) + (hasLower ? 25 : 0) + (hasNumber ? 25 : 0)
        };
    }

    static validateUsername(username) {
        const minLength = username.length >= 4;
        const maxLength = username.length <= 20;
        const validChars = /^[a-zA-Z0-9_]+$/.test(username);

        return minLength && maxLength && validChars;
    }
}

// Crime Detection Client-Side
class CrimeDetector {
    constructor() {
        this.suspiciousPatterns = [
            /\b(kill|murder|bomb|terrorist|weapon|gun|knife|attack)\b/gi,
            /\b(violence|threat|blackmail|ransom|kidnap|abuse|assault)\b/gi,
            /\b(robbery|steal|fraud|scam|drug dealing|cocaine|heroin)\b/gi,
            /\b(methamphetamine|illegal|criminal|crime|felony)\b/gi
        ];

        this.warningWords = [
            'harm', 'hurt', 'revenge', 'destroy', 'eliminate', 'terminate',
            'explosive', 'ammunition', 'firearms', 'dangerous', 'toxic'
        ];
    }

    analyzeThreatLevel(text) {
        let threatLevel = 0;
        const foundPatterns = [];

        this.suspiciousPatterns.forEach(pattern => {
            const matches = text.match(pattern);
            if (matches) {
                threatLevel += matches.length * 2;
                foundPatterns.push(...matches);
            }
        });

        this.warningWords.forEach(word => {
            if (text.toLowerCase().includes(word)) {
                threatLevel += 1;
                foundPatterns.push(word);
            }
        });

        return {
            level: threatLevel,
            severity: this.getSeverity(threatLevel),
            keywords: [...new Set(foundPatterns)]
        };
    }

    getSeverity(level) {
        if (level >= 8) return 'critical';
        if (level >= 5) return 'high';
        if (level >= 3) return 'medium';
        if (level >= 1) return 'low';
        return 'safe';
    }
}

// Chat functionality
class ChatManager {
    constructor() {
        this.socket = null;
        this.currentRoom = null;
        this.currentUser = null;
        this.crimeDetector = new CrimeDetector();
        this.typingUsers = new Set();
        this.messageHistory = [];

        this.initializeChat();
    }

    initializeChat() {
        if (typeof io !== 'undefined') {
            this.socket = io();
            this.setupSocketListeners();
        }
    }

    setupSocketListeners() {
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.updateConnectionStatus(true);
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.updateConnectionStatus(false);
        });

        this.socket.on('message', (data) => {
            this.displayMessage(data);
            this.messageHistory.push(data);
        });

        this.socket.on('sender_warning', (data) => {
            this.showSenderWarning(data);
        });

        this.socket.on('receiver_warning', (data) => {
            this.showReceiverWarning(data);
        });

        this.socket.on('crime_alert', (data) => {
            this.showCrimeAlert(data);
        });

        this.socket.on('typing', (data) => {
            this.showTypingIndicator(data);
        });

        this.socket.on('stop_typing', (data) => {
            this.hideTypingIndicator(data);
        });

        this.socket.on('phishing_alert', (data) => {
            this.showPhishingToast(data.phishing_urls, data.sender_username);
        });

        this.socket.on('status', (data) => {
            this.showStatusMessage(data.msg);
        });
    }

    joinRoom(room, username) {
        console.log('ChatManager joinRoom called:', { room, username });
        this.currentRoom = room;
        this.currentUser = username;

        if (this.socket) {
            console.log('Emitting join event:', { room, username });
            this.socket.emit('join', {
                room: room,
                username: username
            });
        } else {
            console.error('No socket connection for joining room');
        }
    }

    leaveRoom() {
        if (this.socket && this.currentRoom && this.currentUser) {
            this.socket.emit('leave', {
                room: this.currentRoom,
                username: this.currentUser
            });
        }
    }

    sendMessage(message) {
        console.log('ChatManager sendMessage called:', { message, room: this.currentRoom, user: this.currentUser });

        if (!this.socket) {
            console.error('No socket connection');
            return false;
        }

        if (!this.currentRoom) {
            console.error('No current room set');
            return false;
        }

        if (!message.trim()) {
            console.error('Empty message');
            return false;
        }

        // Client-side threat analysis
        const analysis = this.crimeDetector.analyzeThreatLevel(message);

        if (analysis.severity === 'critical' || analysis.severity === 'high') {
            this.showPreventiveWarning(analysis);
            return false;
        }

        console.log('Emitting message:', { room: this.currentRoom, message });
        this.socket.emit('message', {
            room: this.currentRoom,
            message: message
        });

        return true;
    }

    renderMessageContent(rawText, phishingResults) {
        const urlRegex = /((?:https?:\/\/|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}\/)(?:[^\s()<>]+|\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))*\))+(?:\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»""'']))/gi;
        const phishingMap = {};
        if (phishingResults && phishingResults.length) {
            phishingResults.forEach(r => { phishingMap[r.url] = r; });
        }
        const escaped = this.escapeHtml(rawText);
        return escaped.replace(urlRegex, function (url) {
            const r = phishingMap[url];
            const href = url.startsWith('http') ? url : 'https://' + url;
            if (r && r.is_phishing) {
                return `<span class="phishing-url-wrap d-block mt-2 mb-2 p-1 border border-danger rounded" style="background:rgba(220,53,69,0.1)">`
                    + `<i class="fas fa-skull-crossbones text-danger me-1"></i>`
                    + `<a href="javascript:void(0)" style="cursor: not-allowed; opacity: 0.7; pointer-events: none; text-decoration: line-through !important;" class="text-danger fw-bold">${url}</a>`
                    + ` <span class="badge bg-danger ms-1" style="font-size:0.65rem;">⚠️ Phishing ${r.confidence}%</span>`
                    + `<div class="text-danger small mt-1" style="font-size: 0.7rem; font-weight: 500;"><i class="fas fa-hand-paper me-1"></i>Link blocked for your protection</div>`
                    + `</span>`;
            } else if (r) {
                return `<span class="safe-url-wrap d-block mt-2 mb-2">`
                    + `<i class="fas fa-shield-halved text-success me-1"></i>`
                    + `<a href="${href}" target="_blank" rel="noopener noreferrer" class="text-info text-decoration-underline">${url}</a>`
                    + ` <span class="badge bg-success ms-1" style="font-size:0.65rem;">✔ Safe</span>`
                    + `</span>`;
            } else {
                return `<a href="${href}" target="_blank" rel="noopener noreferrer" class="text-info text-decoration-underline">${url}</a>`;
            }
        });
    }

    displayMessage(data) {
        const messagesContainer = document.getElementById('chatMessages');
        if (!messagesContainer) return;

        const messageDiv = document.createElement('div');
        const messageClass = data.username === this.currentUser ? 'sent' : 'received';
        const flaggedClass = data.is_flagged ? ' flagged' : '';

        const renderedContent = this.renderMessageContent(data.message, data.phishing_results || []);

        messageDiv.className = `message ${messageClass} animate-fade-in-up`;
        messageDiv.innerHTML = `
            <div class="message-content${flaggedClass}">
                ${renderedContent}
                ${data.is_flagged && data.flag_type !== 'phishing' ? `
                    <div class="flagged-indicator">
                        <i class="fas fa-exclamation-triangle text-warning"></i>
                        <small>Flagged content</small>
                    </div>
                ` : ''}
            </div>
            <div class="message-time">${data.timestamp}</div>
        `;

        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();

        // Add sound notification for received messages
        if (data.username !== this.currentUser) {
            this.playMessageSound();
        }
    }

    showSenderWarning(data) {
        const modal = document.getElementById('senderWarningModal');
        if (modal) {
            // Update modal content based on flag type
            const titleElement = document.getElementById('senderWarningTitle');
            const messageElement = document.getElementById('senderWarningMessage');
            const keywordsElement = document.getElementById('senderFlaggedKeywords');

            if (data.flag_type === 'crime') {
                titleElement.textContent = 'Security Warning';
            } else if (data.flag_type === 'payment') {
                titleElement.textContent = 'Financial Security Alert';
            } else if (data.flag_type === 'phishing') {
                titleElement.textContent = 'Phishing Security Alert';
            }

            messageElement.textContent = data.message;
            keywordsElement.textContent = data.keywords.join(', ');

            // Store XAI data for later use
            this.storeXAIData('sender', data);

            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
        }

        // Play warning sound
        this.playAlertSound();

        // Log security event
        this.logSecurityEvent({
            type: 'sender_warning',
            flag_type: data.flag_type,
            keywords: data.keywords,
            username: data.username,
            xai_data: {
                prediction: data.xai_prediction,
                confidence: data.xai_confidence,
                explanation: data.xai_explanation
            }
        });
    }

    showReceiverWarning(data) {
        const modal = document.getElementById('receiverWarningModal');
        if (modal) {
            // Update modal content based on flag type
            const titleElement = document.getElementById('receiverWarningTitle');
            const messageElement = document.getElementById('receiverWarningMessage');
            const senderElement = document.getElementById('receiverSenderName');
            const keywordsElement = document.getElementById('receiverFlaggedKeywords');

            if (data.flag_type === 'crime') {
                titleElement.textContent = 'Security Alert';
            } else if (data.flag_type === 'payment') {
                titleElement.textContent = 'Financial Safety Warning';
            } else if (data.flag_type === 'phishing') {
                titleElement.textContent = 'Phishing Warning';
            }

            messageElement.textContent = data.message;
            senderElement.textContent = data.sender_username;
            keywordsElement.textContent = data.keywords.join(', ');

            // Store XAI data for later use
            this.storeXAIData('receiver', data);

            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
        }

        // Show browser notification
        const notificationTitle = data.flag_type === 'crime' ? 'Security Alert' : data.flag_type === 'phishing' ? 'Phishing URL Warning' : 'Financial Safety Warning';
        this.showBrowserNotification(notificationTitle, data.message.substring(0, 100) + '...');

        // Play alert sound
        this.playAlertSound();

        // Log security event
        this.logSecurityEvent({
            type: 'receiver_warning',
            flag_type: data.flag_type,
            keywords: data.keywords,
            sender_username: data.sender_username,
            xai_data: {
                prediction: data.xai_prediction,
                confidence: data.xai_confidence,
                explanation: data.xai_explanation
            }
        });
    }

    showPhishingToast(phishingUrls, senderUsername) {
        // Remove existing toast if any
        const existing = document.getElementById('phishingToast');
        if (existing) existing.remove();

        const toast = document.createElement('div');
        toast.id = 'phishingToast';
        toast.style.cssText = 'position:fixed; top:80px; right:20px; z-index:9999; width:320px; background:rgba(15, 10, 25, 0.95); backdrop-filter:blur(10px); border:1px solid rgba(220, 53, 69, 0.4); border-radius:12px; box-shadow:0 10px 30px rgba(0,0,0,0.5); padding:15px; color:white; animation:slideIn 0.3s ease-out;';

        const senderLabel = senderUsername === 'You' ? 'You' : `User ${senderUsername}`;
        const urlList = phishingUrls.map(u => `<li><code>${u.url}</code> (${u.confidence}% match)</li>`).join('');

        toast.innerHTML = `
            <div class="d-flex align-items-center mb-2">
                <div class="me-2 text-danger"><i class="fas fa-skull-crossbones fa-lg"></i></div>
                <div class="fw-bold fs-6">Security Alert: Phishing Link</div>
                <button type="button" class="btn-close btn-close-white ms-auto" style="font-size:0.7rem;" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
            <div class="toast-body p-0">
                <p class="mb-1 small text-white-50">
                    <strong>${senderLabel}</strong> shared a link flagged as malicious:
                </p>
                <ul class="mb-2 ps-3 small text-danger">${urlList}</ul>
                <div class="p-2 rounded bg-danger bg-opacity-10 border border-danger border-opacity-20">
                    <p class="mb-0 text-danger small" style="font-size:0.7rem;">
                        <i class="fas fa-exclamation-triangle me-1"></i><strong>DO NOT CLICK:</strong> This link is designed to steal your credentials or infect your device.
                    </p>
                </div>
            </div>`;
        document.body.appendChild(toast);
        setTimeout(() => { if (document.getElementById('phishingToast')) toast.remove(); }, 12000);
    }

    showCrimeAlert(data) {
        // Legacy method for backward compatibility
        // Show modal alert
        const modal = document.getElementById('crimeAlertModal');
        if (modal) {
            const keywordsElement = document.getElementById('flaggedKeywords');
            if (keywordsElement) {
                keywordsElement.textContent = data.keywords.join(', ');
            }

            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
        }

        // Show browser notification if supported
        this.showBrowserNotification('Security Alert', 'Potentially harmful content detected in conversation');

        // Play alert sound
        this.playAlertSound();

        // Add to security log
        this.logSecurityEvent(data);
    }

    showPreventiveWarning(analysis) {
        const warningHtml = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <h6><i class="fas fa-shield-alt me-2"></i>Message Blocked</h6>
                <p class="mb-1">Your message contains potentially harmful content and has been blocked.</p>
                <small><strong>Detected keywords:</strong> ${analysis.keywords.join(', ')}</small>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        const alertContainer = document.createElement('div');
        alertContainer.innerHTML = warningHtml;
        document.querySelector('.chat-input').prepend(alertContainer.firstElementChild);

        setTimeout(() => {
            const alert = document.querySelector('.alert-danger');
            if (alert) {
                alert.remove();
            }
        }, 5000);
    }

    showTypingIndicator(data) {
        if (data.username !== this.currentUser) {
            this.typingUsers.add(data.username);
            this.updateTypingDisplay();
        }
    }

    hideTypingIndicator(data) {
        this.typingUsers.delete(data.username);
        this.updateTypingDisplay();
    }

    updateTypingDisplay() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (!typingIndicator) return;

        if (this.typingUsers.size > 0) {
            const users = Array.from(this.typingUsers);
            const text = users.length === 1 ?
                `${users[0]} is typing...` :
                `${users.join(', ')} are typing...`;

            typingIndicator.querySelector('.typing-text').textContent = text;
            typingIndicator.style.display = 'flex';
        } else {
            typingIndicator.style.display = 'none';
        }
    }

    updateConnectionStatus(connected) {
        const statusElements = document.querySelectorAll('.connection-status');
        statusElements.forEach(el => {
            el.className = `connection-status ${connected ? 'connected' : 'disconnected'}`;
            el.textContent = connected ? 'Connected' : 'Disconnected';
        });
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chatMessages');
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    showStatusMessage(message) {
        const messagesContainer = document.getElementById('chatMessages');
        if (!messagesContainer) return;

        const statusDiv = document.createElement('div');
        statusDiv.className = 'status-message text-center my-2';
        statusDiv.innerHTML = `<small class="text-muted">${this.escapeHtml(message)}</small>`;

        messagesContainer.appendChild(statusDiv);
        this.scrollToBottom();
    }

    playMessageSound() {
        try {
            const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmASBjmN0fPTeS0EK3zJ8t2OPwsUYLnp7KdUFAk');
            audio.volume = 0.3;
            audio.play();
        } catch (e) {
            console.log('Audio not supported');
        }
    }

    playAlertSound() {
        try {
            const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmASBjmN0fPTeS0EK3zJ8t2OPwsUYLnp7KdUFAm');
            audio.volume = 0.7;
            audio.play();
        } catch (e) {
            console.log('Audio not supported');
        }
    }

    showBrowserNotification(title, message) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: message,
                icon: '/static/favicon.ico'
            });
        }
    }

    logSecurityEvent(data) {
        const securityLog = JSON.parse(localStorage.getItem('securityLog') || '[]');
        securityLog.push({
            timestamp: new Date().toISOString(),
            type: 'crime_alert',
            keywords: data.keywords,
            username: data.username,
            room: this.currentRoom
        });

        // Keep only last 100 events
        if (securityLog.length > 100) {
            securityLog.splice(0, securityLog.length - 100);
        }

        localStorage.setItem('securityLog', JSON.stringify(securityLog));
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    storeXAIData(type, data) {
        // Store XAI data for the toggle functionality
        if (type === 'sender') {
            this.senderXAIData = {
                prediction: data.xai_prediction,
                confidence: data.xai_confidence,
                explanation: data.xai_explanation
            };
        } else if (type === 'receiver') {
            this.receiverXAIData = {
                prediction: data.xai_prediction,
                confidence: data.xai_confidence,
                explanation: data.xai_explanation
            };
        }
    }

    displayXAIExplanation(type) {
        const xaiData = type === 'sender' ? this.senderXAIData : this.receiverXAIData;
        if (!xaiData || !xaiData.explanation) return;

        // Update prediction and confidence
        const predictionElement = document.getElementById(`${type}AIPrediction`);
        const confidenceElement = document.getElementById(`${type}AIConfidence`);

        if (predictionElement && xaiData.prediction) {
            predictionElement.textContent = xaiData.prediction.replace('_', ' ').toUpperCase();
            predictionElement.className = `badge ${this.getBadgeClass(xaiData.prediction)}`;
        }

        if (confidenceElement && xaiData.confidence) {
            const confidencePercent = (xaiData.confidence * 100).toFixed(1);
            confidenceElement.style.width = confidencePercent + '%';
            confidenceElement.textContent = confidencePercent + '%';
            confidenceElement.className = `progress-bar ${this.getProgressClass(xaiData.confidence)}`;
        }

        // Display LIME explanation
        this.displayLIMEFeatures(type, xaiData.explanation.lime);

        // Display SHAP explanation if available
        if (xaiData.explanation.shap) {
            this.displaySHAPFeatures(type, xaiData.explanation.shap);
            document.getElementById(`${type}SHAPSection`).style.display = 'block';
        }
    }

    displayLIMEFeatures(type, limeData) {
        if (!limeData || !limeData.feature_importance) return;

        const featuresContainer = document.getElementById(`${type}LIMEFeatures`);
        if (!featuresContainer) return;

        let html = '<div class="lime-features">';

        // Sort features by importance (absolute value)
        const sortedFeatures = limeData.feature_importance
            .slice(0, 10) // Show top 10 features
            .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]));

        sortedFeatures.forEach(([word, importance]) => {
            const absImportance = Math.abs(importance);
            const isPositive = importance > 0;
            const color = isPositive ? 'danger' : 'success';
            const icon = isPositive ? 'fas fa-arrow-up' : 'fas fa-arrow-down';
            const intensity = Math.min(1, absImportance * 5); // Scale for opacity

            html += `
                <span class="badge bg-${color} me-1 mb-1" style="opacity: ${0.3 + intensity * 0.7}" title="Importance: ${importance.toFixed(4)}">
                    <i class="${icon} me-1"></i>${word}
                    <small class="ms-1">${importance > 0 ? '+' : ''}${importance.toFixed(3)}</small>
                </span>
            `;
        });

        html += '</div>';
        html += '<p class="small text-muted mt-2"><i class="fas fa-info-circle me-1"></i>';
        html += 'Red badges indicate words that <strong>increased</strong> the threat score. ';
        html += 'Green badges indicate words that <strong>decreased</strong> the threat score.</p>';

        featuresContainer.innerHTML = html;
    }

    displaySHAPFeatures(type, shapData) {
        if (!shapData || !shapData.feature_importance) return;

        const featuresContainer = document.getElementById(`${type}SHAPFeatures`);
        if (!featuresContainer) return;

        let html = '<div class="shap-features">';

        // Sort SHAP features by absolute value
        const sortedFeatures = shapData.feature_importance
            .slice(0, 8) // Show top 8 features
            .sort((a, b) => Math.abs(b.shap_value) - Math.abs(a.shap_value));

        sortedFeatures.forEach(feature => {
            const absValue = Math.abs(feature.shap_value);
            const isPositive = feature.shap_value > 0;
            const color = isPositive ? 'danger' : 'info';
            const intensity = Math.min(1, absValue * 10); // Scale for bar width

            html += `
                <div class="shap-feature mb-2">
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="feature-name"><code>${feature.feature}</code></span>
                        <span class="shap-value text-${color}">${feature.shap_value.toFixed(4)}</span>
                    </div>
                    <div class="progress" style="height: 4px;">
                        <div class="progress-bar bg-${color}" role="progressbar" 
                             style="width: ${intensity * 100}%" title="SHAP Value: ${feature.shap_value}"></div>
                    </div>
                </div>
            `;
        });

        html += '</div>';
        featuresContainer.innerHTML = html;
    }

    getBadgeClass(category) {
        const categoryClasses = {
            'safe': 'bg-success',
            'cyberbullying': 'bg-warning',
            'financial_fraud': 'bg-danger',
            'identity_theft': 'bg-danger',
            'illegal_drugs': 'bg-dark',
            'phishing': 'bg-warning',
            'romance_scam': 'bg-info',
            'threats_violence': 'bg-danger',
            'weapons_trafficking': 'bg-dark'
        };
        return categoryClasses[category] || 'bg-secondary';
    }

    getProgressClass(confidence) {
        if (confidence >= 0.9) return 'bg-danger';
        if (confidence >= 0.7) return 'bg-warning';
        if (confidence >= 0.5) return 'bg-info';
        return 'bg-success';
    }
}

// Notification manager
class NotificationManager {
    static requestPermission() {
        if ('Notification' in window) {
            Notification.requestPermission();
        }
    }

    static show(title, options = {}) {
        if ('Notification' in window && Notification.permission === 'granted') {
            return new Notification(title, {
                icon: '/static/favicon.ico',
                badge: '/static/favicon.ico',
                ...options
            });
        }
    }
}

// Security dashboard utilities
class SecurityDashboard {
    static getSecurityLog() {
        return JSON.parse(localStorage.getItem('securityLog') || '[]');
    }

    static getSecurityStats() {
        const log = this.getSecurityLog();
        const last24h = new Date(Date.now() - 24 * 60 * 60 * 1000);

        const recent = log.filter(event => new Date(event.timestamp) > last24h);

        return {
            totalAlerts: log.length,
            recentAlerts: recent.length,
            mostCommonKeywords: this.getMostCommonKeywords(log),
            alertsByHour: this.getAlertsByHour(recent)
        };
    }

    static getMostCommonKeywords(log) {
        const keywordCounts = {};

        log.forEach(event => {
            if (event.keywords) {
                event.keywords.forEach(keyword => {
                    keywordCounts[keyword] = (keywordCounts[keyword] || 0) + 1;
                });
            }
        });

        return Object.entries(keywordCounts)
            .sort(([, a], [, b]) => b - a)
            .slice(0, 10);
    }

    static getAlertsByHour(log) {
        const hourCounts = new Array(24).fill(0);

        log.forEach(event => {
            const hour = new Date(event.timestamp).getHours();
            hourCounts[hour]++;
        });

        return hourCounts;
    }
}

// Initialize global instances
let chatManager;
let notificationManager;

// Document ready initialization
document.addEventListener('DOMContentLoaded', function () {
    // Initialize chat manager globally for floating chat window
    window.chatManager = new ChatManager();

    // Request notification permission
    NotificationManager.requestPermission();

    // Initialize chat UI if elements exist
    if (document.getElementById('chatMessages')) {
        // Chat window is available, set up event listeners
        const messageInput = document.getElementById('messageInput');
        if (messageInput) {
            messageInput.addEventListener('keypress', function (e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    sendMessage();
                }
            });
        }
    }

    // Initialize form handlers
    initializeFormHandlers();

    // Initialize tooltip and popover
    initializeBootstrapComponents();

    // Initialize theme switcher
    initializeThemeSwitcher();
});

function initializeFormHandlers() {
    // Chat form handler
    const messageForm = document.getElementById('messageForm');
    if (messageForm) {
        messageForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const messageInput = document.getElementById('messageInput');
            const message = messageInput.value.trim();

            if (message && chatManager) {
                if (chatManager.sendMessage(message)) {
                    messageInput.value = '';
                }
            }
        });

        // Typing indicator
        const messageInput = document.getElementById('messageInput');
        if (messageInput) {
            let typingTimer;

            messageInput.addEventListener('input', function () {
                if (chatManager && chatManager.socket) {
                    clearTimeout(typingTimer);

                    chatManager.socket.emit('typing', {
                        room: chatManager.currentRoom,
                        username: chatManager.currentUser
                    });

                    typingTimer = setTimeout(() => {
                        chatManager.socket.emit('stop_typing', {
                            room: chatManager.currentRoom,
                            username: chatManager.currentUser
                        });
                    }, 1000);
                }
            });
        }
    }

    // Password strength indicator for registration
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function () {
            const validation = FormValidator.validatePassword(this.value);
            updatePasswordStrength(validation.strength);
        });
    }
}

function updatePasswordStrength(strength) {
    const progressBar = document.querySelector('.password-strength .progress-bar');
    if (progressBar) {
        progressBar.style.width = strength + '%';
        progressBar.className = 'progress-bar';

        if (strength <= 25) {
            progressBar.classList.add('bg-danger');
        } else if (strength <= 50) {
            progressBar.classList.add('bg-warning');
        } else if (strength <= 75) {
            progressBar.classList.add('bg-info');
        } else {
            progressBar.classList.add('bg-success');
        }
    }
}

function initializeBootstrapComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

function initializeThemeSwitcher() {
    // Add theme switcher functionality if needed
    const theme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', theme);
}

// Utility functions
function formatTime(date) {
    return new Intl.DateTimeFormat('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(date);
}

// Chat UI Functions
function loadChatUsers() {
    const modal = new bootstrap.Modal(document.getElementById('chatUsersModal'));
    modal.show();

    // Load users list
    fetch('/api/users')
        .then(response => response.json())
        .then(users => {
            const usersList = document.getElementById('usersList');
            usersList.innerHTML = '';

            users.forEach(user => {
                const userItem = document.createElement('div');
                userItem.className = 'list-group-item list-group-item-action d-flex align-items-center';
                userItem.innerHTML = `
                    <div class="suggestion-avatar me-3">${user.username[0].toUpperCase()}</div>
                    <div class="flex-grow-1">
                        <h6 class="mb-0">${user.username}</h6>
                        <small class="text-muted">Posts: ${user.posts_count}</small>
                    </div>
                    <button class="btn btn-primary btn-sm" onclick="startChat('${user.username}')">
                        <i class="fas fa-comment me-1"></i>Chat
                    </button>
                `;
                usersList.appendChild(userItem);
            });
        })
        .catch(error => {
            console.error('Error loading users:', error);
            document.getElementById('usersList').innerHTML = '<div class="text-center text-muted">Error loading users</div>';
        });
}

function startChat(username) {
    console.log('Starting chat with:', username);

    // Close modal
    bootstrap.Modal.getInstance(document.getElementById('chatUsersModal')).hide();

    // Show chat window
    const chatWindow = document.getElementById('chatWindow');
    chatWindow.style.display = 'flex';

    // Update chat header
    document.getElementById('chatUsername').textContent = username;
    document.getElementById('chatStatus').textContent = 'Online';

    // Clear messages
    document.getElementById('chatMessages').innerHTML = '';

    // Initialize chat if manager exists
    if (window.chatManager) {
        // Get current user from API
        fetch('/api/current-user')
            .then(response => response.json())
            .then(data => {
                const currentUser = data.username;
                const room = [currentUser, username].sort().join('_');
                console.log('Starting chat:', { currentUser, username, room });

                // Join the room first
                window.chatManager.joinRoom(room, currentUser);

                // Load chat history
                return fetch(`/api/chat-history/${username}`);
            })
            .then(response => response.json())
            .then(historyData => {
                console.log('Loaded chat history:', historyData);

                // Display previous messages
                if (historyData.messages && historyData.messages.length > 0) {
                    historyData.messages.forEach(message => {
                        window.chatManager.displayMessage(message);
                    });
                }
            })
            .catch(error => {
                console.error('Error starting chat:', error);
                alert('Unable to start chat. Please refresh the page.');
            });
    }
}

function closeChat() {
    document.getElementById('chatWindow').style.display = 'none';
    if (window.chatManager) {
        window.chatManager.leaveRoom();
    }
}

function minimizeChat() {
    const chatWindow = document.getElementById('chatWindow');
    chatWindow.classList.toggle('minimized');
}

function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();

    if (message && window.chatManager) {
        if (window.chatManager.sendMessage(message)) {
            input.value = '';
        }
    }
}

// Enter key support is handled in the main DOMContentLoaded event

// Warning modal actions
function viewGuidelines() {
    // Close sender warning modal
    const senderModal = bootstrap.Modal.getInstance(document.getElementById('senderWarningModal'));
    if (senderModal) {
        senderModal.hide();
    }

    // Show guidelines (could redirect to guidelines page or show another modal)
    alert('Community Guidelines:\n\n1. Be respectful to all users\n2. No harmful, violent, or threatening content\n3. No financial scams or unauthorized monetary requests\n4. Report suspicious behavior\n5. Keep conversations appropriate');
}

function blockUser() {
    // Close receiver warning modal
    const receiverModal = bootstrap.Modal.getInstance(document.getElementById('receiverWarningModal'));
    if (receiverModal) {
        receiverModal.hide();
    }

    // Block user functionality (would need backend implementation)
    const confirmed = confirm('Are you sure you want to block this user? They will no longer be able to message you.');
    if (confirmed) {
        // Implementation would go here
        alert('User has been blocked successfully.');
        closeChat();
    }
}

function reportUser() {
    // Close receiver warning modal
    const receiverModal = bootstrap.Modal.getInstance(document.getElementById('receiverWarningModal'));
    if (receiverModal) {
        receiverModal.hide();
    }

    // Report user functionality (would need backend implementation)
    const reason = prompt('Please provide a reason for reporting this user:');
    if (reason && reason.trim()) {
        // Implementation would go here
        alert('Thank you for your report. Our moderation team will review this case.');
        closeChat();
    }
}

// Global function to toggle XAI explanations
function toggleXAIExplanation(type) {
    const xaiSection = document.getElementById(`${type}XAISection`);
    const toggleButton = document.getElementById(`${type}ToggleXAI`);

    if (!xaiSection || !toggleButton || !window.chatManager) return;

    if (xaiSection.style.display === 'none' || !xaiSection.style.display) {
        // Show XAI explanation
        window.chatManager.displayXAIExplanation(type);
        xaiSection.style.display = 'block';
        toggleButton.innerHTML = '<i class="fas fa-eye-slash me-1"></i>Hide AI Analysis';
        toggleButton.className = toggleButton.className.replace('btn-outline-info', 'btn-outline-secondary').replace('btn-outline-warning', 'btn-outline-secondary');
    } else {
        // Hide XAI explanation
        xaiSection.style.display = 'none';
        const buttonClass = type === 'sender' ? 'btn-outline-info' : 'btn-outline-warning';
        toggleButton.innerHTML = '<i class="fas fa-brain me-1"></i>Show AI Analysis';
        toggleButton.className = toggleButton.className.replace('btn-outline-secondary', buttonClass);
    }
}

// Export for use in other scripts
window.ChatManager = ChatManager;
window.NotificationManager = NotificationManager;
window.SecurityDashboard = SecurityDashboard;
window.FormValidator = FormValidator;
window.loadChatUsers = loadChatUsers;
window.startChat = startChat;
window.closeChat = closeChat;
window.minimizeChat = minimizeChat;
window.sendMessage = sendMessage;
window.viewGuidelines = viewGuidelines;
window.blockUser = blockUser;
window.reportUser = reportUser;
window.toggleXAIExplanation = toggleXAIExplanation;
