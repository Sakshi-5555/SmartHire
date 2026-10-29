
import pickle

# Load the trained model
with open("resume_model.pkl", "rb") as file:
    model = pickle.load(file)

# Sample resume text
resume_text = """
Python Developer with experience in Python, Flask, MySQL,
REST APIs, HTML, CSS, JavaScript, and software development.
Worked on web applications and database integration.
"""

# Predict the job category
prediction = model.predict([resume_text])

print("Predicted Job Category:", prediction[0])
