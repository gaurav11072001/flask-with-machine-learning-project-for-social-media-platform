#!/usr/bin/env python3

from xai_cybercrime_model import CybercrimeXAIModel
import re

def analyze_features_by_category(features):
    """Categorize features by type"""
    categories = {
        'Financial Terms': [],
        'Weapons/Violence': [],
        'Technology/Security': [],
        'Drugs/Illegal': [],
        'Communication': [],
        'Identity/Personal': [],
        'N-grams (Phrases)': [],
        'Numbers/Values': [],
        'Other': []
    }
    
    # Define patterns for categorization
    patterns = {
        'Financial Terms': ['money', 'transfer', 'investment', 'purchase', 'sale', 'business', 'pay', 'cash', 'dollar', 'euro', 'bitcoin', 'cost', 'price'],
        'Weapons/Violence': ['weapon', 'bomb', 'explosive', 'kill', 'attack', 'violence', 'threat', 'gun', 'knife', 'murder', 'assault'],
        'Technology/Security': ['account', 'password', 'login', 'verify', 'update', 'credential', 'security', 'system', 'hack', 'malware'],
        'Drugs/Illegal': ['drug', 'cocaine', 'heroin', 'marijuana', 'illegal', 'trafficking', 'substance'],
        'Communication': ['send', 'message', 'call', 'email', 'contact', 'info', 'information', 'document', 'text'],
        'Identity/Personal': ['identity', 'personal', 'social', 'ssn', 'name', 'address', 'birth', 'id'],
        'Numbers/Values': ['\\d+', '500', '1000', 'amount', 'number']
    }
    
    for feature in features:
        feature_name = feature['feature'].lower()
        categorized = False
        
        # Check if it's an n-gram (contains multiple words)
        if ' ' in feature_name and len(feature_name.split()) > 1:
            categories['N-grams (Phrases)'].append(feature)
            categorized = True
        else:
            # Check patterns
            for category, pattern_list in patterns.items():
                for pattern in pattern_list:
                    if re.search(pattern, feature_name):
                        categories[category].append(feature)
                        categorized = True
                        break
                if categorized:
                    break
        
        # If not categorized, put in 'Other'
        if not categorized:
            categories['Other'].append(feature)
    
    return categories

def main():
    print("Loading XAI Cybercrime Detection Model...")
    model = CybercrimeXAIModel()
    
    if not model.load_model():
        print("Failed to load model!")
        return
    
    # Get comprehensive insights
    insights = model.get_model_insights(top_features=100)
    
    print("\n" + "="*100)
    print("COMPREHENSIVE XAI CYBERCRIME DETECTION MODEL ANALYSIS")
    print("="*100)
    
    # Model overview
    if 'model_params' in insights:
        params = insights['model_params']
        print(f"\n🤖 MODEL OVERVIEW:")
        print(f"   • Algorithm: {params.get('model_type', 'Unknown')}")
        print(f"   • Total Features Extracted: {params.get('n_features', 0):,}")
        print(f"   • Detection Categories: {params.get('n_classes', 0)}")
        print(f"   • Classes: {', '.join(params.get('classes', []))}")
    
    # Feature extraction details
    print(f"\n📊 FEATURE EXTRACTION PROCESS:")
    print(f"   • Text Preprocessing: Tokenization, Lemmatization, Stop-word removal")
    print(f"   • Vectorization: TF-IDF with n-grams (1-3)")
    print(f"   • Feature Selection: Max 5,000 features, Min DF=2, Max DF=0.8")
    print(f"   • Preserved Keywords: Crime and payment-related terms")
    
    if 'top_features' in insights and insights['top_features']:
        # Analyze top features by category
        categorized_features = analyze_features_by_category(insights['top_features'])
        
        print(f"\n🔍 TOP PREDICTIVE FEATURES BY CATEGORY:")
        print("=" * 100)
        
        for category, features in categorized_features.items():
            if features:
                print(f"\n📌 {category.upper()} ({len(features)} features):")
                print("-" * 80)
                for i, feat in enumerate(features[:10]):  # Show top 10 per category
                    print(f"   {i+1:2d}. {feat['feature']:<35} | Importance: {feat['importance']:.6f}")
                if len(features) > 10:
                    print(f"   ... and {len(features) - 10} more features")
        
        # Overall top 20 features
        print(f"\n🏆 OVERALL TOP 20 MOST IMPORTANT FEATURES:")
        print("=" * 100)
        print(f"{'Rank':<5} {'Feature':<40} {'Importance':<12} {'Type':<20}")
        print("-" * 100)
        
        for i, feat in enumerate(insights['top_features'][:20]):
            feature_name = feat['feature']
            importance = feat['importance']
            
            # Determine type
            if ' ' in feature_name:
                feat_type = "N-gram Phrase"
            elif any(char.isdigit() for char in feature_name):
                feat_type = "Number/Value"
            elif feature_name in ['money', 'transfer', 'investment', 'purchase']:
                feat_type = "Financial"
            elif feature_name in ['weapon', 'bomb', 'threat', 'violence']:
                feat_type = "Violence/Weapons"
            elif feature_name in ['account', 'password', 'verify', 'login']:
                feat_type = "Security/Tech"
            elif feature_name in ['drug', 'cocaine', 'illegal']:
                feat_type = "Drugs/Illegal"
            else:
                feat_type = "General Term"
            
            print(f"{i+1:<5} {feature_name:<40} {importance:.6f}   {feat_type:<20}")
    
    print(f"\n💡 KEY INSIGHTS:")
    print("=" * 100)
    print("• The model uses TF-IDF vectorization to convert text into numerical features")
    print("• Features include individual words, bigrams, and trigrams (1-3 word combinations)")
    print("• High-importance features are domain-specific terms related to cybercrime categories")
    print("• The model can detect subtle patterns through phrase combinations (n-grams)")
    print("• Feature importance scores indicate the relative predictive power for classification")
    print("• Both explicit keywords and contextual phrases contribute to accurate detection")

if __name__ == "__main__":
    main()
