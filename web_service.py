"""
Cascaid Agent HQ - Web Service
Flask-based web service for processing PDF reports via HTTP requests
"""

import os
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Import your existing functions
from main import summarize_report

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/process-report', methods=['POST'])
def process_report():
    """
    Process a PDF report and return AI-generated summary
    Expected JSON payload:
    {
        "report_url": "https://drive.google.com/file/d/FILE_ID/view",
        "cascaid_id": "optional_patient_id",
        "full_name": "optional_patient_name", 
        "report_type": "optional_report_type",
        "report_date": "optional_report_date"
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False, 
                'error': 'No JSON data provided'
            }), 400
        
        # Extract required fields
        report_url = data.get('report_url')
        if not report_url:
            return jsonify({
                'success': False,
                'error': 'report_url is required'
            }), 400
        
        # Extract optional fields
        cascaid_id = data.get('cascaid_id', 'UNKNOWN')
        full_name = data.get('full_name', 'Unknown')
        report_type = data.get('report_type', 'Unknown')
        report_date = data.get('report_date', 'Unknown')
        
        # Process the report using your existing function
        summary = summarize_report(
            report_url=report_url,
            cascaid_id=cascaid_id,
            full_name=full_name,
            report_type=report_type,
            report_date=report_date
        )
        
        return jsonify({
            'success': True,
            'summary': summary,
            'metadata': {
                'cascaid_id': cascaid_id,
                'full_name': full_name,
                'report_type': report_type,
                'report_date': report_date
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'cascaid-agent-hq'
    })

if __name__ == '__main__':
    # For local testing
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)