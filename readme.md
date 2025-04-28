# Resume Reviewer & Career Coach

A powerful, AI-powered Streamlit application that analyzes resumes, provides professional feedback, and recommends suitable job opportunities.


## Features

- **Resume Parsing**: Extracts key information from PDF, DOCX, and TXT resume files
- **Intelligent Analysis**: Uses Meta's Llama 4 Maverick model via Groq API to provide professional feedback
- **Job Recommendations**: Suggests suitable job roles based on the resume profile
- **Dark Theme UI**: Clean, professional dark theme with excellent text visibility
- **Error Resilience**: Handles API issues gracefully with smart retries and fallbacks

## Requirements

- Python 3.7+
- Streamlit
- PyPDF2
- docx2txt
- pandas
- requests
- python-dotenv

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/resume-reviewer.git
cd resume-reviewer
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your Groq API key (see below)

## Groq API Key Setup

This application uses the Groq API with Meta's Llama 4 Maverick model for resume analysis. You need to obtain a Groq API key:

1. Create an account at [console.groq.com](https://console.groq.com/)
2. Generate an API key from your dashboard
3. Create a `.env` file in the project root directory
4. Add your API key to the `.env` file:
```
GROQ_API_KEY=your_api_key_here
```

**Important**: Never commit your `.env` file to version control!

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Open your browser and navigate to the URL displayed in the terminal (typically http://localhost:8501)

3. Upload your resume (PDF, DOCX, or TXT format) using the file uploader

4. Review the extracted information, analysis, and job recommendations in the respective tabs

## Handling API Errors

The application includes robust error handling for common API issues:

- **Authentication Errors (401)**: Check that your API key is correct in the `.env` file
- **Service Unavailable (503)**: The app will automatically retry up to 3 times. If the issue persists, the Groq API may be experiencing high load or maintenance - try again later
- **Timeout Errors**: If the API takes too long to respond, the app will retry the request

You can check the Groq API status at [status.groq.com](https://status.groq.com/) if you encounter persistent issues.

## Deploying to Streamlit Cloud

1. Push your code to a GitHub repository

2. Log in to [Streamlit Cloud](https://streamlit.io/cloud)

3. Create a new app and connect it to your GitHub repository

4. Add your Groq API key to the Streamlit Cloud secrets management:
   - Go to your app settings
   - Navigate to the "Secrets" section
   - Add your API key in the following format:
     ```
     GROQ_API_KEY=your_api_key_here
     ```

5. Deploy the application

## How The Analysis Works

1. **Resume Parsing**: The app uses regex patterns to extract key information like contact details, education, experience, skills, and summary
2. **AI Analysis**: The extracted data is sent to the Llama 4 Maverick model via Groq's API 
3. **JSON Response**: The model returns a structured JSON response with strengths, weaknesses, improvements, and job suggestions
4. **Fallback Mechanisms**: If JSON parsing fails, the app uses regex extraction as a fallback to still provide useful information

## Customization

You can modify the code to customize various aspects:

- **UI Theme**: Adjust the CSS styles in the main script
- **Parsing Logic**: Enhance the regex patterns in the `parse_resume` function
- **Analysis Prompt**: Modify the prompt in the `analyze_resume` function
- **Error Handling**: Adjust retry attempts and timeouts in the API call logic

## License

[MIT License](LICENSE)

## Acknowledgements

- [Streamlit](https://streamlit.io/) for the web app framework
- [Meta](https://ai.meta.com/) for the Llama 4 Maverick model
- [Groq](https://groq.com/) for the fast inference API
