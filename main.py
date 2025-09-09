import os, sys
from dotenv import load_dotenv
import google.generativeai as genai

from drive_fetch import file_id_from_url, fetch_pdf_bytes
from text_extract import pdf_bytes_to_text
from prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

def summarize_report(
    report_url: str,
    cascaid_id: str = "UNKNOWN",
    full_name: str = "Unknown",
    report_type: str = "Unknown",
    report_date: str = "Unknown",
    model_name: str = "gemini-1.5-flash",
    max_chars: int = 120_000,
):
    file_id = file_id_from_url(report_url)
    pdf = fetch_pdf_bytes(file_id)
    text = pdf_bytes_to_text(pdf, max_pages=None)  # quick+dirty

    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[Truncated for token limits]"

    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel(model_name)

    # Combine system prompt with user prompt since Gemini doesn't support system role
    combined_prompt = f"{SYSTEM_PROMPT}\n\n{USER_PROMPT_TEMPLATE.format(
        full_name=full_name,
        cascaid_id=cascaid_id,
        report_type=report_type,
        report_date=report_date,
        report_text=text,
    )}"
    
    parts = [{"role": "user", "parts": [combined_prompt]}]

    resp = model.generate_content(parts)
    return resp.text

if __name__ == "__main__":
    load_dotenv()
    report_url = os.getenv("REPORT_URL") or (sys.argv[1] if len(sys.argv) > 1 else None)
    if not report_url:
        print("Usage: python main.py <drive_report_url>  (or set REPORT_URL in .env)")
        sys.exit(1)

    summary = summarize_report(
        report_url=report_url,
        cascaid_id=os.getenv("CASCAID_ID", "UNKNOWN"),
        full_name=os.getenv("FULL_NAME", "Unknown"),
        report_type=os.getenv("REPORT_TYPE", "Unknown"),
        report_date=os.getenv("REPORT_DATE", "Unknown"),
    )
    print("\n=== SUMMARY ===\n")
    print(summary)
