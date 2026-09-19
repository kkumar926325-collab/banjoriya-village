from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

SCOPES = ["https://www.googleapis.com/auth/drive"]

FOLDER_ID = "1xQC68EtB9XfsjIDPGN1DvJ3fRrcnBeho"

def get_drive_service():
    token_file = "/etc/secrets/token.json"

    if not os.path.exists(token_file):
        token_file = "token.json"

    creds = Credentials.from_authorized_user_file(
        token_file,
        SCOPES
    )

    return build(
        "drive",
        "v3",
        credentials=creds
    )

def upload_to_drive(file_path):

    service = get_drive_service()

    file_name = os.path.basename(file_path)

    extension = file_name.rsplit(".", 1)[-1].lower()

    mime_types = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
        "mp4": "video/mp4",
        "webm": "video/webm",
        "ogg": "video/ogg"
    }

    mime_type = mime_types.get(
        extension,
        "application/octet-stream"
    )

    file_metadata = {
        "name": file_name,
        "parents": [FOLDER_ID]
    }

    media = MediaFileUpload(
        file_path,
        mimetype=mime_type,
        resumable=True
    )

    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id,name,mimeType,size"
    ).execute()

    return uploaded_file

def list_drive_files():
    service = get_drive_service()

    results = service.files().list(
        q=f"'{FOLDER_ID}' in parents and trashed = false",
        fields="files(id,name,mimeType,size)",
        orderBy="createdTime desc"
    ).execute()

    return results.get("files", [])

def get_drive_file(file_id):
    service = get_drive_service()
    return service.files().get(
        fileId=file_id,
        fields="id,name,mimeType,size"
    ).execute()

def list_drive_files():
    service = get_drive_service()

    results = service.files().list(
        q=f"'{FOLDER_ID}' in parents and trashed = false",
        fields="files(id,name,mimeType,size)",
        orderBy="createdTime desc"
    ).execute()

    return results.get("files", [])
