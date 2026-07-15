#!/usr/bin/env python3
"""
Lightweight XAI Model for Cybercrime Detection
Optimized version without SHAP to reduce memory usage
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
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# Text preprocessing
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# LIME only (no SHAP to reduce memory)
try:
    import lime
    from lime.lime_text import LimeTextExplainer
    LIME_AVAILABLE = True
except ImportError:
    LIME_AVAILABLE = False
    print("LIME not available. Install with: pip install lime")

class CybercrimeXAIModelLite:
    """Lightweight XAI model for cybercrime detection"""
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.lime_explainer = None
        self.feature_names = None
        self.model_trained = False
        
        # Initialize text preprocessing components
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            print("Downloading NLTK data...")
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True) 
                nltk.download('wordnet', quiet=True)
            except Exception:
                pass
        
        try:
            self.lemmatizer = WordNetLemmatizer()
            self.stop_words = set(stopwords.words('english'))
        except Exception:
            self.lemmatizer = None
            self.stop_words = set()
        
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
        
        # Basic tokenization if NLTK not available
        if self.lemmatizer:
            tokens = word_tokenize(text)
            tokens = [token for token in tokens if token not in self.stop_words or token in self.preserve_words]
            tokens = [self.lemmatizer.lemmatize(token) for token in tokens if len(token) > 1]
        else:
            tokens = text.split()
            tokens = [token for token in tokens if len(token) > 1]
        
        return ' '.join(tokens)
    
    def predict_with_explanation(self, text, explanation_type='lime'):
        """Predict cybercrime category with explanation"""
        if not self.model_trained:
            raise ValueError("Model not trained yet. Call load_model() first.")
        
        # Preprocess text
        processed_text = self.preprocess_text(text)
        X_vectorized = self.vectorizer.transform([processed_text])
        
        # Make prediction
        prediction = self.model.predict(X_vectorized)[0]
        prediction_proba = self.model.predict_proba(X_vectorized)[0]
        
        # Get category name
        category = self.label_encoder.inverse_transform([prediction])[0]
        confidence = np.max(prediction_proba)
        
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
        
        # SHAP is not available in lite version
        if explanation_type in ['shap', 'both']:
            explanations['shap'] = {
                'feature_importance': [],
                'base_value': 0.0,
                'note': 'SHAP not available in lite version'
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
            
            # Initialize LIME explainer
            if LIME_AVAILABLE and self.model_trained:
                class_names = self.label_encoder.classes_
                self.lime_explainer = LimeTextExplainer(
                    class_names=class_names,
                    feature_selection='auto',
                    random_state=42
                )
                print("LIME explainer initialized")
            
            print(f"Lite XAI model loaded from {filepath}")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

# Alias for compatibility
CybercrimeXAIModel = CybercrimeXAIModelLite

if __name__ == "__main__":
    # Test the lite model
    model = CybercrimeXAIModelLite()
    if model.load_model():
        print("Model loaded successfully!")
        
        # Test prediction
        test_message = "Send me money for emergency help"
        result = model.predict_with_explanation(test_message, 'lime')
        print(f"\nTest: '{test_message}'")
        print(f"Category: {result['predicted_category']}")
        print(f"Confidence: {result['confidence']:.3f}")
        
        if 'lime' in result['explanations']:
            print("LIME explanation available")
        else:
            print("No LIME explanation")
    else:
        print("Failed to load model")
