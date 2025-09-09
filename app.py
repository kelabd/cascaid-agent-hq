from flask import Flask, request, jsonify
from drive_fetch import file_id_from_url, fetch_pdf_bytes
from text_extract import pdf_bytes_to_text
from prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
import google.generativeai as genai
import os

app = Flask(__name__)

# Configure Gemini
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

@app.route("/review", methods=["POST"])
def review():
    try:
        data = request.get_json()
        if not data or "file_url" not in data:
            return jsonify({"ok": False, "error": "Missing file_url"}), 400

        # Metadata from Apps Script payload
        report_url = data["file_url"]
        cascaid_id = data.get("cascaid_id", "UNKNOWN")
        full_name = data.get("full_name", "Unknown")
        report_type = data.get("report_type", "Unknown")
        report_date = data.get("report_date", "Unknown")

        # Download + extract
        file_id = file_id_from_url(report_url)
        pdf = fetch_pdf_bytes(file_id)
        text = pdf_bytes_to_text(pdf, max_pages=None)

        # Prompt
        prompt = USER_PROMPT_TEMPLATE.format(
            full_name=full_name,
            cascaid_id=cascaid_id,
            report_type=report_type,
            report_date=report_date,
            report_text=text[:100000],  # safety cutoff
        )

        model = genai.GenerativeModel("gemini-1.5-flash")
        resp = model.generate_content([SYSTEM_PROMPT + "\n\n" + prompt])

        return jsonify({"ok": True, "summary": resp.text})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
