import re
from google.auth import default
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def _build_drive():
    # Uses application default credentials (from gcloud auth application-default login)
    creds, _ = default(scopes=SCOPES)
    return build("drive", "v3", credentials=creds)

def file_id_from_url(url: str) -> str:
    # Handles .../file/d/<ID>/..., /document/d/<ID>/..., open?id=<ID>, etc.
    m = re.search(r"/d/([A-Za-z0-9_-]+)", url)
    if m: return m.group(1)
    m = re.search(r"[?&]id=([A-Za-z0-9_-]+)", url)
    if m: return m.group(1)
    raise ValueError("Could not parse file id from URL")

def fetch_pdf_bytes(file_id: str) -> bytes:
    """
    If the file is a PDF -> download bytes.
    If it's a Google Doc -> export as PDF (or text later).
    """
    drive = _build_drive()
    meta = drive.files().get(
        fileId=file_id,
        fields="id, name, mimeType",
        supportsAllDrives=True,
    ).execute()
    mime = meta["mimeType"]

    if mime == "application/pdf":
        request = drive.files().get_media(fileId=file_id, supportsAllDrives=True)
        return request.execute()

    # Google Docs export as PDF
    google_doc_types = {
        "application/vnd.google-apps.document": "application/pdf",
        "application/vnd.google-apps.presentation": "application/pdf",
        "application/vnd.google-apps.spreadsheet": "application/pdf",
    }
    if mime in google_doc_types:
        request = drive.files().export_media(
            fileId=file_id,
            mimeType=google_doc_types[mime],
        )
        return request.execute()

    # Fallback: try direct media (some images, etc.)
    request = drive.files().get_media(fileId=file_id, supportsAllDrives=True)
    return request.execute()