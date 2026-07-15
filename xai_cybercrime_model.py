#!/usr/bin/env python3
"""
Explainable AI Model for Cybercrime Detection
This module implements an XAI model using LIME and SHAP for interpretable cybercrime detection
"""

import pandas as pd
import numpy as np
import pickle
import json
import re
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Core ML libraries
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, roc_auc_score
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline

# Text preprocessing
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# XAI libraries
try:
    import lime
    from lime.lime_text import LimeTextExplainer
    LIME_AVAILABLE = True
except ImportError:
    LIME_AVAILABLE = False
    print("LIME not available. Install with: pip install lime")

try:
    import shap
    SHAP_AVAILABLE = True
except (ImportError, MemoryError) as e:
    SHAP_AVAILABLE = False
    print(f"SHAP not available ({e}). LIME explanations will still work.")

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

class CybercrimeXAIModel:
    """Explainable AI model for cybercrime detection"""
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.lime_explainer = None
        self.shap_explainer = None
        self.feature_names = None
        self.model_trained = False
        
        # Initialize text preprocessing components
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            print("Downloading NLTK data...")
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
        
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Cybercrime-specific keywords that shouldn't be removed
        self.preserve_words = {
            'kill', 'murder', 'bomb', 'gun', 'weapon', 'money', 'bitcoin',
            'transfer', 'payment', 'fraud', 'scam', 'threat', 'violence'
        }
        
    def preprocess_text(self, text):
        """Advanced text preprocessing for cybercrime detection"""
        if not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s!?$€£]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords but preserve cybercrime-related terms
        tokens = [token for token in tokens if token not in self.stop_words or token in self.preserve_words]
        
        # Lemmatize
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens if len(token) > 1]
        
        return ' '.join(tokens)
    
    def extract_features(self, df):
        """Extract comprehensive features from text data"""
        processed_texts = []
        
        for text in df['text']:
            processed_text = self.preprocess_text(text)
            processed_texts.append(processed_text)
        
        return processed_texts
    
    def prepare_data(self, df):
        """Prepare data for training"""
        # Extract features
        X_text = self.extract_features(df)
        
        # Prepare labels for multi-class classification
        y_category = df['category'].values
        y_binary = df['is_cybercrime'].astype(int).values
        
        # Initialize vectorizer with more features and wider n-gram range
        if self.vectorizer is None:
            self.vectorizer = TfidfVectorizer(
                max_features=10000,
                ngram_range=(1, 3),
                min_df=1, # Allow rare but important words
                max_df=0.9,
                stop_words='english',
                sublinear_tf=True # Use log scale for term frequency
            )
            X_vectorized = self.vectorizer.fit_transform(X_text)
        else:
            X_vectorized = self.vectorizer.transform(X_text)
        
        # Prepare label encoder for categories
        if self.label_encoder is None:
            self.label_encoder = LabelEncoder()
            y_category_encoded = self.label_encoder.fit_transform(y_category)
        else:
            y_category_encoded = self.label_encoder.transform(y_category)
        
        # Store feature names
        self.feature_names = self.vectorizer.get_feature_names_out()
        
        return X_vectorized, y_category_encoded, y_binary, X_text
    
    def train_model(self, df, model_type='random_forest', test_size=0.2):
        """Train the XAI model with comprehensive evaluation"""
        print("Preparing data for training...")
        X_vectorized, y_category, y_binary, X_text = self.prepare_data(df)
        
        # Split data
        X_train, X_test, y_train, y_test, text_train, text_test = train_test_split(
            X_vectorized, y_category, X_text, test_size=test_size, random_state=42, stratify=y_category
        )
        
        print(f"Training set size: {X_train.shape[0]}")
        print(f"Test set size: {X_test.shape[0]}")
        
        # Select and train model
        if model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=200, # Increased for better stability
                max_depth=40,    # Increased for complex pattern recognition
                min_samples_split=2,
                min_samples_leaf=1,
                class_weight='balanced', # Crucial for diverse categories
                random_state=42,
                n_jobs=-1
            )
        elif model_type == 'gradient_boosting':
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=10,
                learning_rate=0.1,
                random_state=42
            )
        elif model_type == 'logistic_regression':
            self.model = LogisticRegression(
                max_iter=1000,
                random_state=42,
                multi_class='ovr'
            )
        
        print(f"Training {model_type} model...")
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        print(f"\nModel Accuracy: {accuracy:.3f}")
        
        # Detailed classification report
        class_names = self.label_encoder.classes_
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=class_names))
        
        # Initialize explainers
        self._initialize_explainers(X_train, text_train, y_train)
        
        self.model_trained = True
        
        # Return evaluation metrics
        evaluation = {
            'accuracy': accuracy,
            'test_size': len(y_test),
            'train_size': len(y_train),
            'feature_count': X_train.shape[1],
            'classes': list(class_names)
        }
        
        return evaluation
    
    def _initialize_explainers(self, X_train, text_train, y_train):
        """Initialize LIME and SHAP explainers"""
        print("Initializing explainers...")
        
        # Initialize LIME explainer
        if LIME_AVAILABLE:
            class_names = self.label_encoder.classes_
            self.lime_explainer = LimeTextExplainer(
                class_names=class_names,
                feature_selection='auto',
                random_state=42
            )
            print("LIME explainer initialized")
        
        # Initialize SHAP explainer with improved compatibility
        if SHAP_AVAILABLE:
            try:
                # Ensure X_train is in the right format
                if hasattr(X_train, 'toarray'):
                    X_train_dense = X_train.toarray()
                else:
                    X_train_dense = X_train
                
                # Ensure proper dtype
                X_train_dense = X_train_dense.astype(np.float64)
                
                # For tree-based models, use TreeExplainer
                if hasattr(self.model, 'estimators_'):
                    # Try different TreeExplainer configurations for compatibility
                    try:
                        self.shap_explainer = shap.TreeExplainer(self.model)
                    except Exception as e1:
                        try:
                            # Fallback with background data
                            self.shap_explainer = shap.TreeExplainer(
                                self.model, 
                                X_train_dense[:100]
                            )
                        except Exception as e2:
                            # Final fallback to KernelExplainer
                            print(f"TreeExplainer failed ({e1}), using KernelExplainer")
                            def predict_fn(x):
                                return self.model.predict_proba(x)
                            self.shap_explainer = shap.KernelExplainer(
                                predict_fn,
                                X_train_dense[:20]  # Small subset for speed
                            )
                elif hasattr(self.model, 'coef_'):
                    # For linear models, use LinearExplainer
                    try:
                        self.shap_explainer = shap.LinearExplainer(
                            self.model, 
                            X_train_dense[:100]
                        )
                    except Exception:
                        # Fallback for linear models
                        def predict_fn(x):
                            return self.model.predict_proba(x)
                        self.shap_explainer = shap.KernelExplainer(
                            predict_fn,
                            X_train_dense[:20]
                        )
                else:
                    # Fallback to KernelExplainer
                    def predict_fn(x):
                        return self.model.predict_proba(x)
                    
                    self.shap_explainer = shap.KernelExplainer(
                        predict_fn,
                        X_train_dense[:20]  # Smaller subset for KernelExplainer
                    )
                
                print("SHAP explainer initialized")
            except Exception as e:
                print(f"SHAP explainer initialization failed: {e}")
                self.shap_explainer = None
    
    def predict_with_explanation(self, text, explanation_type='both'):
        """Predict cybercrime category with explanation"""
        if not self.model_trained:
            raise ValueError("Model not trained yet. Call train_model() first.")
        
        # Preprocess text
        processed_text = self.preprocess_text(text)
        X_vectorized = self.vectorizer.transform([processed_text])
        
        # Make prediction
        prediction = self.model.predict(X_vectorized)[0]
        prediction_proba = self.model.predict_proba(X_vectorized)[0]
        
        # Get category name
        category = self.label_encoder.inverse_transform([prediction])[0]
        confidence = np.max(prediction_proba)

        # --- SAFETY GUARDRAIL OVERRIDE ---
        # Highly flexible patterns to catch social engineering
        phishing_patterns = [
            r'visit\b.*?\blink',
            r'click\b.*?\b(?:here|this|link)',
            r'send\b.*?\bmoney',
            r'verification\b.*?\bcode',
            r'login\b.*?\b(?:account|here|now)',
            r'urgent\b.*?\bhelp',
            r'bank\b.*?\baccount'
        ]
        
        # Technical indicators
        has_url = bool(re.search(r'http[s]?://', text.lower()))
        has_ip = bool(re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', text.lower()))
        
        is_risky_text = any(re.search(pattern, text.lower()) for pattern in phishing_patterns)
        
        # Aggressive Link Strategy: If message has a link AND any suspicious request word, flag it.
        request_keywords = ['can', 'you', 'please', 'check', 'help', 'verify', 'account', 'now']
        has_request = any(word in text.lower() for word in request_keywords)
        
        if (is_risky_text or (has_url and has_request) or (has_ip and has_request)):
            # If AI is unsure (confidence < 0.70) or says it's safe, we override
            if category == 'safe' or confidence < 0.70:
                category = 'phishing'
                confidence = 0.90 # High confidence for manual overrides
            
        result = {
            'text': text,
            'predicted_category': category,
            'confidence': confidence,
            'is_cybercrime': category != 'safe',
            'all_probabilities': dict(zip(self.label_encoder.classes_, prediction_proba))
        }
        
        # Generate explanations
        explanations = {}
        
        if explanation_type in ['lime', 'both'] and LIME_AVAILABLE and self.lime_explainer:
            try:
                lime_explanation = self._get_lime_explanation(text)
                explanations['lime'] = lime_explanation
            except Exception as e:
                print(f"LIME explanation failed: {e}")
        
        if explanation_type in ['shap', 'both'] and SHAP_AVAILABLE:
            if self.shap_explainer is not None:
                try:
                    shap_explanation = self._get_shap_explanation(X_vectorized)
                    explanations['shap'] = shap_explanation
                except Exception as e:
                    print(f"SHAP explanation failed: {e}")
                    # Provide fallback explanation
                    if hasattr(self.model, 'feature_importances_'):
                        explanations['shap'] = {
                            'feature_importance': [],
                            'base_value': 0.0,
                            'note': f'SHAP unavailable, using model features ({str(e)[:50]}...)'
                        }
            else:
                # SHAP explainer failed to initialize
                explanations['shap'] = {
                    'feature_importance': [],
                    'base_value': 0.0,
                    'note': 'SHAP explainer not available'
                }
        
        result['explanations'] = explanations
        
        return result
    
    def _get_lime_explanation(self, text, num_features=10):
        """Generate LIME explanation"""
        def predict_fn(texts):
            processed_texts = [self.preprocess_text(t) for t in texts]
            X_vectorized = self.vectorizer.transform(processed_texts)
            return self.model.predict_proba(X_vectorized)
        
        explanation = self.lime_explainer.explain_instance(
            text, predict_fn, num_features=num_features
        )
        
        # Extract explanation data
        lime_data = {
            'feature_importance': explanation.as_list(),
            'prediction_proba': explanation.predict_proba.tolist(),
            'score': explanation.score
        }
        
        return lime_data
    
    def _get_shap_explanation(self, X_vectorized, max_display=10):
        """Generate SHAP explanation with improved error handling"""
        try:
            # Convert sparse matrix to dense if needed
            if hasattr(X_vectorized, 'toarray'):
                X_dense = X_vectorized.toarray()
            else:
                X_dense = X_vectorized
            
            # Ensure proper dtype
            X_dense = X_dense.astype(np.float64)
            
            # Determine class index for multi-class SHAP
            predicted_class = self.model.predict(X_vectorized)[0]
            class_name = self.label_encoder.inverse_transform([predicted_class])[0]
            class_idx = list(self.label_encoder.classes_).index(class_name)
            
            # Get SHAP values based on explainer type
            if hasattr(self.shap_explainer, 'shap_values'):
                # For tree explainers
                shap_values = self.shap_explainer.shap_values(X_dense)
                if isinstance(shap_values, list):
                    # Multi-class case (list of arrays)
                    shap_values = shap_values[min(class_idx, len(shap_values)-1)]
                elif isinstance(shap_values, np.ndarray) and len(shap_values.shape) == 3:
                    # Multi-class case (3D array: [samples, features, classes] or [classes, samples, features])
                    # Try to detect which dimension is classes (usually matches n_classes)
                    n_classes = len(self.label_encoder.classes_)
                    if shap_values.shape[2] == n_classes:
                        shap_values = shap_values[:, :, class_idx]
                    elif shap_values.shape[0] == n_classes:
                        shap_values = shap_values[class_idx, :, :]
            else:
                # For other explainers
                shap_values = self.shap_explainer(X_dense)
                if hasattr(shap_values, 'values'):
                    shap_values = shap_values.values
                
                # Handle multi-class for Explanation objects
                if len(shap_values.shape) == 3:
                    shap_values = shap_values[:, :, class_idx]
            
            # Handle sample dimension
            if len(shap_values.shape) == 2:
                shap_values = shap_values[0]  # Take first sample
            elif len(shap_values.shape) == 1:
                pass # Already 1D
            
            # Get feature values (first sample)
            feature_values = X_dense[0]
            
            # Helper to safely convert to float scalar
            def to_scalar(val):
                if isinstance(val, (np.ndarray, list)):
                    try:
                        return float(val[0])
                    except:
                        return 0.0
                return float(val)

            # Create explanation dictionary
            feature_importance = []
            for i, (feature, shap_val) in enumerate(zip(self.feature_names, shap_values)):
                s_val = to_scalar(shap_val)
                if abs(s_val) > 1e-10:  # Only include non-zero values
                    feature_importance.append({
                        'feature': str(feature),
                        'shap_value': s_val,
                        'feature_value': to_scalar(feature_values[i])
                    })
            
            # Sort by absolute SHAP value
            feature_importance.sort(key=lambda x: abs(x['shap_value']), reverse=True)
            
            # Get base value
            base_value = 0.0
            if hasattr(self.shap_explainer, 'expected_value'):
                expected_val = self.shap_explainer.expected_value
                if isinstance(expected_val, (np.ndarray, list)):
                    # Handle multi-class expected values
                    if len(expected_val) > class_idx:
                        base_value = to_scalar(expected_val[class_idx])
                    else:
                        base_value = to_scalar(expected_val[0])
                else:
                    base_value = to_scalar(expected_val)
            
            return {
                'feature_importance': feature_importance[:max_display],
                'base_value': base_value
            }
            
        except Exception as e:
            # Return a fallback explanation based on model feature importance
            print(f"SHAP explanation failed, using model feature importance: {e}")
            if hasattr(self.model, 'feature_importances_'):
                # Get top features from model
                feature_importance = []
                for i, (feature, importance) in enumerate(zip(self.feature_names, self.model.feature_importances_)):
                    if importance > 1e-10:
                        feature_importance.append({
                            'feature': str(feature),
                            'shap_value': float(importance),
                            'feature_value': float(X_vectorized.toarray()[0][i]) if hasattr(X_vectorized, 'toarray') else float(X_vectorized[0][i])
                        })
                
                feature_importance.sort(key=lambda x: abs(x['shap_value']), reverse=True)
                return {
                    'feature_importance': feature_importance[:max_display],
                    'base_value': 0.0,
                    'note': 'Using model feature importance (SHAP failed)'
                }
            else:
                return {
                    'feature_importance': [],
                    'base_value': 0.0,
                    'error': str(e)
                }
    
    def get_model_insights(self, top_features=20):
        """Get global model insights"""
        if not self.model_trained:
            raise ValueError("Model not trained yet.")
        
        insights = {}
        
        # Feature importance (for tree-based models)
        if hasattr(self.model, 'feature_importances_'):
            feature_importance = self.model.feature_importances_
            feature_names = self.feature_names
            
            # Sort features by importance
            sorted_indices = np.argsort(feature_importance)[::-1][:top_features]
            
            insights['top_features'] = [
                {
                    'feature': feature_names[i],
                    'importance': float(feature_importance[i])
                }
                for i in sorted_indices
            ]
        
        # Model parameters
        insights['model_params'] = {
            'model_type': type(self.model).__name__,
            'n_features': len(self.feature_names),
            'n_classes': len(self.label_encoder.classes_),
            'classes': list(self.label_encoder.classes_)
        }
        
        return insights
    
    def save_model(self, filepath='xai_cybercrime_model.pkl'):
        """Save trained model and components"""
        if not self.model_trained:
            raise ValueError("No trained model to save.")
        
        model_data = {
            'model': self.model,
            'vectorizer': self.vectorizer,
            'label_encoder': self.label_encoder,
            'feature_names': self.feature_names,
            'model_trained': self.model_trained,
            'training_date': datetime.now().isoformat()
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath='xai_cybercrime_model.pkl'):
        """Load trained model and components"""
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.vectorizer = model_data['vectorizer']
            self.label_encoder = model_data['label_encoder']
            self.feature_names = model_data['feature_names']
            self.model_trained = model_data['model_trained']
            
            # Fix scikit-learn version compatibility issue
            if self.model and hasattr(self.model, 'estimators_'):
                if not hasattr(self.model, 'monotonic_cst'):
                    self.model.monotonic_cst = None
            
            # Reinitialize explainers
            if self.model_trained:
                print("Reinitializing explainers...")
                # Create dummy data for explainer initialization
                dummy_X = np.random.random((10, len(self.feature_names)))
                dummy_text = ["dummy text"] * 10
                dummy_y = np.zeros(10)
                self._initialize_explainers(dummy_X, dummy_text, dummy_y)
            
            print(f"Model loaded from {filepath}")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

def install_dependencies():
    """Install required XAI dependencies"""
    import subprocess
    import sys
    
    packages = ['lime', 'shap', 'nltk', 'matplotlib', 'seaborn']
    
    for package in packages:
        try:
            __import__(package)
            print(f"✓ {package} already installed")
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

if __name__ == "__main__":
    # Check and install dependencies
    print("Checking XAI dependencies...")
    install_dependencies()
    
    # Load dataset
    print("\nLoading cybercrime dataset...")
    try:
        df = pd.read_csv('cybercrime_dataset.csv')
        print(f"Dataset loaded: {len(df)} samples")
    except FileNotFoundError:
        print("Dataset not found. Run cybercrime_dataset.py first!")
        exit(1)
    
    # Initialize and train model
    print("\nInitializing XAI model...")
    xai_model = CybercrimeXAIModel()
    
    print("Training model...")
    evaluation = xai_model.train_model(df, model_type='random_forest')
    
    print("\n=== Training Complete ===")
    print(f"Model accuracy: {evaluation['accuracy']:.3f}")
    print(f"Features used: {evaluation['feature_count']}")
    
    # Save model
    xai_model.save_model()
    
    # Test predictions with explanations
    test_messages = [
        "Send me $500 for emergency help",
        "I'm going to kill you if you don't listen",
        "How was your day today?",
        "Click this link to verify your account",
        "Selling cocaine, high quality stuff"
    ]
    
    print("\n=== Testing Predictions with Explanations ===")
    for message in test_messages:
        print(f"\nText: '{message}'")
        result = xai_model.predict_with_explanation(message, explanation_type='lime')
        print(f"Predicted: {result['predicted_category']} (confidence: {result['confidence']:.3f})")
        
        if 'lime' in result['explanations']:
            print("LIME explanation (top features):")
            for feature, importance in result['explanations']['lime']['feature_importance'][:5]:
                print(f"  {feature}: {importance:.3f}")
    
    print("\nXAI model training complete!")
