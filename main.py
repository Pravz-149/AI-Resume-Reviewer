# Description: Streamlit app to provide Resume Review using OpenAI GPT-3
# Author: Pravallika Molleti

__title__ = "Resume Reviewer"
__author__ = "Pravallika Molleti"

from datetime import datetime
from dotenv import load_dotenv
import os
import openai
import streamlit as st

import io
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams

# Function to extract text from a PDF file
def extract_text_from_pdf(uploaded_file):
    file_contents = uploaded_file.read()
    pdf_bytesio = io.BytesIO(file_contents)
    laparams = LAParams()
    text = extract_text(pdf_bytesio, laparams=laparams)
    return text

# Authenticate with OpenAI API using your API key
load_dotenv()

# Access the environment variable
openai.api_key = os.getenv('OPEN_AI_KEY')

# Function to generate resume review
def generate_resume_review(resume_text, length=300):
    # Set up the prompt for OpenAI
    prompt = f"""
Act as a career counselor and provide personalized recommendations to improve the 
quality of my resume: '{resume_text}'.  
All of the categories should have a specific example from resume of how it can be improved:

1. **Summary and Overall Impression:**
    - analyze and give a personalized example from resume to improve
   - If a summary is not present, suggest adding a brief summary highlighting key achievements and career goals.

2. **Structure, Hierarchy, and Formatting:**
- - analyze and give a personalized example from resume to improve
   - Check for clear sections (Work Experience, Education, Projects, Skills, etc.) with appropriate headings and subheadings.
   - if no bulleted points point it out also emphasize uniformity by giving personalized examples
   - if no consistent hierarchy point it out by giving personalized examples

3. **Impact and Quantifiable Results:**
- - analyze and give a personalized example from resume to improve
   - Evaluate each work experience bullet point for specific achievements and quantifiable results.
   - Suggest using action verbs and power words to emphasize accomplishments by giving personalized examples

4. **Vocabulary Enhancement:**
- - analyze and give a personalized example from resume to improve
   - Recommend incorporating industry-specific keywords and terminology.
   - Identify and replace weak or repetitive words with more impactful synonyms by giving personalized examples

5. **Grammar and Sentence Structure:**
- - analyze and give a personalized example from resume to improve
   - Proofread for grammatical errors, typos, and sentence structure.
   - Encourage the use of active voice and avoidance of passive voice constructions by giving personalized examples

6. **Skill Set Enhancement:**
- - analyze and give a personalized example from resume to improve
   - Highlight key skills relevant to the target job.
   - Suggest including additional certifications or completed courses to strengthen the skill set  by provided list of personalized skill words

7. **Additional Sections:**
- - analyze and give a personalized example from resume to improve
   - Recommend adding relevant sections like Awards and Recognition, Leadership Experience, or Publications.
   - Consider including volunteer work, internships, or extracurricular activities that showcase skills.

In continuation to the above, ask a list of details question by question to tailor the recommendations further:

- Number of years of total experience?
- Leadership experience: Have you led any teams? If so, provide details.
- Awards and recognition: Have you received any? Include details.
- Impact metrics: Quantify the impact of your work experience.
- other tools you have used.

The above is just an example of the format. You can use your recommendations and also ask more questions if necessary'"""

    prompt += f"If inputs don't seem like resume content, simply reply with exactly 'Error! Please provide a resume'."

    # Call OpenAI API for chat completion
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    )

    # Extract and return the generated text
    resume_review = response.choices[0].message['content']
    return resume_review

# Function to generate an improvised resume taking the recommendations
def gen_new_resume(resume_text, recommendations, input_details):
    prompt = f"""
             The below is my:
              '{resume_text}',
             The below are the suggestions you have to follow on improving the above resume by using the supporting info from '{input_details}' to the resume .
             Make sure sections are arranged according to hierarchy, adding summary at the top followed by Work Experience, Education, Projects, Skills.
              '{recommendations}'
             Finally, generate the updated resume in the same format as the given resume in points by adding required points and modifying the context and following the suggestions and recommendations.
             Also, make sure the important context or works in the original resume are not excluded """

    # Call OpenAI API for chat completion
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])

    # Extract and return the generated text
    new_resume = response.choices[0].message['content']
    return new_resume

# Define Streamlit app
def app():
    # Set app title and description
    st.set_page_config(
        page_title="Resume Reviewer",
        page_icon=":memo:",
        layout="centered",
        menu_items={"Get Help": "https://www.linkedin.com/in/pravz149", 
                    "About": "Resume Reviewer is a Github repository that reviews resume content using the OpenAI GPT-3.5 API. With a simple prompt, users can quickly upload a resume and receive feedback and recommendations to enhance their resume."},
    )
    st.title("Resume Reviewer")

    # File uploader for resume
    uploaded_file = st.file_uploader("Upload a Resume (PDF)", type=["pdf"])

    # Placeholder for resume text
    resume_text = ""

    # Check if a file has been uploaded
    if uploaded_file is not None:
        # Extract text from the PDF
        resume_text = extract_text_from_pdf(uploaded_file)

        # Display extracted text
        st.subheader("Extracted Text from Resume:")
        st.text_area("", value=resume_text, height=300, max_chars=None)

    # Input fields for generating the resume review
    st.subheader("Generate Resume Review:")
    fixed_length = 300  # Set your desired fixed length here

    # Initialize generated_text outside the if block
    generated_text = ""

    # Generate and display the resume review
    if st.button("Generate Review"):
        if resume_text == "":
            st.error("Please upload a resume before generating a review.", icon="❌")
        else:
            # Clear existing elements
            st.empty()

            with st.spinner("Generating resume review, this may take a while..."):
                try:
                    # Generate the resume review
                    generated_text = generate_resume_review(resume_text, fixed_length)

                    # Display the generated review
                    st.subheader("Generated Resume Review:")
                    st.write(generated_text)

                except Exception as e:
                    print(e)
                    st.error("An error occurred while generating the resume review. Please try again later.")
                    return

    # Store generated_text in session state
    st.session_state.generated_text = generated_text

    # Asking for the details that can be added to the resume
    input_details = st.text_area("Enter the required details as per recommendations")

    if st.button("Process Resume"):
        # Clear existing elements
        st.empty()

        # Retrieve the stored generated_text
        generated_text = st.session_state.generated_text

        # Generate the new resume
        result = gen_new_resume(resume_text, generated_text, input_details)

        # Display the generated resume
        st.subheader("Generated New Resume:")
        st.write(result)

    st.markdown('---')
    st.markdown('Created by [Pravallika Molleti](https://www.linkedin.com/in/pravz149)')

# Run the app
if __name__ == "__main__":
    app()
