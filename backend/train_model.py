
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from backend.training_data import training_examples
import joblib
from pathlib import Path


# Separate customer sentences and their intent labels
sentences = [example[0] for example in training_examples]
labels = [example[1] for example in training_examples]


# Build our machine-learning pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
    ("classifier", LogisticRegression(max_iter=1000))
])


# Train the model using our examples
model.fit(sentences, labels)


# Test the trained model
test_messages = [
    "I want some earphones",
    "Find shoes under 2500",
    "Show me all the items"
]

print("Model trained successfully!")
print()

for message in test_messages:
    prediction = model.predict([message])[0]

    print("Customer:", message)
    print("Predicted intent:", prediction)
    print("-" * 40)

    # Save the trained model
model_path = Path(__file__).with_name("intent_model.joblib")

joblib.dump(model, model_path)

print(f"\nModel saved successfully at: {model_path}")
