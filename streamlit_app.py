"""
Cascaid Agent HQ - Streamlit Web App
Streamlit-based web service for processing PDF reports
"""

import streamlit as st
import os
import json
from dotenv import load_dotenv

# Import your existing functions
from main import summarize_report

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Cascaid Agent HQ",
    page_icon="��",
    layout="wide"
)

st.title("🏥 Cascaid Agent HQ")
st.markdown("**PDF Report Summarization System**")

# API endpoint for external calls
if st.query_params.get("api") == "true":
    # This handles API calls from your Apps Script
    if st.query_params.get("method") == "POST":
        try:
            # Get JSON data from request body
            # Note: Streamlit doesn't handle POST bodies the same way as Flask
            # We'll use query parameters instead
            report_url = st.query_params.get("report_url")
            
            if not report_url:
                st.json({"success": False, "error": "report_url is required"})
                st.stop()
            
            # Process the report
            summary = summarize_report(
                report_url=report_url,
                cascaid_id=st.query_params.get("cascaid_id", "UNKNOWN"),
                full_name=st.query_params.get("full_name", "Unknown"),
                report_type=st.query_params.get("report_type", "Unknown"),
                report_date=st.query_params.get("report_date", "Unknown")
            )
            
            st.json({
                "success": True,
                "summary": summary,
                "metadata": {
                    "cascaid_id": st.query_params.get("cascaid_id", "UNKNOWN"),
                    "full_name": st.query_params.get("full_name", "Unknown"),
                    "report_type": st.query_params.get("report_type", "Unknown"),
                    "report_date": st.query_params.get("report_date", "Unknown")
                }
            })
            
        except Exception as e:
            st.json({"success": False, "error": str(e)})
    else:
        st.json({"success": False, "error": "Method not allowed"})
else:
    # Regular Streamlit UI
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
        with st.spinner("Processing report... This may take a few moments."):
            try:
                summary = summarize_report(
                    report_url=report_url,
                    cascaid_id=cascaid_id,
                    full_name=full_name,
                    report_type=report_type,
                    report_date=report_date
                )
                
                st.success("✅ Report processed successfully!")
                st.markdown("### 📋 AI Summary")
                st.markdown(summary)
                
            except Exception as e:
                st.error(f"❌ Error processing report: {str(e)}")
    
    elif submitted and not report_url:
        st.warning("⚠️ Please enter a Google Drive URL")

# Health check endpoint
if st.query_params.get("health") == "true":
    st.json({"status": "healthy", "service": "cascaid-agent-hq"})