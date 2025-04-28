import streamlit as st
import PyPDF2
import io
import re
import pandas as pd
import os
import time
from io import StringIO
import docx2txt
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# Set page title and favicon - THIS MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Resume Reviewer & Career Coach",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.streamlit.io/community',
        'Report a bug': "https://github.com/yourusername/resume-reviewer/issues",
        'About': "# Resume Reviewer & Career Coach\nThis app analyzes resumes and provides feedback and job recommendations."
    }
)
# Custom CSS
st.markdown("""
<style>
    /* Dark theme with white text */
    .main-header {
        font-size: 2.5rem;
        color: #FFFFFF;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #E0E0E0;
        margin-bottom: 1rem;
    }
    .section {
        background-color: #2C2C2C;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #FFFFFF;
    }
    .highlight {
        background-color: #212121;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #BB86FC;
        color: #FFFFFF;
    }
    .job-card {
        background-color: #2C2C2C;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 1rem;
        color: #FFFFFF;
    }
    .stApp {
        background-color: #121212;
    }
    .upload-section {
        display: flex;
        justify-content: center;
        align-items: center;
        background-color: #1E1E1E;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        margin: 2rem auto;
        max-width: 800px;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding: 1rem;
        font-size: 0.8rem;
        color: #BB86FC;
    }
    /* Fix text visibility */
    h1, h2, h3, h4, h5, h6, p, div, .stMarkdown, .streamlit-expanderHeader {
        color: #FFFFFF !important;
    }
    label, span {
        color: #E0E0E0 !important;
    }
    /* Style for main content */
    .main-content {
        background-color: #121212;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
    /* Style for file uploader */
    .css-1dhfpht {
        background-color: #2C2C2C;
        border: 2px dashed #BB86FC;
        color: #FFFFFF;
    }
    /* Style for tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #2C2C2C;
        color: #FFFFFF;
        padding: 10px 20px;
        border-radius: 5px 5px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #BB86FC;
        color: #000000;
    }
    /* Sidebar */
    .css-1d391kg, .css-1wrcr25, .css-ocqkz7 {
        background-color: #1E1E1E;
    }
    /* Buttons */
    .stButton button {
        background-color: #BB86FC;
        color: #000000;
    }
    /* Info boxes */
    .stAlert {
        background-color: #2C2C2C;
        color: #FFFFFF;
    }
    .st-bj {
        background-color: #2C2C2C;
        color: #FFFFFF;
    }
    .st-bk {
        background-color: #2C2C2C;
        color: #FFFFFF;
    }
    .st-bl {
        background-color: #2C2C2C;
        color: #FFFFFF;
    }
    /* Success message colors */
    .stSuccess {
        background-color: #1E1E1E !important;
    }
    .stSuccess > div {
        color: #BB86FC !important;
    }
    /* Info message colors */
    .stInfo {
        background-color: #1E1E1E !important;
    }
    .stInfo > div {
        color: #03DAC6 !important;
    }
</style>
""", unsafe_allow_html=True)

