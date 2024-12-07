import streamlit as st
import google.generativeai as genai
import os
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure the generative AI API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_text):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input_text)
    return response.text

def input_pdf_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text()
    return text

# Helper to wrap long text
def format_paragraph(text, max_line_length=80):
    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 > max_line_length:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word)
        else:
            current_line.append(word)
            current_length += len(word) + 1
    if current_line:
        lines.append(" ".join(current_line))
    return "\n".join(lines)

# Streamlit interface
st.title("Smart ATS")
st.text("Improve your resume for ATS")
jd = st.text_area("Paste your job description")
uploaded_file = st.file_uploader("Upload your resume", type="pdf", help="Please upload your PDF resume")
submit = st.button("Submit")

if submit:
    if uploaded_file is not None:
        text = input_pdf_text(uploaded_file)
        input_prompt = f"""
        Hey, act like a skilled and experienced application tracking system with a deep understanding 
        of the tech field, software engineering, data science, data analysis, and big data engineering.
        Your task is to evaluate the resume based on the given job description. You must consider the 
        job market is very competitive and provide the best assistance for improving resumes. Assign a 
        percentage match based on the JD and identify missing keywords with high accuracy.
        Resume: {text}
        Job Description: {jd}
        
        I want the response in one single string with the structure:
        {{"JD Match":"%", "MissingKeywords":[], "Profile Summary":""}}
        """
        response = get_gemini_response(input_prompt)

        # Format response for better readability
        try:
            response_json = json.loads(response)
            # Format Profile Summary with line breaks
            if "Profile Summary" in response_json:
                response_json["Profile Summary"] = format_paragraph(response_json["Profile Summary"])
            st.subheader("JD Match Percentage")
            st.text(response_json["JD Match"])
            st.subheader("Missing Keywords")
            st.text(", ".join(response_json["MissingKeywords"]))
            st.subheader("Profile Summary")
            st.text(response_json["Profile Summary"])  # Preserves line breaks
        except json.JSONDecodeError:
            st.text("Error processing response. Please check the input and try again.")
