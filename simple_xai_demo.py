#!/usr/bin/env python3
"""
Simplified XAI Demo for Testing Warning Modals
This creates mock XAI responses without loading the full ML stack
"""

class SimpleXAIDemo:
    """Simple XAI demo for testing purposes"""
    
    def __init__(self):
        self.categories = [
            'safe', 'cyberbullying', 'financial_fraud', 'identity_theft', 
            'illegal_drugs', 'phishing', 'romance_scam', 'threats_violence', 
            'weapons_trafficking'
        ]
        
        # Mock keyword patterns for demo
        self.patterns = {
            'threats_violence': ['kill', 'murder', 'bomb', 'weapon', 'gun', 'attack', 'violence', 'threat'],
            'financial_fraud': ['money', 'send money', 'transfer', 'payment', 'investment', 'loan'],
            'phishing': ['verify', 'account', 'login', 'password', 'credential', 'update'],
            'illegal_drugs': ['drug', 'cocaine', 'heroin', 'marijuana', 'pills'],
            'weapons_trafficking': ['weapon', 'gun', 'explosive', 'bomb making', 'ammunition'],
            'cyberbullying': ['stupid', 'ugly', 'hate you', 'loser', 'worthless'],
            'identity_theft': ['ssn', 'social security', 'identity', 'personal info'],
            'romance_scam': ['love you', 'meet me', 'lonely', 'relationship']
        }
    
    def predict_with_explanation(self, text, explanation_type='lime'):
        """Mock prediction with explanation"""
        text_lower = text.lower()
        
        # Find matching category
        best_category = 'safe'
        best_confidence = 0.1
        matched_words = []
        
        for category, keywords in self.patterns.items():
            matches = [word for word in keywords if word in text_lower]
            if matches:
                confidence = min(0.95, len(matches) * 0.3 + 0.5)
                if confidence > best_confidence:
                    best_category = category
                    best_confidence = confidence
                    matched_words = matches
        
        # Generate mock LIME explanation
        lime_explanation = self.generate_mock_lime(text, matched_words, best_category)
        
        # Generate mock SHAP explanation (simplified)
        shap_explanation = self.generate_mock_shap(text, matched_words, best_category) if explanation_type in ['shap', 'both'] else None
        
        explanations = {'lime': lime_explanation}
        if shap_explanation:
            explanations['shap'] = shap_explanation
        
        return {
            'text': text,
            'predicted_category': best_category,
            'confidence': best_confidence,
            'is_cybercrime': best_category != 'safe',
            'all_probabilities': self.generate_mock_probabilities(best_category, best_confidence),
            'explanations': explanations
        }
    
    def generate_mock_lime(self, text, matched_words, category):
        """Generate mock LIME explanation"""
        words = text.split()
        feature_importance = []
        
        for word in words:
            if word.lower() in matched_words:
                # High positive importance for matched threat words
                importance = 0.8 + (len(word) * 0.02)
                feature_importance.append([word, importance])
            elif word.lower() in ['the', 'and', 'or', 'but', 'is', 'are', 'was', 'were']:
                # Slight negative importance for stop words
                importance = -0.1 - (len(word) * 0.01)
                feature_importance.append([word, importance])
            elif len(word) > 3:
                # Small random importance for other words
                importance = (hash(word) % 100 - 50) / 1000
                feature_importance.append([word, importance])
        
        # Sort by absolute importance
        feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)
        
        return {
            'feature_importance': feature_importance,
            'prediction_proba': self.generate_mock_probabilities(category, 0.8),
            'score': 0.85
        }
    
    def generate_mock_shap(self, text, matched_words, category):
        """Generate mock SHAP explanation"""
        words = text.split()
        feature_importance = []
        
        for word in words[:10]:  # Limit to top 10 features
            if word.lower() in matched_words:
                shap_value = 0.5 + (hash(word) % 50) / 100
                feature_importance.append({
                    'feature': word,
                    'shap_value': shap_value,
                    'feature_value': 1.0
                })
            else:
                shap_value = (hash(word) % 100 - 50) / 500  # Random small values
                feature_importance.append({
                    'feature': word,
                    'shap_value': shap_value,
                    'feature_value': 1.0 if word.lower() in text.lower() else 0.0
                })
        
        # Sort by absolute SHAP value
        feature_importance.sort(key=lambda x: abs(x['shap_value']), reverse=True)
        
        return {
            'feature_importance': feature_importance,
            'base_value': 0.1
        }
    
    def generate_mock_probabilities(self, predicted_category, confidence):
        """Generate mock probability distribution"""
        probs = {}
        remaining_prob = 1.0 - confidence
        
        for category in self.categories:
            if category == predicted_category:
                probs[category] = confidence
            else:
                # Distribute remaining probability among other categories
                probs[category] = remaining_prob / (len(self.categories) - 1)
        
        return probs

if __name__ == "__main__":
    # Test the simple XAI demo
    demo = SimpleXAIDemo()
    
    test_messages = [
        "I will kill you if you don't listen",
        "Send me money for emergency",
        "Please verify your account by clicking this link",
        "How are you doing today?",
        "Want to buy some drugs?"
    ]
    
    for message in test_messages:
        print(f"\nTesting: '{message}'")
        result = demo.predict_with_explanation(message, 'both')
        print(f"Category: {result['predicted_category']}")
        print(f"Confidence: {result['confidence']:.3f}")
        print(f"LIME features: {result['explanations']['lime']['feature_importance'][:3]}")
        if 'shap' in result['explanations']:
            print(f"SHAP features: {len(result['explanations']['shap']['feature_importance'])}")
