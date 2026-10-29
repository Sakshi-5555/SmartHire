
import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# Load the dataset
df = pd.read_csv("dataset/Resume.csv")

# Select required columns
df = df[["Resume_str", "Category"]].copy()

# Clean the data
df["Resume_str"] = df["Resume_str"].fillna("").str.strip()
df = df[df["Resume_str"] != ""]
df = df.dropna(subset=["Category"])

# Input and output
X = df["Resume_str"]
y = df["Category"]

# Split into training and testing data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Create the machine learning pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer(
        stop_words="english",
        max_features=10000,
        ngram_range=(1, 2)
    )),
    ("classifier", LogisticRegression(
        max_iter=1000,
        class_weight="balanced"
    ))
])

# Train the model
print("Training the model...")
model.fit(X_train, y_train)

# Evaluate the model
predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("\nModel training completed!")
print(f"Accuracy: {accuracy * 100:.2f}%")

print("\nClassification Report:")
print(classification_report(
    y_test,
    predictions,
    zero_division=0
))

# Save the trained model
with open("resume_model.pkl", "wb") as file:
    pickle.dump(model, file)

print("\nModel saved as resume_model.pkl")
