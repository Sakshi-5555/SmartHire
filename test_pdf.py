
import fitz
import pickle

# Load the trained model
with open("resume_model.pkl", "rb") as file:
    model = pickle.load(file)

# Enter the PDF path
pdf_path = input("Enter the path of your PDF resume: ").strip().strip('"')

try:
    # Extract text from the PDF
    document = fitz.open(pdf_path)
    resume_text = ""

    for page in document:
        resume_text += page.get_text()

    document.close()

    if not resume_text.strip():
        print("No readable text found in this PDF.")

    else:
        print("\nResume text extracted successfully!")

        # Predict the job category
        prediction = model.predict([resume_text])[0]

        print("\nPredicted Job Category:", prediction)

except Exception as error:
    print("Error:", error)
