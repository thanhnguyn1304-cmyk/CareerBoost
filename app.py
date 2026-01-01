import streamlit as st
import os
import json
from pypdf import PdfReader
from openai import OpenAI

# Page Configuration
st.set_page_config(
    page_title="CareerBoost",
    page_icon="🚀",
    layout="wide"
)

# --- Logic Engine ---

def extract_text_from_pdf(uploaded_file):
    """Extracts text from a PDF file using pypdf."""
    try:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

def analyze_resume(cv_text, jd_text, api_key):
    """Calls OpenAI API to analyze the CV against the JD."""
    if not api_key:
        st.error("Please provide an OpenAI API Key.")
        return None
    
    client = OpenAI(api_key=api_key)
    
    system_prompt = """
    You are an expert Career Coach and Resume Optimization Specialist.
    Your task is to analyze a candidate's Resume (CV) against a Job Description (JD).
    You must identify gaps in hard and soft skills, calculate a match score, and provide actionable advice.
    
    You must respond in strictly valid JSON format with the following structure:
    {
        "match_score": integer (0-100),
        "missing_hard_skills": ["skill1", "skill2"],
        "missing_soft_skills": ["skill1", "skill2"],
        "recommended_courses": ["Course Name 1", "Course Name 2"],
        "rewritten_bullet_points": [
            {
                "original": "Original bullet from CV",
                "optimized": "Rewritten bullet including keywords from JD"
            },
            {
                "original": "Original bullet from CV",
                "optimized": "Rewritten bullet including keywords from JD"
            }
        ]
    }
    Provide 3 rewritten bullet point examples.
    For recommended_courses, suggest generic or specific titles like 'Udemy: [Topic]' or 'Coursera: [Topic]' for the missing hard skills.
    """
    
    user_prompt = f"RESUME:\n{cv_text}\n\nJOB DESCRIPTION:\n{jd_text}"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Or gpt-3.5-turbo if preferred
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
        
    except Exception as e:
        st.error(f"Error calling OpenAI API: {e}")
        return None

# --- UI/UX ---

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key to enable the logic engine.")
    
    st.divider()
    
    uploaded_file = st.file_uploader("Upload your CV (PDF)", type=["pdf"])
    jd_input = st.text_area("Paste Job Description (JD)", height=200, placeholder="Paste the full job description here...")
    
    analyze_btn = st.button("🚀 Boost My Career", type="primary", use_container_width=True)

# Main Content
st.title("🚀 CareerBoost")
st.subheader("The Lost Student Solution")
st.markdown("---")

if analyze_btn:
    if not uploaded_file or not jd_input or not api_key:
        st.warning("Please fill in all fields (API Key, PDF, and Job Description) to proceed.")
    else:
        with st.spinner("Analyzing your profile... (This may take a few seconds)"):
            # 1. Extract Text
            cv_text = extract_text_from_pdf(uploaded_file)
            
            if cv_text:
                # 2. Analyze with AI
                result = analyze_resume(cv_text, jd_input, api_key)
                
                if result:
                    # Layout
                    col1, col2 = st.columns([1, 2])
                    
                    # Section 1: The Hook (Score)
                    with col1:
                        st.markdown("### Match Score")
                        score = result.get('match_score', 0)
                        st.metric(label="ATS Compatibility", value=f"{score}%")
                        st.progress(score / 100)
                        
                        # Hackathon Hidden Revenue Stream: Course Recommendation
                        if score < 70:
                            st.divider()
                            st.markdown("#### 🎓 Boost Your Score")
                            st.warning("Your score is below 70%. We recommend this course to bridge the gap:")
                            courses = result.get('recommended_courses', [])
                            if courses:
                                st.info(f"👉 **{courses[0]}**")
                                st.markdown("[Click here to enroll (Mock Link)](https://www.udemy.com)")
                            
                    # Section 2: Gap Analysis
                    with col2:
                        st.markdown("### 🧩 Skill Gap Analysis")
                        
                        st.markdown("**Missing Hard Skills:**")
                        hard_skills = result.get('missing_hard_skills', [])
                        if hard_skills:
                            for skill in hard_skills:
                                st.markdown(f"<span style='background-color: #ffcccb; padding: 5px 10px; border-radius: 15px; margin-right: 5px; color: #8b0000;'>{skill}</span>", unsafe_allow_html=True)
                        else:
                            st.success("No missing hard skills detected!")
                            
                        st.markdown("") # Spacer
                        
                        st.markdown("**Missing Soft Skills:**")
                        soft_skills = result.get('missing_soft_skills', [])
                        if soft_skills:
                            for skill in soft_skills:
                                st.markdown(f"<span style='background-color: #e0f7fa; padding: 5px 10px; border-radius: 15px; margin-right: 5px; color: #006064;'>{skill}</span>", unsafe_allow_html=True)
                        else:
                            st.success("Your soft skills look great!")

                    st.markdown("---")
                    
                    # Section 3: The Solution (Rewrites)
                    st.markdown("### ✍️ Optimized Bullet Points")
                    st.caption("Here is how you can rewrite your experience to better match the job:")
                    
                    rewrites = result.get('rewritten_bullet_points', [])
                    for i, item in enumerate(rewrites):
                        with st.container():
                            c_left, c_right = st.columns(2)
                            with c_left:
                                st.error(f"**Before:**\n\n{item.get('original', '')}")
                            with c_right:
                                st.success(f"**After:**\n\n{item.get('optimized', '')}")
                        st.divider()
                    
                    st.success("Analysis Complete! Good luck with your application.")

else:
    # Landing State
    st.info("👈 Please configure the sidebar to start your Career Boost.")
    st.markdown("""
    **How it works:**
    1. Enter your OpenAI API Key.
    2. Upload your existing Resume (PDF).
    3. Paste a Job Description you want to apply for.
    4. Click **Boost My Career** to see the magic!
    """)
