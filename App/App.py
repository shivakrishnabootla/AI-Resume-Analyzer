# Developed by ShivaKrishna    Made with Streamlit


###### Packages Used ######
import streamlit as st # core package used in this project
import pandas as pd
import base64, random
import time,datetime
import pymysql
import os
import socket
import platform
import geocoder
import secrets
import io,random
import plotly.express as px # to create visualisations at the admin session
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
# libraries used to parse the pdf files
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
from streamlit_tags import st_tags
from PIL import Image
# pre stored data for prediction purposes
from Courses import ds_course,web_course,android_course,ios_course,uiux_course,resume_videos,interview_videos
import nltk
nltk.download('stopwords')


###### Preprocessing functions ######


# Generates a link allowing the data in a given panda dataframe to be downloaded in csv format 
def get_csv_download_link(df,filename,text):
    csv = df.to_csv(index=False)
    ## bytes conversions
    b64 = base64.b64encode(csv.encode()).decode()      
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


# Reads Pdf file and check_extractable
def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    ## close open handles
    converter.close()
    fake_file_handle.close()
    return text


# show uploaded file path to view pdf_display
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


# course recommendations which has data already loaded from Courses.py
def course_recommender(course_list):
    st.subheader("**Courses & Certificates Recommendations 👨‍🎓**")
    c = 0
    rec_course = []
    ## slider to choose from range 1-10
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course


###### Database Stuffs ######


# sql connector - with error handling
connection = None
cursor = None
try:
    # First connect without database to create it if needed
    temp_connection = pymysql.connect(host='localhost', user='root', password='123456')
    temp_cursor = temp_connection.cursor()
    temp_cursor.execute("CREATE DATABASE IF NOT EXISTS cv")
    temp_cursor.close()
    temp_connection.close()
    
    # Now connect with the database
    connection = pymysql.connect(host='localhost', user='root', password='123456', db='cv')
    cursor = connection.cursor()
except Exception as e:
    # Connection will be None if error occurs - will be handled in run() function
    pass


