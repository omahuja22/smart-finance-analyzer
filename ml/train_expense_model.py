import os
import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

# Absolute path handling
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "expenses_data.csv")

# Load dataset
df = pd.read_csv("expenses_data.csv")

X = df["text"]
y = df["category"]
# ML Pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("clf", MultinomialNB())
])

# Train model
model.fit(X, y)

# Save model
MODEL_PATH = os.path.join(BASE_DIR, "expense_model.pkl")
with open(MODEL_PATH, "wb") as f:
    pickle.dump(model, f)

print("✅ Expense categorization model trained & saved successfully")
