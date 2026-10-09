import pickle

try:
    with open('xgboost_mourabaha_final.pkl', 'rb') as f:
        model = pickle.load(f)
    print("Model type:", type(model))
    if hasattr(model, 'feature_names_in_'):
        print("Feature names:", model.feature_names_in_)
    else:
        print("Model doesn't have feature_names_in_")
except Exception as e:
    print("Error:", e)
