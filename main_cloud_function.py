"""
Cloud Function entry point for Cascaid Agent HQ
"""

import functions_framework
from web_service import app

@functions_framework.http
def process_report(request):
    """Cloud Function entry point"""
    return app(request.environ, lambda *args: None)