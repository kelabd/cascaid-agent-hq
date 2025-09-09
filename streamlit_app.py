"""
Cascaid Agent HQ - Streamlit Web App
Streamlit-based web service for processing PDF reports
"""

import streamlit as st
import os
import json
from dotenv import load_dotenv
import time
from datetime import datetime
import logging

# Import your existing functions
from main import summarize_report

# Load environment variables
load_dotenv()

# Add detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Cascaid Agent HQ",
    page_icon="",
    layout="wide"
)

# Check if this is an API call using URL parameters
def is_api_call():
    try:
        # Check if we're in an API call context
        # This is a workaround for older Streamlit versions
        return st.session_state.get('api_call', False)
    except:
        return False

# Handle API calls
def handle_api_call():
    try:
        # Get parameters from URL or session state
        report_url = st.session_state.get('report_url')
        
        if not report_url:
            st.json({"success": False, "error": "report_url is required"})
            return
        
        # Process the report
        summary = summarize_report(
            report_url=report_url,
            cascaid_id=st.session_state.get('cascaid_id', 'UNKNOWN'),
            full_name=st.session_state.get('full_name', 'Unknown'),
            report_type=st.session_state.get('report_type', 'Unknown'),
            report_date=st.session_state.get('report_date', 'Unknown')
        )
        
        st.json({
            "success": True,
            "summary": summary,
            "metadata": {
                "cascaid_id": st.session_state.get('cascaid_id', 'UNKNOWN'),
                "full_name": st.session_state.get('full_name', 'Unknown'),
                "report_type": st.session_state.get('report_type', 'Unknown'),
                "report_date": st.session_state.get('report_date', 'Unknown')
            }
        })
        
    except Exception as e:
        st.json({"success": False, "error": str(e)})

# Check for API call parameters in the URL
def check_api_params():
    # This is a workaround - we'll use a different approach
    # Create a simple API endpoint using st.sidebar
    if st.sidebar.button("API Mode"):
        st.session_state.api_call = True
        st.session_state.report_url = st.sidebar.text_input("Report URL")
        st.session_state.cascaid_id = st.sidebar.text_input("Cascaid ID", value="UNKNOWN")
        st.session_state.full_name = st.sidebar.text_input("Full Name", value="Unknown")
        st.session_state.report_type = st.sidebar.text_input("Report Type", value="Unknown")
        st.session_state.report_date = st.sidebar.text_input("Report Date", value="Unknown")
        
        if st.sidebar.button("Process API Call"):
            handle_api_call()
            return True
    return False

# Main app logic
if not check_api_params():
    # Regular Streamlit UI
    st.title("🏥 Cascaid Agent HQ")
    st.markdown("**PDF Report Summarization System**")

    st.markdown("### Upload a PDF Report for AI Analysis")

    # Input form
    with st.form("report_form"):
        report_url = st.text_input(
            "Google Drive URL",
            placeholder="https://drive.google.com/file/d/FILE_ID/view",
            help="Paste the Google Drive URL of your PDF report"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            cascaid_id = st.text_input("Cascaid ID (optional)", value="UNKNOWN")
            full_name = st.text_input("Full Name (optional)", value="Unknown")
        
        with col2:
            report_type = st.text_input("Report Type (optional)", value="Unknown")
            report_date = st.text_input("Report Date (optional)", value="Unknown")
        
        submitted = st.form_submit_button("Process Report", type="primary")

    if submitted and report_url:
        start_time = time.time()
        with st.spinner("Processing report... This may take a few moments."):
            try:
                # Add step-by-step tracking
                st.info(f" Started processing at {datetime.now().strftime('%H:%M:%S')}")
                
                # Step 1: Extract file ID
                st.info(" Step 1: Extracting file ID from URL...")
                step1_start = time.time()
                
                from drive_fetch import file_id_from_url
                file_id = file_id_from_url(report_url)
                st.success(f"✅ File ID extracted: {file_id} (took {time.time() - step1_start:.1f}s)")
                
                # Step 2: Download PDF
                st.info("📥 Step 2: Downloading PDF from Google Drive...")
                step2_start = time.time()
                
                from drive_fetch import fetch_pdf_bytes
                pdf_bytes = fetch_pdf_bytes(file_id)
                st.success(f"✅ PDF downloaded: {len(pdf_bytes)} bytes (took {time.time() - step2_start:.1f}s)")
                
                # Step 3: Extract text
                st.info(" Step 3: Extracting text from PDF...")
                step3_start = time.time()
                
                from text_extract import pdf_bytes_to_text
                text = pdf_bytes_to_text(pdf_bytes)
                st.success(f"✅ Text extracted: {len(text)} characters (took {time.time() - step3_start:.1f}s)")
                
                # Step 4: Generate AI summary
                st.info(" Step 4: Generating AI summary...")
                step4_start = time.time()
                
                summary = summarize_report(
                    report_url=report_url,
                    cascaid_id=cascaid_id,
                    full_name=full_name,
                    report_type=report_type,
                    report_date=report_date
                )
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                st.success(f"✅ Report processed successfully in {processing_time:.1f} seconds!")
                st.markdown("### 📋 AI Summary")
                st.markdown(summary)
                
            except Exception as e:
                end_time = time.time()
                processing_time = end_time - start_time
                st.error(f"❌ Error processing report after {processing_time:.1f} seconds: {str(e)}")
                st.error("This might be due to authentication issues or a very large file.")
                
                # Show which step failed
                if 'file_id_from_url' in str(e):
                    st.error("Failed at Step 1: URL parsing")
                elif 'fetch_pdf_bytes' in str(e):
                    st.error("Failed at Step 2: Google Drive download")
                elif 'pdf_bytes_to_text' in str(e):
                    st.error("Failed at Step 3: PDF text extraction")
                else:
                    st.error("Failed at Step 4: AI processing")

    elif submitted and not report_url:
        st.warning("⚠️ Please enter a Google Drive URL")