# inserting miscellaneous data, fetched results, prediction and recommendation into user_data table
def insert_data(sec_token,ip_add,host_name,dev_user,os_name_ver,latlong,city,state,country,act_name,act_mail,act_mob,name,email,res_score,timestamp,no_of_pages,reco_field,cand_level,skills,recommended_skills,courses,pdf_name):
    DB_table_name = 'user_data'
    insert_sql = "insert into " + DB_table_name + """
    values (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (str(sec_token),str(ip_add),host_name,dev_user,os_name_ver,str(latlong),city,state,country,act_name,act_mail,act_mob,name,email,str(res_score),timestamp,str(no_of_pages),reco_field,cand_level,skills,recommended_skills,courses,pdf_name)
    cursor.execute(insert_sql, rec_values)
    connection.commit()


# inserting feedback data into user_feedback table
def insertf_data(feed_name,feed_email,feed_score,comments,Timestamp):
    DBf_table_name = 'user_feedback'
    insertfeed_sql = "insert into " + DBf_table_name + """
    values (0,%s,%s,%s,%s,%s)"""
    rec_values = (feed_name, feed_email, feed_score, comments, Timestamp)
    cursor.execute(insertfeed_sql, rec_values)
    connection.commit()


###### Setting Page Configuration (favicon, Logo, Title) ######


st.set_page_config(
   page_title="AI Resume Analyzer",
   page_icon='./Logo/recommend.png',
   layout="wide",
   initial_sidebar_state="expanded"
)


###### Main function run() ######


def run():
    
    # Add Professional Black Background with Overlay
    def add_bg_from_local(image_file):
        # Create a sleek black gradient background instead of using image
        st.markdown(
            f"""
            <style>
            .stApp {{
                background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0f0f0f 100%);
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
                background-repeat: no-repeat;
            }}
            
            /* Professional overlay for better text readability */
            .stApp::before {{
                content: '';
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.3);
                z-index: -1;
            }}
            
            /* Enhanced container styling - Dark theme */
            .stMainBlockContainer {{
                background: rgba(30, 30, 30, 0.95);
                border-radius: 10px;
                padding: 20px;
                margin: 10px;
                box-shadow: 0 8px 32px rgba(255, 255, 255, 0.05);
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    
    # Call this function with your JPG file path
    # NOTE: Disabled per user request — using CSS gradient (black theme) instead of JPG background
    # add_bg_from_local('background.jpg')
    
    # Professional Black-themed CSS with Cloud Animation
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Professional Black Color Palette - Enhanced Visibility */
    :root {
        --primary-gold: #ffd700;
        --primary-blue: #0969da;
        --primary-gold-hover: #ffed4e;
        --accent-silver: #e8e8e8;
        --dark-black: #0a0a0a;
        --light-gray: #f5f5f5;
        --text-light: #ffffff;
        --text-gold: #ffd700;
        --text-silver: #e8e8e8;
        --text-bright: #ffffff;
        --text-highlight: #ffd700;
        --border: #333333;
        --bg-dark: #1a1a1a;
        --bg-darker: #0f0f0f;
        --shadow: 0 1px 3px rgba(0, 0, 0, 0.5), 0 1px 2px rgba(255, 215, 0, 0.1);
        --shadow-hover: 0 3px 12px rgba(255, 215, 0, 0.2), 0 2px 4px rgba(255, 215, 0, 0.15);
    }

    /* Force most text to white for legibility on dark theme */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    .stApp p, .stApp span, .stApp label, .stApp div, .stApp li, .stApp a,
    .stApp button, .stApp small, .stApp td, .stApp th {
        color: var(--text-light) !important;
    }

    /* Preserve colors inside temporary boxes marked with .github-card */
    .github-card h1, .github-card h2, .github-card h3, .github-card p, .github-card span, .github-card div {
        color: #24292f !important;
    }
    .github-card p, .github-card .subtext {
        color: #57606a !important;
    }

    /* Preserve the sidebar "Built by" / team IDs color when wrapped in .team-ids */
    [data-testid="stSidebar"] .team-ids, .team-ids, .team-ids * {
        color: var(--text-highlight) !important;
    }
    
    /* Professional Cloud Animation */
    @keyframes float-cloud {
        0% { transform: translateX(-100%); opacity: 0; }
        10% { opacity: 0.6; }
        50% { opacity: 0.8; }
        90% { opacity: 0.6; }
        100% { transform: translateX(100vw); opacity: 0; }
    }
    
    @keyframes gentle-drift {
        0%, 100% { transform: translateY(0px) translateX(0px); }
        25% { transform: translateY(-8px) translateX(10px); }
        50% { transform: translateY(-12px) translateX(0px); }
        75% { transform: translateY(-8px) translateX(-10px); }
    }
    
    @keyframes subtle-glow {
        0%, 100% { box-shadow: 0 0 15px rgba(255, 215, 0, 0.3); }
        50% { box-shadow: 0 0 25px rgba(255, 215, 0, 0.5); }
    }
    
    /* Floating Cloud Container */
    .cloud-container {
        position: fixed;
        top: 80px;
        left: 0;
        width: 100%;
        height: 200px;
        pointer-events: none;
        z-index: 1;
    }
    
    .cloud {
        position: absolute;
        background: linear-gradient(135deg, rgba(232, 232, 232, 0.15) 0%, rgba(200, 200, 200, 0.1) 100%);
        border-radius: 100px;
        filter: blur(2px) drop-shadow(0 4px 8px rgba(255, 215, 0, 0.1));
        animation: float-cloud linear infinite, gentle-drift 6s ease-in-out infinite;
    }
    
    .cloud:nth-child(1) { width: 120px; height: 50px; top: 20px; animation-duration: 20s, 6s; animation-delay: 0s, 0s; }
    .cloud:nth-child(2) { width: 150px; height: 60px; top: 60px; animation-duration: 25s, 8s; animation-delay: 5s, 1s; }
    .cloud:nth-child(3) { width: 100px; height: 45px; top: 100px; animation-duration: 30s, 7s; animation-delay: 10s, 2s; }
    .cloud:nth-child(4) { width: 140px; height: 55px; top: 40px; animation-duration: 22s, 6.5s; animation-delay: 15s, 1.5s; }
    
    /* Main container - Professional Black style */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1280px;
    }
    
    /* Enhanced fade-in animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Professional Header - Black gradient with gold accent */
    .github-header {
        background: linear-gradient(135deg, #1a1a1a 0%, #000000 50%, #0f0f0f 100%);
        border: 2px solid rgba(255, 215, 0, 0.3);
        border-radius: 12px;
        padding: 3rem 2rem;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: var(--shadow-hover);
        animation: fadeIn 0.6s ease-out, subtle-glow 3s ease-in-out infinite;
    }
    
    .github-header h1 {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        color: #ffd700;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.02em;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.8);
    }
    
    .github-header p {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 1.25rem;
        font-weight: 400;
        color: #e8e8e8;
        margin: 0;
        text-shadow: 0 1px 4px rgba(0, 0, 0, 0.5);
    }
    
    /* Professional Logo Container */
    .logo-container-github {
        background: linear-gradient(135deg, #1a1a1a 0%, #262626 100%);
        border: 2px solid #ffd700;
        border-radius: 12px;
        padding: 2rem;
        margin: 2rem 0;
        text-align: center;
        box-shadow: var(--shadow);
        animation: fadeIn 0.8s ease-out;
    }
    
    /* Professional Cards - Blue themed */
    .github-card {
        background: linear-gradient(135deg, #ffffff 0%, #f6f9ff 100%);
        border: 2px solid #ddf4ff;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: var(--shadow);
        transition: all 0.3s ease;
        animation: fadeIn 0.6s ease-out;
    }
    
    .github-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #262626 100%);
        border: 2px solid #ffd700;
    }
    
    .github-card:hover {
        box-shadow: var(--shadow-hover);
        border-color: #ffed4e;
        transform: translateY(-2px);
    }
    
    .github-card h2 {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffd700 !important;
        margin: 0 0 1rem 0;
    }
    
    .github-card p {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 1rem;
        color: #e8e8e8 !important;
        line-height: 1.6;
        margin: 0;
    }
    
    /* Professional Buttons - Black themed with Gold accent */
    .stButton > button {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-weight: 600;
        font-size: 0.875rem;
        background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
        color: #000000 !important;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(255, 215, 0, 0.2);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #f0c000 0%, #ffe066 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(255, 215, 0, 0.3);
    }
    
    /* Input Fields - Black themed */
    .stTextInput > div > div > input {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        border: 2px solid #ffd700;
        border-radius: 8px;
        padding: 0.5rem 0.75rem;
        font-size: 0.875rem;
        transition: all 0.2s ease;
        background-color: #1a1a1a;
        color: #ffd700 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #ffed4e;
        outline: none;
        box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.2);
    }
    
    /* Selectbox - Black themed */
    .stSelectbox > div > div > select {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        border: 2px solid #ffd700;
        border-radius: 8px;
        background-color: #1a1a1a;
        color: #ffd700 !important;
    }
    
    /* Success/Info/Error messages - Black themed */
    .stSuccess {
        background-color: #1a3a1a;
        border: 2px solid #4ade80;
        border-radius: 8px;
        color: #86efac !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        animation: slideIn 0.3s ease-out;
    }
    
    .stInfo {
        background-color: #1a2a3a;
        border: 2px solid #ffd700;
        border-radius: 8px;
        color: #ffd700 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        animation: slideIn 0.3s ease-out;
    }
    
    .stError {
        background-color: #3a1a1a;
        border: 2px solid #ff6b6b;
        border-radius: 8px;
        color: #ffa8a8 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        animation: slideIn 0.3s ease-out;
    }
    
    /* Progress Bar - Black themed with gold */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #ffd700 0%, #ffed4e 100%);
        border-radius: 4px;
    }
    
    /* File Uploader */
    .uploadedFile {
        border: 2px solid #ffd700;
        border-radius: 8px;
        padding: 0.75rem;
        background: linear-gradient(135deg, #262626 0%, #1a1a1a 100%);
        animation: fadeIn 0.3s ease-out;
        color: #ffd700 !important;
    }
    
    /* Dataframes */
    .dataframe {
        border: 1px solid #ffd700;
        border-radius: 8px;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background-color: #1a1a1a;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Professional Typography - Black themed */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: #ffd700 !important;
        font-weight: 700;
    }
    
    p, span, div, label, li, td, th {
        color: #e8e8e8 !important;
    }
    
    /* Code blocks - Black themed */
    code {
        background: linear-gradient(135deg, #262626 0%, #1a1a1a 100%);
        border: 1px solid #ffd700;
        border-radius: 4px;
        padding: 0.125rem 0.25rem;
        font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', monospace;
        font-size: 0.875em;
        color: #ffd700 !important;
    }
    
    /* Smooth transitions */
    * {
        transition: border-color 0.2s ease, box-shadow 0.2s ease, color 0.2s ease;
    }
    
    /* Dividers - Black themed */
    hr {
        border: none;
        border-top: 2px solid #ffd700;
        margin: 1.5rem 0;
    }
    
    /* Badges - Black themed */
    .github-badge {
        display: inline-block;
        padding: 0.125rem 0.5rem;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 12px;
        background: linear-gradient(135deg, #262626 0%, #1a1a1a 100%);
        color: #ffd700 !important;
        border: 1px solid #ffd700;
    }
    
    /* Sidebar - Black Theme */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%) !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        background-color: transparent !important;
    }
    
    /* Sidebar Text */
    [data-testid="stSidebar"] .stMarkdown p {
        color: #e8e8e8 !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #ffd700 !important;
    }
    
    /* Sidebar Selectbox */
    [data-testid="stSidebar"] .stSelectbox > div > div > select {
        background-color: #1a1a1a !important;
        color: #ffd700 !important;
        border: 2px solid #ffd700 !important;
    }
    
    /* Sidebar Selectbox Label */
    [data-testid="stSidebar"] .stSelectbox label {
        color: #ffd700 !important;
    }
    
    /* Sidebar Divider */
    [data-testid="stSidebar"] hr {
        border-top: 2px solid #ffd700 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Add Cloud Animation HTML
    st.markdown("""
    <div class="cloud-container">
        <div class="cloud"></div>
        <div class="cloud"></div>
        <div class="cloud"></div>
        <div class="cloud"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # GitHub-style Professional Header
    st.markdown("""
    <div class="github-header">
        <h1>🤖 AI Resume Analyzer</h1>
        <p>Transform your resume into opportunities with AI-powered insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # GitHub-style Professional Logo with AI Brain Animation
    st.markdown('<div class="logo-container-github">', unsafe_allow_html=True)
    st.markdown(
        """
        <svg width="100%" height="200" viewBox="0 0 900 200" fill="none" xmlns="http://www.w3.org/2000/svg">
          <defs>
                                    <linearGradient id="githubGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                                        <stop offset="0%" stop-color="#0969da"/>
                                        <stop offset="50%" stop-color="#0550ae"/>
                                        <stop offset="100%" stop-color="#0969da"/>
                                    </linearGradient>
            <style>
              @keyframes drawBrain {
                to { stroke-dashoffset: 0; }
              }
              @keyframes pulseNode {
                0%, 100% { r: 5; opacity: 0.7; }
                50% { r: 8; opacity: 1; }
              }
              @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
              }
              .brain-path {
                stroke: url(#githubGrad);
                stroke-width: 3;
                fill: none;
                stroke-dasharray: 1200;
                stroke-dashoffset: 1200;
                animation: drawBrain 2s ease forwards;
              }
                            .circuit-line {
                                stroke: var(--primary-blue);
                                stroke-width: 2;
                                opacity: 0.9;
                                animation: fadeIn 1s ease forwards;
                            }
                            .node {
                                fill: var(--primary-blue);
                                animation: pulseNode 2s ease-in-out infinite;
                            }
                            .logo-text {
                                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                                font-weight: 600;
                                fill: var(--text-light);
                            }
              .logo-subtext {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                font-weight: 400;
                fill: #57606a;
              }
            </style>
          </defs>
          <!-- AI Brain Icon -->
          <g transform="translate(50, 50)">
            <!-- Brain outline -->
            <path class="brain-path" d="M80,60 C80,40 100,30 115,45 C125,25 155,28 162,50 C180,42 205,55 207,78 C230,75 250,92 248,115 C270,123 278,155 262,175 C270,195 253,215 232,210 C220,225 195,222 187,205 C170,218 145,215 138,198 C120,210 95,205 88,188 C72,192 55,180 57,162 C40,152 40,128 55,118 C50,100 58,82 72,80"/>
            <!-- Circuit connections -->
            <g class="circuit-line" style="animation-delay: 1s;">
              <line x1="140" y1="95" x2="170" y2="95"/>
              <line x1="150" y1="115" x2="180" y2="130"/>
              <line x1="120" y1="135" x2="150" y2="150"/>
            </g>
            <!-- Neural nodes -->
            <circle class="node" cx="170" cy="95" r="6" style="animation-delay: 1.2s;"/>
            <circle class="node" cx="180" cy="130" r="6" style="animation-delay: 1.4s;"/>
            <circle class="node" cx="150" cy="150" r="6" style="animation-delay: 1.6s;"/>
          </g>
          <!-- Text -->
          <text x="300" y="90" class="logo-text" font-size="32">AI Resume Analyzer</text>
          <text x="300" y="120" class="logo-subtext" font-size="16">Powered by Machine Learning • Built for AI Students</text>
          <text x="300" y="145" class="logo-subtext" font-size="14" fill="#ffffff">Analyze • Improve • Succeed</text>
        </svg>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Check database connection
    if connection is None or cursor is None:
        st.error("⚠️ Database Connection Error: Please ensure MySQL is running and credentials in App.py (line 99-106) are correct.")
        st.info("The application can still run for testing, but data will not be saved to the database.")
        st.stop()
    
    # GitHub-style Sidebar Navigation - Black Theme
    st.sidebar.markdown("""
    <div style='padding: 1rem; background: linear-gradient(135deg, #1a1a1a 0%, #262626 100%); border: 2px solid #ffd700; border-radius: 6px; 
                margin-bottom: 1.5rem; text-align: center;'>
        <h3 style='color: #ffd700; font-family: Inter, sans-serif; font-weight: 600; margin: 0; font-size: 1rem;'>
            📋 Navigation
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    activities = ["User", "Feedback", "About", "Admin"]
    choice = st.sidebar.selectbox("**Select an option:**", activities, 
                                   help="Choose a section to navigate")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style='padding: 1rem; text-align: center; font-size: 0.875rem; color: #e8e8e8;'>
        <p style='margin: 0.5rem 0; color: #e8e8e8;'>Built by</p>
        <p style='margin: 0;'><strong class='team-ids' style='color: #ffd700;'>23090-AI-<br>088<br>082<br>083<br>084<br>085<br>086<br>088<br>089<br>090</strong></p>
    </div>
    """, unsafe_allow_html=True)

    ###### Creating Database and Table ######


    # Create the DB
    db_sql = """CREATE DATABASE IF NOT EXISTS CV;"""
    cursor.execute(db_sql)


    # Create table user_data and user_feedback
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                    sec_token varchar(20) NOT NULL,
                    ip_add varchar(50) NULL,
                    host_name varchar(50) NULL,
                    dev_user varchar(50) NULL,
                    os_name_ver varchar(50) NULL,
                    latlong varchar(50) NULL,
                    city varchar(50) NULL,
                    state varchar(50) NULL,
                    country varchar(50) NULL,
                    act_name varchar(50) NOT NULL,
                    act_mail varchar(50) NOT NULL,
                    act_mob varchar(20) NOT NULL,
                    Name varchar(500) NOT NULL,
                    Email_ID VARCHAR(500) NOT NULL,
                    resume_score VARCHAR(8) NOT NULL,
                    Timestamp VARCHAR(50) NOT NULL,
                    Page_no VARCHAR(5) NOT NULL,
                    Predicted_Field BLOB NOT NULL,
                    User_level BLOB NOT NULL,
                    Actual_skills BLOB NOT NULL,
                    Recommended_skills BLOB NOT NULL,
                    Recommended_courses BLOB NOT NULL,
                    pdf_name varchar(50) NOT NULL,
                    PRIMARY KEY (ID)
                    );
                """
    cursor.execute(table_sql)


    DBf_table_name = 'user_feedback'
    tablef_sql = "CREATE TABLE IF NOT EXISTS " + DBf_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                        feed_name varchar(50) NOT NULL,
                        feed_email VARCHAR(50) NOT NULL,
                        feed_score VARCHAR(5) NOT NULL,
                        comments VARCHAR(100) NULL,
                        Timestamp VARCHAR(50) NOT NULL,
                        PRIMARY KEY (ID)
                    );
                """
    cursor.execute(tablef_sql)


    ###### CODE FOR CLIENT SIDE (USER) ######

    if choice == 'User':
        
        # GitHub-style Welcome Card
        st.markdown("""
        <div class="github-card" style='text-align: center; padding: 2.5rem;'>
            <h2 style='color: #ffffff; margin-bottom: 1rem; font-size: 1.75rem; font-weight: 600;'>
                ✨ Welcome to AI Resume Analyzer
            </h2>
            <p style='color: #ffffff; font-size: 1rem; line-height: 1.6; margin: 0;'>
                Get instant feedback on your resume with AI-powered analysis. 
                We'll help you identify strengths, suggest improvements, and recommend skills to boost your career!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # GitHub-style Personal Information Section
        st.markdown("### 👤 Personal Information")
        st.markdown('<hr style="margin: 1.5rem 0; border-color: #d0d7de;">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            act_name = st.text_input('**Name** *', placeholder="Enter your full name", help="Your name as it appears on your resume")
        with col2:
            act_mail = st.text_input('**Email** *', placeholder="your.email@example.com", help="Your email address")
        
        act_mob = st.text_input('**Mobile Number** *', placeholder="+1234567890", help="Your contact number")
        
        sec_token = secrets.token_urlsafe(12)
        host_name = socket.gethostname()
        ip_add = socket.gethostbyname(host_name)
        dev_user = os.getlogin()
        os_name_ver = platform.system() + " " + platform.release()
        
        try:
            g = geocoder.ip('me')
            latlong = g.latlng
            geolocator = Nominatim(user_agent="http")
            location = geolocator.reverse(latlong, language='en')
            address = location.raw['address']
            cityy = address.get('city', '')
            statee = address.get('state', '')
            countryy = address.get('country', '')  
            city = cityy
            state = statee
            country = countryy
        except:
            city = state = country = "Unknown"

        # GitHub-style Resume Upload Section
        st.markdown('<hr style="margin: 1.5rem 0; border-color: #d0d7de;">', unsafe_allow_html=True)
        st.markdown("""
        <div class="github-card" style='margin: 2rem 0; padding: 2rem; border-left: 3px solid #ffffff;'>
            <h3 style='color: #ffffff; margin-bottom: 0.75rem; font-size: 1.25rem; font-weight: 600;'>
                📄 Upload Your Resume
            </h3>
            <p style='color: #57606a; font-size: 0.9375rem; line-height: 1.6; margin: 0;'>
                Upload your resume in PDF format and get instant AI-powered analysis, 
                skill recommendations, and career insights!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        ## file upload in pdf format
        pdf_file = st.file_uploader("**Choose your Resume (PDF format)**", type=["pdf"], help="Upload your resume in PDF format")
        if pdf_file is not None:
            st.success("✅ Resume uploaded successfully!")
            with st.spinner('🤖 AI is analyzing your resume... Please wait while we process your document...'):
                time.sleep(4)
        
            ### saving the uploaded resume to folder
            save_image_path = './Uploaded_Resumes/'+pdf_file.name
            pdf_name = pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)

            ### parsing and extracting whole resume 
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                
                ## Get the whole resume data into resume_text
                resume_text = pdf_reader(save_image_path)

                ## GitHub-style Analysis Results
                st.markdown('<hr style="margin: 2rem 0; border-color: #d0d7de;">', unsafe_allow_html=True)
                st.markdown("""
                <div class="github-card" style='background: linear-gradient(135deg, #1a1a1a 0%, #262626 100%); color: white; padding: 2rem; text-align: center; border: none;'>
                    <h1 style='color: white; margin-bottom: 0.5rem; font-size: 1.75rem; font-weight: 600;'>
                        📊 Resume Analysis Complete!
                    </h1>
                    <p style='font-size: 1rem; color: rgba(255,255,255,0.9); margin: 0;'>
                        Your resume has been successfully analyzed
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                st.success("👋 Hello "+ resume_data['name'] + "! Welcome to your resume analysis.")
                st.markdown("### 👤 Your Basic Information")
                st.markdown('<hr style="margin: 1.5rem 0; border-color: #d0d7de;">', unsafe_allow_html=True)
                try:
                    st.text('Name: '+resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Degree: '+str(resume_data['degree']))                    
                    st.text('Resume pages: '+str(resume_data['no_of_pages']))

                except:
                    pass
                ## Predicting Candidate Experience Level 

                ### Trying with different possibilities
                cand_level = ''
                if resume_data['no_of_pages'] < 1:                
                    cand_level = "NA"
                    st.markdown( '''<h4 style='text-align: left; color: #d73b5c;'>You are at Fresher level!</h4>''',unsafe_allow_html=True)
                
                #### if internship then intermediate level
                elif 'INTERNSHIP' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif 'INTERNSHIPS' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif 'Internship' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif 'Internships' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                
                #### if Work Experience/Experience then Experience level
                elif 'EXPERIENCE' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                elif 'WORK EXPERIENCE' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                elif 'Experience' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                elif 'Work Experience' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                else:
                    cand_level = "Fresher"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at Fresher level!!''',unsafe_allow_html=True)


                ## GitHub-style Skills Recommendation
                st.markdown('<hr style="margin: 2rem 0; border-color: #d0d7de;">', unsafe_allow_html=True)
                st.markdown("""
                <div class="github-card" style='background: linear-gradient(135deg, #1a1a1a 0%, #262626 100%); color: white; padding: 1.5rem; text-align: center; border: none;'>
                    <h2 style='color: white; margin: 0; font-size: 1.5rem; font-weight: 600;'>💡 Skills Recommendation</h2>
                </div>
                """, unsafe_allow_html=True)
                
                ### Current Analyzed Skills
                st.markdown("#### 🎯 Your Current Skills")
                keywords = st_tags(label='**Your Skills**',
                text='These are the skills extracted from your resume',value=resume_data['skills'],key = '1  ')

                ### Keywords for Recommendations
                ds_keyword = ['tensorflow','keras','pytorch','machine learning','deep Learning','flask','streamlit']
                web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress','javascript', 'angular js', 'C#', 'Asp.net', 'flask']
                android_keyword = ['android','android development','flutter','kotlin','xml','kivy']
                ios_keyword = ['ios','ios development','swift','cocoa','cocoa touch','xcode']
                uiux_keyword = ['ux','adobe xd','figma','zeplin','balsamiq','ui','prototyping','wireframes','storyframes','adobe photoshop','photoshop','editing','adobe illustrator','illustrator','adobe after effects','after effects','adobe premier pro','premier pro','adobe indesign','indesign','wireframe','solid','grasp','user research','user experience']
                n_any = ['english','communication','writing', 'microsoft office', 'leadership','customer management', 'social media']
                ### Skill Recommendations Starts                
                recommended_skills = []
                reco_field = ''
                rec_course = ''

                ### condition starts to check skills from keywords and predict field
                for i in resume_data['skills']:
                
                    #### Data science recommendation
                    if i.lower() in ds_keyword:
                        print(i.lower())
                        reco_field = 'Data Science'
                        st.success("** Our analysis says you are looking for Data Science Jobs.**")
                        recommended_skills = ['Data Visualization','Predictive Analysis','Statistical Modeling','Data Mining','Clustering & Classification','Data Analytics','Quantitative Analysis','Web Scraping','ML Algorithms','Keras','Pytorch','Probability','Scikit-learn','Tensorflow',"Flask",'Streamlit']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '2')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(ds_course)
                        break

                    #### Web development recommendation
                    elif i.lower() in web_keyword:
                        print(i.lower())
                        reco_field = 'Web Development'
                        st.success("** Our analysis says you are looking for Web Development Jobs **")
                        recommended_skills = ['React','Django','Node JS','React JS','php','laravel','Magento','wordpress','Javascript','Angular JS','c#','Flask','SDK']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '3')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(web_course)
                        break

                    #### Android App Development
                    elif i.lower() in android_keyword:
                        print(i.lower())
                        reco_field = 'Android Development'
                        st.success("** Our analysis says you are looking for Android App Development Jobs **")
                        recommended_skills = ['Android','Android development','Flutter','Kotlin','XML','Java','Kivy','GIT','SDK','SQLite']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '4')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(android_course)
                        break

                    #### IOS App Development
                    elif i.lower() in ios_keyword:
                        print(i.lower())
                        reco_field = 'IOS Development'
                        st.success("** Our analysis says you are looking for IOS App Development Jobs **")
                        recommended_skills = ['IOS','IOS Development','Swift','Cocoa','Cocoa Touch','Xcode','Objective-C','SQLite','Plist','StoreKit',"UI-Kit",'AV Foundation','Auto-Layout']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '5')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(ios_course)
                        break

                    #### Ui-UX Recommendation
                    elif i.lower() in uiux_keyword:
                        print(i.lower())
                        reco_field = 'UI-UX Development'
                        st.success("** Our analysis says you are looking for UI-UX Development Jobs **")
                        recommended_skills = ['UI','User Experience','Adobe XD','Figma','Zeplin','Balsamiq','Prototyping','Wireframes','Storyframes','Adobe Photoshop','Editing','Illustrator','After Effects','Premier Pro','Indesign','Wireframe','Solid','Grasp','User Research']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '6')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(uiux_course)
                        break

                    #### For Not Any Recommendations
                    elif i.lower() in n_any:
                        print(i.lower())
                        reco_field = 'NA'
                        st.warning("** Currently our tool only predicts and recommends for Data Science, Web, Android, IOS and UI/UX Development**")
                        recommended_skills = ['No Recommendations']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Currently No Recommendations',value=recommended_skills,key = '6')
                        st.markdown('''<h5 style='text-align: left; color: #092851;'>Maybe Available in Future Updates</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = "Sorry! Not Available for this Field"
                        break


                ## GitHub-style Resume Tips
                st.markdown('<hr style="margin: 2rem 0; border-color: #d0d7de;">', unsafe_allow_html=True)
                st.markdown("""
                <div class="github-card" style='background: linear-gradient(135deg, #1a1a1a 0%, #262626 100%); color: white; padding: 1.5rem; text-align: center; border: none;'>
                    <h2 style='color: white; margin: 0; font-size: 1.5rem; font-weight: 600;'>📝 Resume Tips & Ideas</h2>
                </div>
                """, unsafe_allow_html=True)
                resume_score = 0
                
                ### Predicting Whether these key points are added to the resume
                if 'Objective' or 'Summary' in resume_text:
                    resume_score = resume_score+6
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Objective/Summary</h4>''',unsafe_allow_html=True)                
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add your career objective, it will give your career intension to the Recruiters.</h4>''',unsafe_allow_html=True)

                if 'Education' or 'School' or 'College'  in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Education Details</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Education. It will give Your Qualification level to the recruiter</h4>''',unsafe_allow_html=True)

                if 'EXPERIENCE' in resume_text:
                    resume_score = resume_score + 16
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Experience</h4>''',unsafe_allow_html=True)
                elif 'Experience' in resume_text:
                    resume_score = resume_score + 16
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Experience</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Experience. It will help you to stand out from crowd</h4>''',unsafe_allow_html=True)

                if 'INTERNSHIPS'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                elif 'INTERNSHIP'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                elif 'Internships'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                elif 'Internship'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Internships. It will help you to stand out from crowd</h4>''',unsafe_allow_html=True)

                if 'SKILLS'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                elif 'SKILL'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                elif 'Skills'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                elif 'Skill'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Skills. It will help you a lot</h4>''',unsafe_allow_html=True)

                if 'HOBBIES' in resume_text:
                    resume_score = resume_score + 4
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies</h4>''',unsafe_allow_html=True)
                elif 'Hobbies' in resume_text:
                    resume_score = resume_score + 4
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Hobbies. It will show your personality to the Recruiters and give the assurance that you are fit for this role or not.</h4>''',unsafe_allow_html=True)

                if 'INTERESTS'in resume_text:
                    resume_score = resume_score + 5
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Interest</h4>''',unsafe_allow_html=True)
                elif 'Interests'in resume_text:
                    resume_score = resume_score + 5
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Interest</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Interest. It will show your interest other that job.</h4>''',unsafe_allow_html=True)

                if 'ACHIEVEMENTS' in resume_text:
                    resume_score = resume_score + 13
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements </h4>''',unsafe_allow_html=True)
                elif 'Achievements' in resume_text:
                    resume_score = resume_score + 13
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements </h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Achievements. It will show that you are capable for the required position.</h4>''',unsafe_allow_html=True)

                if 'CERTIFICATIONS' in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                elif 'Certifications' in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                elif 'Certification' in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Certifications. It will show that you have done some specialization for the required position.</h4>''',unsafe_allow_html=True)

                if 'PROJECTS' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                elif 'PROJECT' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                elif 'Projects' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                elif 'Project' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Projects. It will show that you have done work related the required position or not.</h4>''',unsafe_allow_html=True)

                st.markdown('<hr style="margin: 2rem 0; border-color: #d0d7de;">', unsafe_allow_html=True)
                st.markdown("""
                <div class="github-card" style='background: linear-gradient(135deg, #1a1a1a 0%, #262626 100%); color: white; padding: 1.5rem; text-align: center; border: none;'>
                    <h2 style='color: white; margin: 0; font-size: 1.5rem; font-weight: 600;'>📊 Resume Score</h2>
                </div>
                """, unsafe_allow_html=True)

                ### Score Bar
                my_bar = st.progress(0)
                score = 0
                for percent_complete in range(resume_score):
                    score +=1
                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1)

                ### GitHub-style Score Display
                st.markdown(f"""
                <div class="github-card" style='background: linear-gradient(135deg, #1a1a1a 0%, #262626 100%); color: white; padding: 2.5rem; text-align: center; border: none; margin: 2rem 0;'>
                    <h1 style='color: white; font-size: 3.5rem; margin: 0; font-weight: 700;'>{score}/100</h1>
                    <p style='font-size: 1.125rem; color: rgba(255,255,255,0.9); margin-top: 0.5rem;'>Your Resume Writing Score</p>
                </div>
                """, unsafe_allow_html=True)
                st.info("ℹ️ **Note:** This score is calculated based on the content that you have in your Resume.")

                # print(str(sec_token), str(ip_add), (host_name), (dev_user), (os_name_ver), (latlong), (city), (state), (country), (act_name), (act_mail), (act_mob), resume_data['name'], resume_data['email'], str(resume_score), timestamp, str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']), str(recommended_skills), str(rec_course), pdf_name)


                ### Getting Current Date and Time
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date+'_'+cur_time)


                ## Calling insert_data to add all the data into user_data                
                insert_data(str(sec_token), str(ip_add), (host_name), (dev_user), (os_name_ver), (latlong), (city), (state), (country), (act_name), (act_mail), (act_mob), resume_data['name'], resume_data['email'], str(resume_score), timestamp, str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']), str(recommended_skills), str(rec_course), pdf_name)

                st.markdown('<hr style="margin: 2rem 0; border-color: #d0d7de;">', unsafe_allow_html=True)
                ## GitHub-style Video Sections
                st.markdown("""
                <div class="github-card" style='padding: 1.5rem; margin: 2rem 0; border-left: 3px solid var(--primary-blue);'>
                    <h2 style='color: #24292f; margin: 0; font-size: 1.25rem; font-weight: 600;'>💡 Bonus: Resume Writing Tips Video</h2>
                </div>
                """, unsafe_allow_html=True)
                resume_vid = random.choice(resume_videos)
                st.video(resume_vid)

                st.markdown("""
                <div class="github-card" style='padding: 1.5rem; margin: 2rem 0; border-left: 3px solid var(--primary-blue);'>
                    <h2 style='color: #24292f; margin: 0; font-size: 1.25rem; font-weight: 600;'>🎤 Bonus: Interview Tips Video</h2>
                </div>
                """, unsafe_allow_html=True)
                interview_vid = random.choice(interview_videos)
                st.video(interview_vid)

                ## On Successful Result 
                st.balloons()

            else:
                st.error('Something went wrong..')                


    ###### CODE FOR FEEDBACK SIDE ######
    elif choice == 'Feedback':   
        
        st.markdown("""
        <div class="github-card" style='background: linear-gradient(135deg, #1a1a1a 0%, #262626 100%); color: white; padding: 2rem; text-align: center; border: none; margin: 2rem 0;'>
            <h1 style='color: white; margin-bottom: 0.5rem; font-size: 2rem; font-weight: 600;'>💬 Feedback</h1>
            <p style='font-size: 1rem; color: rgba(255,255,255,0.9); margin: 0;'>Your feedback helps us improve!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # timestamp 
        ts = time.time()
        cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        timestamp = str(cur_date+'_'+cur_time)

        # Feedback Form
        st.markdown("### 📝 Share Your Feedback")
        st.markdown("---")
        with st.form("my_form"):
            col1, col2 = st.columns(2)
            with col1:
                feed_name = st.text_input('**Name**', placeholder="Enter your name")
            with col2:
                feed_email = st.text_input('**Email**', placeholder="your.email@example.com")
            
            feed_score = st.slider('**Rate Us From 1 - 5** ⭐', 1, 5, 5, help="Rate your experience with our tool")
            comments = st.text_area('**Comments**', placeholder="Share your thoughts and suggestions...", height=100)
            Timestamp = timestamp        
            submitted = st.form_submit_button("**Submit Feedback** ✉️")
            if submitted:
                ## Calling insertf_data to add dat into user feedback
                insertf_data(feed_name,feed_email,feed_score,comments,Timestamp)    
                ## Success Message 
                st.success("✅ Thanks! Your Feedback was recorded.") 
                ## On Successful Submit
                st.balloons()    


        # query to fetch data from user feedback table
        query = 'select * from user_feedback'        
        plotfeed_data = pd.read_sql(query, connection)                        


        # fetching feed_score from the query and getting the unique values and total value count 
        labels = plotfeed_data.feed_score.unique()
        values = plotfeed_data.feed_score.value_counts()


        # GitHub-style Charts
        st.markdown('<hr style="margin: 2rem 0; border-color: #d0d7de;">', unsafe_allow_html=True)
        st.markdown("""
        <div class="github-card" style='padding: 1.5rem; margin: 2rem 0;'>
            <h2 style='color: #24292f; margin: 0 0 1rem 0; font-size: 1.5rem; font-weight: 600;'>📊 Past User Ratings</h2>
        </div>
        """, unsafe_allow_html=True)
        fig = px.pie(values=values, names=labels, title="Chart of User Rating Score From 1 - 5", 
                 color_discrete_sequence=['#0969da', '#0550ae', '#033d8b', '#022561', '#01163d'])
        st.plotly_chart(fig)


        #  Fetching Comment History
        cursor.execute('select feed_name, comments from user_feedback')
        plfeed_cmt_data = cursor.fetchall()

        st.markdown('<hr style="margin: 2rem 0; border-color: #d0d7de;">', unsafe_allow_html=True)
        st.markdown("""
        <div class="github-card" style='padding: 1.5rem; margin: 2rem 0;'>
            <h2 style='color: #24292f; margin: 0 0 1rem 0; font-size: 1.5rem; font-weight: 600;'>💬 User Comments</h2>
        </div>
        """, unsafe_allow_html=True)
        dff = pd.DataFrame(plfeed_cmt_data, columns=['User', 'Comment'])
        st.dataframe(dff, width=1000)

    
    ###### CODE FOR ABOUT PAGE ######
    elif choice == 'About':   
        
        st.markdown("""
        <div class="github-card" style='background: linear-gradient(135deg, #1a1a1a 0%, #262626 100%); color: white; padding: 2rem; text-align: center; border: none; margin: 2rem 0;'>
            <h1 style='color: white; margin-bottom: 0.5rem; font-size: 2rem; font-weight: 600;'>ℹ️ About The Tool</h1>
            <p style='font-size: 1rem; color: rgba(255,255,255,0.9); margin: 0;'>AI RESUME ANALYZER</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<hr style="margin: 2rem 0; border-color: #d0d7de;">', unsafe_allow_html=True)

        st.markdown("""
        <div class="github-card" style='padding: 2rem; margin: 2rem 0;'>
            <h3 style='color: #24292f; margin-bottom: 1rem; font-size: 1.25rem; font-weight: 600;'>📋 What is AI Resume Analyzer?</h3>
            <p style='color: #57606a; font-size: 1rem; line-height: 1.6; text-align: justify; margin: 0;'>
                A powerful tool which parses information from a resume using natural language processing and finds the keywords, 
                clusters them onto sectors based on their keywords. And lastly shows recommendations, predictions, and analytics 
                to the applicant based on keyword matching.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="github-card" style='padding: 2rem; margin: 2rem 0;'>
            <h3 style='color: #24292f; margin-bottom: 1rem; font-size: 1.25rem; font-weight: 600;'>🚀 How to Use It</h3>
            <p style='color: #57606a; font-size: 1rem; line-height: 1.6; text-align: justify; margin: 0;'>
                <strong style='color: var(--primary-blue);'>👤 User -</strong> <br/>
                In the Side Bar choose yourself as user and fill the required fields and upload your resume in pdf format.<br/>
                Just sit back and relax our tool will do the magic on it's own.<br/><br/>
                <strong style='color: var(--primary-blue);'>💬 Feedback -</strong> <br/>
                A place where user can suggest some feedback about the tool.<br/><br/>
                <strong style='color: var(--primary-blue);'>🔐 Admin -</strong> <br/>
                For login use <strong>see passs file</strong> as username and <strong>see passs file</strong> as password.<br/>
                It will load all the required stuffs and perform analysis.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="github-card" style='text-align: center; padding: 2rem; margin: 2rem 0; background: #f6f8fa;'>
            <p style='font-size: 1rem; color: #57606a; margin: 0;'>
                Built with ❤️ by 
                <strong style='color: var(--primary-blue);'>ShivaKrishna</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)  


    ###### CODE FOR ADMIN SIDE (ADMIN) ######
    else:
        st.success('Welcome to Admin Side')

        #  Admin Login
        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')

        if st.button('Login'):
            
            ## Credentials 
            if ad_user == 'admin' and ad_password == 'admin@resume-analyzer':
                
                ### Fetch miscellaneous data from user_data(table) and convert it into dataframe
                cursor.execute('''SELECT ID, ip_add, resume_score, convert(Predicted_Field using utf8), convert(User_level using utf8), city, state, country from user_data''')
                datanalys = cursor.fetchall()
                plot_data = pd.DataFrame(datanalys, columns=['Idt', 'IP_add', 'resume_score', 'Predicted_Field', 'User_Level', 'City', 'State', 'Country'])
                
                ### Total Users Count with a Welcome Message
                values = plot_data.Idt.count()
                st.success("Welcome ShivaKrishna ! Total %d " % values + " User's Have Used Our Tool : )")                
                
                ### Fetch user data from user_data(table) and convert it into dataframe
                cursor.execute('''SELECT ID, sec_token, ip_add, act_name, act_mail, act_mob, convert(Predicted_Field using utf8), Timestamp, Name, Email_ID, resume_score, Page_no, pdf_name, convert(User_level using utf8), convert(Actual_skills using utf8), convert(Recommended_skills using utf8), convert(Recommended_courses using utf8), city, state, country, latlong, os_name_ver, host_name, dev_user from user_data''')
                data = cursor.fetchall()                

                st.header("**User's Data**")
                df = pd.DataFrame(data, columns=['ID', 'Token', 'IP Address', 'Name', 'Mail', 'Mobile Number', 'Predicted Field', 'Timestamp',
                                                 'Predicted Name', 'Predicted Mail', 'Resume Score', 'Total Page',  'File Name',   
                                                 'User Level', 'Actual Skills', 'Recommended Skills', 'Recommended Course',
                                                 'City', 'State', 'Country', 'Lat Long', 'Server OS', 'Server Name', 'Server User',])
                
                ### Viewing the dataframe
                st.dataframe(df)
                
                ### Downloading Report of user_data in csv file
                st.markdown(get_csv_download_link(df,'User_Data.csv','Download Report'), unsafe_allow_html=True)

                ### Fetch feedback data from user_feedback(table) and convert it into dataframe
                cursor.execute('''SELECT * from user_feedback''')
                data = cursor.fetchall()

                st.header("**User's Feedback Data**")
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Feedback Score', 'Comments', 'Timestamp'])
                st.dataframe(df)

                ### query to fetch data from user_feedback(table)
                query = 'select * from user_feedback'
                plotfeed_data = pd.read_sql(query, connection)                        

                ### Analyzing All the Data's in pie charts

                # fetching feed_score from the query and getting the unique values and total value count 
                labels = plotfeed_data.feed_score.unique()
                values = plotfeed_data.feed_score.value_counts()
                
                # Pie chart for user ratings
                st.subheader("**User Rating's**")
                fig = px.pie(values=values, names=labels, title="Chart of User Rating Score From 1 - 5 🤗", color_discrete_sequence=px.colors.sequential.Aggrnyl)
                st.plotly_chart(fig)

                # fetching Predicted_Field from the query and getting the unique values and total value count                 
                labels = plot_data.Predicted_Field.unique()
                values = plot_data.Predicted_Field.value_counts()

                # Pie chart for predicted field recommendations
                st.subheader("**Pie-Chart for Predicted Field Recommendation**")
                fig = px.pie(df, values=values, names=labels, title='Predicted Field according to the Skills 👽', color_discrete_sequence=px.colors.sequential.Aggrnyl_r)
                st.plotly_chart(fig)

                # fetching User_Level from the query and getting the unique values and total value count                 
                labels = plot_data.User_Level.unique()
                values = plot_data.User_Level.value_counts()

                # Pie chart for User's👨‍💻 Experienced Level
                st.subheader("**Pie-Chart for User's Experienced Level**")
                fig = px.pie(df, values=values, names=labels, title="Pie-Chart 📈 for User's 👨‍💻 Experienced Level", color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig)

                # fetching resume_score from the query and getting the unique values and total value count                 
                labels = plot_data.resume_score.unique()                
                values = plot_data.resume_score.value_counts()

                # Pie chart for Resume Score
                st.subheader("**Pie-Chart for Resume Score**")
                fig = px.pie(df, values=values, names=labels, title='From 1 to 100 💯', color_discrete_sequence=px.colors.sequential.Agsunset)
                st.plotly_chart(fig)

                # fetching IP_add from the query and getting the unique values and total value count 
                labels = plot_data.IP_add.unique()
                values = plot_data.IP_add.value_counts()

                # Pie chart for Users
                st.subheader("**Pie-Chart for Users App Used Count**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based On IP Address 👥', color_discrete_sequence=px.colors.sequential.matter_r)
                st.plotly_chart(fig)

                # fetching City from the query and getting the unique values and total value count 
                labels = plot_data.City.unique()
                values = plot_data.City.value_counts()

                # Pie chart for City
                st.subheader("**Pie-Chart for City**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based On City 🌆', color_discrete_sequence=px.colors.sequential.Jet)
                st.plotly_chart(fig)

                # fetching State from the query and getting the unique values and total value count 
                labels = plot_data.State.unique()
                values = plot_data.State.value_counts()

                # Pie chart for State
                st.subheader("**Pie-Chart for State**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based on State 🚉', color_discrete_sequence=px.colors.sequential.PuBu_r)
                st.plotly_chart(fig)

                # fetching Country from the query and getting the unique values and total value count 
                labels = plot_data.Country.unique()
                values = plot_data.Country.value_counts()

                # Pie chart for Country
                st.subheader("**Pie-Chart for Country**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based on Country 🌏', color_discrete_sequence=px.colors.sequential.Purpor_r)
                st.plotly_chart(fig)

            ## For Wrong Credentials
            else:
                st.error("Wrong ID & Password Provided")

# Calling the main (run()) function to make the whole process run
run()
