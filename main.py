# Description: Streamlit app to provide Resume Review using OpenAI GPT-3
# Author: Pravallika Molleti

__title__ = "Resume Reviewer"
__author__ = "Pravallika Molleti"

import streamlit.components.v1 as components
import pdfkit
from datetime import datetime
import os
import openai
import streamlit as st
import io
from pdfminer.high_level import extract_text
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
import base64


# Authenticate with OpenAI API using your API key
# openai.api_key = os.getenv('OPEN_AI_KEY')
openai.api_key = "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"

config = pdfkit.configuration(wkhtmltopdf=r"C:\Users\Pravallika Molleti\AI RESUME REVIEWER\AI-Resume-Reviewer\wkhtmltopdf.exe")


#Function to extract HTML from PDF
def extract_html_from_pdf(uploaded_file):
    file_contents = uploaded_file.read()
    pdf_bytesio = io.BytesIO(file_contents)
    html_bytesio = io.BytesIO()
    laparams = LAParams()
    extract_text_to_fp(pdf_bytesio, html_bytesio, laparams=laparams)
    html_text = html_bytesio.getvalue().decode("utf-8")
    return html_text



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
def gen_new_resume(resume_text, recommendations):
    prompt = f"""
             The below is my resume:
              '{resume_text}',
             The below are the suggestions you have to follow on improving the above resume.
              '{recommendations}'
             Modify the context of resume_text by following the above recommendations and below suggestions.
             Make sure sections are arranged according to hierarchy, adding name, details, related profile contacts, links, summary at the top followed by Work Experience, Education (based on the preference), Projects, Skills.
             Also, make sure the important context or works in the original resume are not excluded and make them detail as per recommendations.
             and finally Generate the HTML text of the updated resume (HTML of the resume is only i want).
              """

    # Call OpenAI API for chat completion
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])

    # Extract and return the generated text
    new_resume = response.choices[0].message['content']
    return new_resume

# Function to generate PDF from HTML content
def generate_pdf(html_content, filename="test2_generated_resume.pdf"):
    # Save the HTML content to a temporary file
    temp_html_path = "temp_resume.html"
    with open(temp_html_path, "w", encoding="utf-8") as file:
        file.write(html_content)

    # Clean up temporary HTML file
    os.remove(temp_html_path)

    return pdfkit.from_string(html_content, filename)

# Utility function to create a download link for binary files
def get_binary_file_downloader_html(bin_file, label='Download PDF'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{bin_file}" target="_blank">{label}</a>'
    return href

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
        resume_text = extract_html_from_pdf(uploaded_file)
        st.write(resume_text)

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
    # input_details = st.text_area("Enter the required details as per recommendations")

    # Initialize result outside the if block
    result = ""


    if st.button("Process Resume"):
        # Clear existing elements
        st.empty()

        # Retrieve the stored generated_text
        generated_text = st.session_state.generated_text

        with st.spinner("Generating updated resume, this may take a while..."):
            try:
               # Generate the new resume
               result = gen_new_resume(resume_text, generated_text)

               # Display the generated resume in HTML format
               st.subheader("Generated New Resume (HTML):")
               # st.markdown(result, unsafe_allow_html=True)

               # Before converting to PDF
               st.write("HTML Content:", result)

            except Exception as e:
                    print(e)
                    st.error("An error occurred while generating the updated resume. Please try again later.")
                    return

        generate_pdf(result)

    # # Store result in session state
    # st.session_state.result = result

    # # Create a download button for PDF
    # if st.button("Download as PDF"):
    #     result = st.session_state.result
    #     generate_pdf(result)
        
        # final_pdf = generate_pdf(result)
        # st.write(final_pdf)

        # # Display a link to download the PDF
        # st.markdown(get_binary_file_downloader_html(final_pdf,'Download PDF'), unsafe_allow_html=True)

    st.markdown('---')
    st.markdown('Created by [Pravallika Molleti](https://www.linkedin.com/in/pravz149)')

# Run the app
if __name__ == "__main__":
    app()