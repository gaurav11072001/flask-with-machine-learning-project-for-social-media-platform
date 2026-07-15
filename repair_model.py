import pickle
import os

filepath = 'xai_cybercrime_model.pkl'

if os.path.exists(filepath):
    try:
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        model = model_data.get('model')
        if model and hasattr(model, 'estimators_'):
            if not hasattr(model, 'monotonic_cst'):
                model.monotonic_cst = None
                print("✅ Fixed monotonic_cst in the model object.")
            else:
                print("ℹ️ monotonic_cst already exists.")
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"✅ Successfully updated and saved {filepath}")
        
    except Exception as e:
        print(f"❌ Error during repair: {e}")
else:
    print(f"❌ {filepath} not found.")
