#!/usr/bin/env python3

from xai_cybercrime_model import CybercrimeXAIModel

def main():
    print("Loading XAI Cybercrime Detection Model...")
    model = CybercrimeXAIModel()
    
    if not model.load_model():
        print("Failed to load model!")
        return
    
    print("\n=== GETTING MODEL INSIGHTS ===")
    insights = model.get_model_insights(top_features=50)
    
    print("\n" + "="*80)
    print("TOP 50 MOST IMPORTANT PREDICTIVE FEATURES")
    print("="*80)
    print(f"{'Rank':<4} {'Feature':<35} {'Importance Score':<15}")
    print("-" * 80)
    
    if 'top_features' in insights:
        for i, feat in enumerate(insights['top_features']):
            feature_name = feat['feature']
            importance = feat['importance']
            print(f"{i+1:<4} {feature_name:<35} {importance:.8f}")
    else:
        print("No feature importance data available.")
    
    print("\n" + "="*80)
    print("MODEL INFORMATION")
    print("="*80)
    
    if 'model_params' in insights:
        params = insights['model_params']
        print(f"Model Type: {params.get('model_type', 'Unknown')}")
        print(f"Total Features: {params.get('n_features', 0):,}")
        print(f"Number of Classes: {params.get('n_classes', 0)}")
        print(f"Classes: {', '.join(params.get('classes', []))}")

if __name__ == "__main__":
    main()
