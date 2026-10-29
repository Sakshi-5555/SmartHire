
import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash
import fitz  # PyMuPDF
import pickle
import mysql.connector

app = Flask(__name__)
with open("resume_model.pkl", "rb") as file:
    resume_model = pickle.load(file)
app.config["UPLOAD_FOLDER"] = "uploads/resumes"
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {"pdf"}

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="smarthire"
    )


import re

def calculate_job_match(resume_text, required_skills):
    if not required_skills:
        return 0, []

    # Convert resume text to lowercase
    resume_text = resume_text.lower()

    # Split the required skills into individual skills
    skills = [
        skill.strip().lower()
        for skill in required_skills.split(",")
        if skill.strip()
    ]

    matched_skills = []

    for skill in skills:
        # Match the skill as a complete phrase or word
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, resume_text):
            matched_skills.append(skill)

    match_percentage = round(
        (len(matched_skills) / len(skills)) * 100, 2
    )

    return match_percentage, matched_skills

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyzer")
def analyzer():
    return render_template("analyzer.html")

@app.route("/analyze-resume", methods=["POST"])
def analyze_resume():
    if "resume" not in request.files:
        return "Please upload a resume."

    resume_file = request.files["resume"]

    if resume_file.filename == "":
        return "No file selected."

    if not resume_file.filename.lower().endswith(".pdf"):
        return "Please upload a PDF file."

    try:
        pdf_bytes = resume_file.read()

        with fitz.open(stream=pdf_bytes, filetype="pdf") as pdf:
            resume_text = "\n".join(
                page.get_text() for page in pdf
            ).strip()

        if not resume_text:
            return "No readable text found in the PDF."

        predicted_category = resume_model.predict([resume_text])[0]
        
        # Find jobs that match the uploaded resume
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, title, company, location, salary,
                   description, required_skills
            FROM jobs
        """)

        available_jobs = cursor.fetchall()
        cursor.close()
        connection.close()

        recommended_jobs = []

        for job in available_jobs:
            match_score, matched_skills = calculate_job_match(
                resume_text,
                job.get("required_skills") or ""
            )

            if match_score > 0:
                job["match_score"] = match_score
                job["matched_skills"] = matched_skills
                recommended_jobs.append(job)

        recommended_jobs.sort(
            key=lambda job: job["match_score"],
            reverse=True
        )

        recommended_jobs = recommended_jobs[:3]


        probabilities = resume_model.predict_proba([resume_text])[0]

        top_indices = probabilities.argsort()[-3:][::-1]

        top_categories = [
        {
        "category": resume_model.classes_[i],
        "confidence": round(probabilities[i] * 100, 2)
        }
        for i in top_indices
    ]

        confidence = top_categories[0]["confidence"]

        
        return render_template(
            "analyzer_result.html",
            category=predicted_category,
            confidence=confidence,
            top_categories=top_categories,
            recommended_jobs=recommended_jobs
        )


    except Exception as error:
        app.logger.exception("Resume analysis failed")
        return "Unable to analyze this PDF. Please try another file."



@app.route("/jobs")
def jobs():
    search = request.args.get("search", "").strip()

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if search:
        query = """
            SELECT * FROM jobs
            WHERE title LIKE %s
               OR company LIKE %s
               OR location LIKE %s
        """
        keyword = f"%{search}%"
        cursor.execute(query, (keyword, keyword, keyword))
    else:
        cursor.execute("SELECT * FROM jobs")

    jobs_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "jobs.html",
        jobs=jobs_list,
        search=search
    )



@app.route("/apply/<int:job_id>", methods=["GET", "POST"])
def apply_job(job_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))
    job = cursor.fetchone()
    cursor.close()
    connection.close()

    if job is None:
        return "Job not found", 404

    if request.method == "POST":
        applicant_name = request.form.get("applicant_name", "").strip()
        email = request.form.get("email", "").strip()
        resume = request.files.get("resume")

        if not applicant_name or not email:
            return "Name and email are required.", 400

        if not resume or resume.filename == "":
            return "Please upload your resume.", 400

        if not resume.filename.lower().endswith(".pdf"):
            return "Only PDF resumes are allowed.", 400

        filename = secure_filename(resume.filename)

        if not filename:
            return "Invalid filename.", 400

        # Create a unique filename to avoid overwriting files
        import uuid
        filename = f"{uuid.uuid4().hex}_{filename}"

        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        # Check that the uploaded file is actually a PDF
        file_header = resume.stream.read(5)
        resume.stream.seek(0)

        if file_header != b"%PDF-":
            return "The uploaded file is not a valid PDF.", 400

        resume.save(file_path)

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute(
                """INSERT INTO applications
                   (job_id, applicant_name, email, resume_filename)
                   VALUES (%s, %s, %s, %s)""",
                (job_id, applicant_name, email, filename)
            )

            connection.commit()
            cursor.close()
            connection.close()

        except Exception:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise

        return render_template("success.html")

    return render_template("apply.html", job=job)



if __name__ == "__main__":
    app.run(debug=True)
