import streamlit as st
import fitz
import google.generativeai as genai
import os

from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def extract_text(pdf):
    text = ""

    doc = fitz.open(stream=pdf.read(), filetype="pdf")

    for page in doc:
        text += page.get_text()

    return text


def extract_skills(text, skills_list):
    found_skills = []

    for skill in skills_list:
        if skill.lower() in text.lower():
            found_skills.append(skill)

    return found_skills

def get_ai_feedback(resume_text, job_description):

    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""

    You are an experienced HR recruiter.

    Compare this resume with the job description.

    Resume:

    {resume_text}

    Job Description:

    {job_description}

    Give:

    1. Overall evaluation

    2. Strengths

    3. Weaknesses

    4. Suggestions for improvement

    5. Estimated ATS match percentage

    Keep the response clear and professional.

    """

    response = model.generate_content(prompt)

    return response.text

st.set_page_config(

    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Resume Analyzer")
st.markdown("### Upload your resume and compare it with a job description.")

st.divider()

uploaded_file = st.file_uploader(
    "Upload your Resume (PDF)",
    type=["pdf"]
)

job_description = st.text_area(
    "Paste the Job Description",
    height=250
)

if st.button("Analyze Resume"):

    if uploaded_file is None:
        st.warning("Please upload your resume first.")

    elif job_description.strip() == "":
        st.warning("Please paste a job description.")

    else:
        resume_text = extract_text(uploaded_file)
        skills = [
            "Python",
            "SQL",
            "Machine Learning",
            "Deep Learning",
            "Git",
            "GitHub",
            "Docker",
            "AWS",
            "Java",
            "JavaScript",
            "HTML",
            "CSS",
            "C++",
            "TensorFlow",
            "PyTorch",
            "Pandas",
            "NumPy",
            "Scikit-learn"
        ]
        matched_skills = extract_skills(resume_text, skills)
        required_skills = extract_skills(job_description, skills)

        st.success("Resume uploaded successfully!")

        st.subheader("✅ Skills Found")
        st.write(matched_skills)

        matched_count = len(set(matched_skills) & set(required_skills))

        total_skills = len(required_skills)

        if total_skills == 0:
            st.warning("⚠️ No recognizable skills were found in the job description. Please paste a complete job description.")
            st.stop()

        match_score = round((matched_count / total_skills) * 100)

        missing_skills = []
        st.subheader("🎯 Resume Match Score")

        st.progress(match_score / 100)

        st.write(f"Match Score: {match_score}%")
        for skill in required_skills:
            if skill.lower() not in resume_text.lower():
                missing_skills.append(skill)

        st.subheader("❌ Missing Skills")
        st.write(missing_skills)
        st.subheader("💡 Suggestions")

        if len(missing_skills) == 0:
            st.success("Excellent! Your resume already matches the job description very well.")
        else:
            for skill in missing_skills:
                st.write(f"• Consider adding experience with **{skill}** if you have worked with it.")
        
        st.subheader("🤖 AI Resume Review")

        with st.spinner("Gemini is analyzing your resume..."):
            try:
                ai_feedback = get_ai_feedback(
                    resume_text,
                    job_description
                )

                st.write(ai_feedback)
                
            except Exception as e:
                st.error("Unable to get AI feedback.")
                st.error(str(e))

        st.subheader("📄 Resume Preview")

        st.text_area(
        "Extracted Resume Text",
        resume_text,
        height=300
)