def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file."""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page_num].extract_text()
    return text

def extract_text_from_docx(docx_file):
    """Extract text from a DOCX file."""
    text = docx2txt.process(docx_file)
    return text

def extract_text_from_txt(txt_file):
    """Extract text from a TXT file."""
    content = txt_file.read().decode('utf-8')
    return content

def parse_resume(text):
    """Parse the resume text to extract key information."""
    # Initialize sections
    sections = {
        'contact_info': {},
        'education': [],
        'experience': [],
        'skills': [],
        'summary': ""
    }
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    if email_match:
        sections['contact_info']['email'] = email_match.group(0)
    
    # Extract phone number
    phone_pattern = r'(?:(?:\+\d{1,2}\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})'
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        sections['contact_info']['phone'] = phone_match.group(0)
    
    # Extract skills (look for common skill section identifiers)
    skill_section = re.search(r'(?i)(?:SKILLS|TECHNICAL SKILLS|CORE COMPETENCIES).*?(?:EDUCATION|EXPERIENCE|PROJECTS|CERTIFICATIONS|\Z)', text, re.DOTALL)
    if skill_section:
        skill_text = skill_section.group(0)
        skill_list = re.findall(r'[A-Za-z+#]+(?:\s[A-Za-z+#]+)*', skill_text)
        sections['skills'] = [skill for skill in skill_list if len(skill) > 2 and skill.lower() not in ['skills', 'technical', 'core', 'competencies', 'education', 'experience', 'projects', 'certifications']]
    
    # Extract education
    edu_section = re.search(r'(?i)EDUCATION.*?(?:EXPERIENCE|SKILLS|PROJECTS|CERTIFICATIONS|\Z)', text, re.DOTALL)
    if edu_section:
        edu_text = edu_section.group(0)
        # Look for education entries with degree or university keywords
        edu_entries = re.findall(r'(?:(?:Bachelor|Master|Doctor|PhD|MBA|BS|BA|MS|MD|JD)[^\n.]*)|(?:[^\n.]*(?:University|College|Institute|School)[^\n.]*)', edu_text)
        sections['education'] = [entry.strip() for entry in edu_entries if len(entry.strip()) > 5]
    
    # Extract experience
    exp_section = re.search(r'(?i)(?:EXPERIENCE|WORK EXPERIENCE|PROFESSIONAL EXPERIENCE).*?(?:EDUCATION|SKILLS|PROJECTS|CERTIFICATIONS|\Z)', text, re.DOTALL)
    if exp_section:
        exp_text = exp_section.group(0)
        # Split experience entries by date patterns or company names
        exp_entries = re.split(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b', exp_text)
        sections['experience'] = [entry.strip() for entry in exp_entries if len(entry.strip()) > 10 and not re.match(r'(?i)(?:EXPERIENCE|WORK EXPERIENCE|PROFESSIONAL EXPERIENCE)', entry.strip())]
    
    # Extract summary
    summary_section = re.search(r'(?i)(?:SUMMARY|PROFESSIONAL SUMMARY|PROFILE).*?(?:EXPERIENCE|EDUCATION|SKILLS|\Z)', text, re.DOTALL)
    if summary_section:
        summary_text = summary_section.group(0)
        clean_summary = re.sub(r'(?i)(?:SUMMARY|PROFESSIONAL SUMMARY|PROFILE)[:\s]*', '', summary_text).strip()
        sections['summary'] = clean_summary.split('\n')[0]
    
    return sections

def analyze_resume(resume_data):
    """Use an LLM to analyze the resume and provide feedback."""
    # Get API key from environment variables or secrets
    api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
    
    if not api_key:
        return {
            "strengths": ["API Key Not Found"],
            "weaknesses": ["Missing Groq API key in environment variables"],
            "improvements": ["Add GROQ_API_KEY to your .env file or Streamlit secrets"],
            "job_suggestions": []
        }
    
    # Prepare the input for the LLM - force strict JSON response
    prompt = f"""
    I need you to act as a professional resume reviewer and career coach. Analyze the following resume information:
    
    Contact Info: {resume_data['contact_info']}
    Summary: {resume_data['summary']}
    Skills: {resume_data['skills']}
    Education: {resume_data['education']}
    Experience: {resume_data['experience']}
    
    Please provide:
    1. Three key strengths of this resume
    2. Three areas for improvement
    3. Three specific suggestions to enhance this resume
    4. Three job roles that would be a good fit based on this profile, with brief reasoning for each
    
    IMPORTANT: Your entire response must be valid JSON that strictly follows this structure with no additional text before or after:
    {{
        "strengths": ["strength1", "strength2", "strength3"],
        "weaknesses": ["weakness1", "weakness2", "weakness3"],
        "improvements": ["improvement1", "improvement2", "improvement3"],
        "job_suggestions": [
            {{"title": "Job Title 1", "reason": "Reason 1"}},
            {{"title": "Job Title 2", "reason": "Reason 2"}},
            {{"title": "Job Title 3", "reason": "Reason 3"}}
        ]
    }}
    """
    
    # Maximum number of retries for API calls
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                json={
                    "model": "meta-llama/llama-4-maverick-17b-128e-instruct",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,  # Lower temperature for more deterministic output
                    "response_format": {"type": "json_object"}  # Request JSON format specifically
                },
                timeout=30  # Add a timeout to avoid hanging on requests
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Try to clean up common JSON formatting issues
                content = content.strip()
                # Remove any markdown code block markers if present
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                try:
                    return json.loads(content)
                except json.JSONDecodeError as e:
                    st.error(f"Error parsing JSON response: {str(e)}")
                    
                    # Extract information using regex as fallback
                    strengths = re.findall(r'"strengths":\s*\[\s*"([^"]+)"', content)
                    weaknesses = re.findall(r'"weaknesses":\s*\[\s*"([^"]+)"', content)
                    improvements = re.findall(r'"improvements":\s*\[\s*"([^"]+)"', content)
                    job_titles = re.findall(r'"title":\s*"([^"]+)"', content)
                    job_reasons = re.findall(r'"reason":\s*"([^"]+)"', content)
                    
                    job_suggestions = []
                    for i in range(min(len(job_titles), len(job_reasons))):
                        job_suggestions.append({"title": job_titles[i], "reason": job_reasons[i]})
                    
                    # Create a structured response from what we could extract
                    return {
                        "strengths": strengths if strengths else ["Could not extract strengths from response"],
                        "weaknesses": weaknesses if weaknesses else ["Could not extract weaknesses from response"],
                        "improvements": improvements if improvements else ["Could not extract improvements from response"],
                        "job_suggestions": job_suggestions if job_suggestions else []
                    }
                    
            elif response.status_code == 401:
                st.error("Authentication Error: Your Groq API key is invalid or expired. Please check your API key in the .env file.")
                return {
                    "strengths": ["API Authentication Error"],
                    "weaknesses": ["Invalid or expired Groq API key"],
                    "improvements": ["Update your API key in the .env file"],
                    "job_suggestions": []
                }
            elif response.status_code == 503:
                error_msg = "Groq API Service Unavailable"
                if attempt < max_retries - 1:
                    st.warning(f"{error_msg}. Retrying in {retry_delay} seconds... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(retry_delay)
                    continue
                else:
                    st.error(f"{error_msg}. The Groq API is currently experiencing issues or high load. Please try again later.")
                    return {
                        "strengths": ["Service Unavailable"],
                        "weaknesses": ["Groq API is temporarily down or overloaded"],
                        "improvements": ["Try again later when the service is available", 
                                        "Check Groq API status at https://status.groq.com/", 
                                        "Consider using a different model or service if this persists"],
                        "job_suggestions": []
                    }
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
                if attempt < max_retries - 1:
                    st.warning(f"Retrying in {retry_delay} seconds... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(retry_delay)
                    continue
                else:
                    return {
                        "strengths": [f"API Error: {response.status_code}"],
                        "weaknesses": ["Could not process the resume"],
                        "improvements": ["Please try again later or check API status at https://status.groq.com/"],
                        "job_suggestions": []
                    }
        except requests.exceptions.Timeout:
            st.error("Request timeout. The Groq API took too long to respond.")
            if attempt < max_retries - 1:
                st.warning(f"Retrying in {retry_delay} seconds... (Attempt {attempt+1}/{max_retries})")
                time.sleep(retry_delay)
                continue
            else:
                return {
                    "strengths": ["Request Timeout"],
                    "weaknesses": ["API response took too long"],
                    "improvements": ["Try again when network conditions improve",
                                    "Check if the Groq API is experiencing delays"],
                    "job_suggestions": []
                }
        except Exception as e:
            st.error(f"Error: {str(e)}")
            if attempt < max_retries - 1:
                st.warning(f"Retrying in {retry_delay} seconds... (Attempt {attempt+1}/{max_retries})")
                time.sleep(retry_delay)
                continue
            else:
                return {
                    "strengths": ["Processing Error"],
                    "weaknesses": ["Could not connect to the Groq API"],
                    "improvements": ["Check your internet connection and API key in the .env file"],
                    "job_suggestions": []
                }
    
    # If we've exhausted all retries
    return {
        "strengths": ["API Connection Failed"],
        "weaknesses": ["Could not establish reliable connection to Groq API after multiple attempts"],
        "improvements": ["Check your internet connection", 
                        "Verify Groq API status at https://status.groq.com/",
                        "Try again later when service might be less busy"],
        "job_suggestions": []
    }

def main():
    # Sidebar with app info
    with st.sidebar:
        st.image("https://www.pngitem.com/pimgs/m/194-1943472_resume-cv-icon-png-transparent-png.png", width=150)
        
        st.title("About")
        st.info(
            """
            This app uses AI to:
            * Extract information from your resume
            * Analyze your resume's strengths and weaknesses
            * Provide actionable improvement suggestions
            * Recommend suitable job roles
            """
        )
        
        st.title("How it works")
        st.success(
            """
            1. Upload your resume (PDF, DOCX, or TXT)
            2. The app extracts and organizes your information
            3. AI analyzes your resume content
            4. Review the analysis and job recommendations
            5. Make improvements based on suggestions
            """
        )
        
        st.markdown("---")
        st.markdown("Developed with Hunzala Rasheed")
    
    # Main content - wrap in a container with background color
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">Resume Reviewer & Career Coach</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #FFFFFF;">Upload your resume to get personalized feedback and job recommendations</p>', unsafe_allow_html=True)
    
    # Upload section with better styling
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload your resume (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_file is not None:
        # Extract text based on file type
        file_type = uploaded_file.name.split(".")[-1].lower()
        
        try:
            if file_type == "pdf":
                resume_text = extract_text_from_pdf(uploaded_file)
            elif file_type == "docx":
                resume_text = extract_text_from_docx(uploaded_file)
            elif file_type == "txt":
                resume_text = extract_text_from_txt(uploaded_file)
            else:
                st.error("Unsupported file format")
                return
            
            # Create tabs
            tab1, tab2, tab3 = st.tabs(["Extracted Information", "Resume Analysis", "Job Recommendations"])
            
            # Parse the resume
            resume_data = parse_resume(resume_text)
            
            # Display parsed information
            with tab1:
                st.markdown('<h2 class="sub-header">Extracted Information</h2>', unsafe_allow_html=True)
                
                # Contact information
                st.markdown('<div class="section">', unsafe_allow_html=True)
                st.subheader("Contact Information")
                for key, value in resume_data['contact_info'].items():
                    st.write(f"**{key.title()}:** {value}")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Summary
                if resume_data['summary']:
                    st.markdown('<div class="section">', unsafe_allow_html=True)
                    st.subheader("Summary")
                    st.write(resume_data['summary'])
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Skills
                if resume_data['skills']:
                    st.markdown('<div class="section">', unsafe_allow_html=True)
                    st.subheader("Skills")
                    skill_cols = st.columns(3)
                    skills_per_col = len(resume_data['skills']) // 3 + 1
                    
                    for i, skill in enumerate(resume_data['skills']):
                        col_index = i // skills_per_col
                        with skill_cols[min(col_index, 2)]:
                            st.write(f"• {skill}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Education
                if resume_data['education']:
                    st.markdown('<div class="section">', unsafe_allow_html=True)
                    st.subheader("Education")
                    for edu in resume_data['education']:
                        st.write(f"• {edu}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Experience
                if resume_data['experience']:
                    st.markdown('<div class="section">', unsafe_allow_html=True)
                    st.subheader("Experience")
                    for exp in resume_data['experience']:
                        st.write(f"• {exp}")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Analyze the resume
            with st.spinner('Analyzing your resume...'):
                analysis = analyze_resume(resume_data)
            
            # Display analysis
            with tab2:
                st.markdown('<h2 class="sub-header">Resume Analysis</h2>', unsafe_allow_html=True)
                
                # Strengths
                st.markdown('<div class="section">', unsafe_allow_html=True)
                st.subheader("Key Strengths")
                for strength in analysis['strengths']:
                    st.markdown(f'<div class="highlight">✓ {strength}</div>', unsafe_allow_html=True)
                    st.write("")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Areas for improvement
                st.markdown('<div class="section">', unsafe_allow_html=True)
                st.subheader("Areas for Improvement")
                for weakness in analysis['weaknesses']:
                    st.markdown(f'<div class="highlight">△ {weakness}</div>', unsafe_allow_html=True)
                    st.write("")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Suggestions
                st.markdown('<div class="section">', unsafe_allow_html=True)
                st.subheader("Recommendations")
                for improvement in analysis['improvements']:
                    st.markdown(f'<div class="highlight">⭑ {improvement}</div>', unsafe_allow_html=True)
                    st.write("")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Display job recommendations
            with tab3:
                st.markdown('<h2 class="sub-header">Job Recommendations</h2>', unsafe_allow_html=True)
                
                for job in analysis['job_suggestions']:
                    st.markdown(f'<div class="job-card">', unsafe_allow_html=True)
                    st.subheader(job['title'])
                    st.write(f"**Why this is a good fit:** {job['reason']}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("""
                <div style="margin-top: 2rem; text-align: center; color: #FFFFFF;">
                These job recommendations are based on your resume. 
                Update your resume with the suggested improvements for better matches.
                </div>
                """, unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    
    else:
        # Display instructions when no file is uploaded
        st.markdown("""
        <div style="text-align: center; margin-top: 2rem; color: #FFFFFF;">
            <img src="https://www.pngitem.com/pimgs/m/194-1943472_resume-cv-icon-png-transparent-png.png" width="150px">
            <h3 style="color: #FFFFFF;">How it works:</h3>
            <p style="color: #FFFFFF; font-size: 1.1rem;">1. Upload your resume in PDF, DOCX, or TXT format</p>
            <p style="color: #FFFFFF; font-size: 1.1rem;">2. Our AI will extract key information</p>
            <p style="color: #FFFFFF; font-size: 1.1rem;">3. Get personalized analysis and improvement suggestions</p>
            <p style="color: #FFFFFF; font-size: 1.1rem;">4. Discover job recommendations that match your profile</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display example resume points
        st.markdown("<h3 style='text-align: center; margin-top: 3rem; color: #FFFFFF;'>Example Resume Analysis</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section">', unsafe_allow_html=True)
            st.subheader("Common Resume Strengths")
            st.markdown("<p style='color: #FFFFFF;'>✓ Quantifiable achievements with metrics</p>", unsafe_allow_html=True)
            st.markdown("<p style='color: #FFFFFF;'>✓ Clear and concise experience descriptions</p>", unsafe_allow_html=True)
            st.markdown("<p style='color: #FFFFFF;'>✓ Relevant skills matched to job targets</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="section">', unsafe_allow_html=True)
            st.subheader("Common Resume Weaknesses")
            st.markdown("<p style='color: #FFFFFF;'>△ Generic objective statements</p>", unsafe_allow_html=True)
            st.markdown("<p style='color: #FFFFFF;'>△ Missing keywords from job descriptions</p>", unsafe_allow_html=True)
            st.markdown("<p style='color: #FFFFFF;'>△ Focusing on duties instead of accomplishments</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Add footer
    st.markdown('<div class="footer">Resume Reviewer & Career Coach — Powered by Llama 4 Maverick via Groq API</div>', unsafe_allow_html=True)
    
    # Close the main-content div
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()