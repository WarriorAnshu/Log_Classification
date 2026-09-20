from sentence_transformers import SentenceTransformer
import joblib

transformer_model = SentenceTransformer('all-MiniLM-L6-v2')
classifier_model = joblib.load('logistic_model.pkl')
def classify_with_bert(log_message):
    
    message_embedding = transformer_model.encode([log_message])
    probabilities = classifier_model.predict_proba(message_embedding)[0]
    if probabilities.max() < 0.5:
        return 'Unclassified'
    predicted_label = classifier_model.predict([message_embedding])[0]
    return predicted_label

