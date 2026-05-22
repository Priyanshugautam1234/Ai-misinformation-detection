import os
import joblib

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "models")
model_path = os.path.join(MODELS_DIR, "spam_model.pkl")
vectorizer_path = os.path.join(MODELS_DIR, "vectorizer.pkl")

print(f"Loading model from: {model_path}")
print(f"Loading vectorizer from: {vectorizer_path}")

try:
    model = joblib.load(model_path)
    print("Model loaded successfully!")
    print(f"Model type: {type(model)}")
    
    vectorizer = joblib.load(vectorizer_path)
    print("Vectorizer loaded successfully!")
    print(f"Vectorizer type: {type(vectorizer)}")
    
    # Test a simple inference
    test_text = ["Congratulations! You've won a free ticket. Call now!"]
    X_test = vectorizer.transform(test_text)
    prediction = model.predict(X_test)
    print(f"Test prediction: {prediction}")
    
    # Check if predict_proba is supported
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X_test)
        print(f"Test probabilities: {probs}")
    
except Exception as e:
    print(f"Error: {e}")
