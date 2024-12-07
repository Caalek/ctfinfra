import os

from CTFd.utils import get_app_config, uploads
from CTFd.utils.encoding import hexencode
from CTFd.utils.uploads.uploaders import BaseUploader
from flask import redirect
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


class GoogleDriveUploader(BaseUploader):
    def __init__(self):
        super(BaseUploader, self).__init__()
        self.project_id = os.getenv("GOOGLE_PROJECT_ID") or get_app_config(
            "GOOGLE_PROJECT_ID"
        )
        self.private_key_id = os.getenv("GOOGLE_PRIVATE_KEY_ID") or get_app_config(
            "GOOGLE_PRIVATE_KEY_ID"
        )
        self.private_key = os.getenv("GOOGLE_PRIVATE_KEY") or get_app_config(
            "GOOGLE_PRIVATE_KEY"
        )
        self.client_email = os.getenv("GOOGLE_CLIENT_EMAIL") or get_app_config(
            "GOOGLE_CLIENT_EMAIL"
        )
        self.client_id = os.getenv("GOOGLE_CLIENT_ID") or get_app_config(
            "GOOGLE_CLIENT_ID"
        )
        self.root_path = (
            os.getenv("GOOGLE_ROOT_PATH")
            or get_app_config("GOOGLE_ROOT_PATH")
            or "/CTFd"
        )
        _credentials = service_account.Credentials.from_service_account_info(
            {
                "type": "service_account",
                "project_id": self.project_id,
                "private_key_id": self.private_key_id,
                "private_key": self.private_key,
                "client_email": self.client_email,
                "client_id": self.client_id,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://accounts.google.com/o/oauth2/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{self.client_email}",
            },
            scopes=["https://www.googleapis.com/auth/drive"],
        )
        self.service = build("drive", "v3", credentials=_credentials)
        self.root_path_id = (
            os.getenv("GOOGLE_SHARED_FOLDER_ID")
            or get_app_config("GOOGLE_SHARED_FOLDER_ID")
            or self._get_or_create_root_path_id()
        )

    def _get_or_create_root_path_id(self):
        query = (
            f"name='{self.root_path}' and mimeType='application/vnd.google-apps.folder'"
        )
        results = self.service.files().list(q=query, fields="files(id)").execute()
        folders = results.get("files", [])

        # If folder exists, return its ID
        if folders:
            return folders[0]["id"]

        # If folder doesn't exist, create it
        folder_metadata = {
            "name": self.root_path,
            "mimeType": "application/vnd.google-apps.folder",
        }
        new_folder = (
            self.service.files().create(body=folder_metadata, fields="id").execute()
        )
        return new_folder["id"]

    def store(self, fileobj, filename):
        file_metadata = {"name": filename, "parents": [self.root_path_id]}
        mimetype = "application/octet-stream" if not fileobj.mimetype else fileobj.mimetype  # According to https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
        media = MediaIoBaseUpload(fileobj, mimetype=mimetype)
        uploaded_file = (
            self.service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )

        # We want uploaded files to be accessible from the Internet
        permission = {"type": "anyone", "role": "reader"}

        self.service.permissions().create(
            fileId=uploaded_file["id"], body=permission
        ).execute()

        return filename

    def upload(self, file_obj, filename):
        extension = "data"

        if "." in filename:
            extension = filename.split(".")[-1]

        encoded_hash = hexencode(os.urandom(16))

        dst = f"{encoded_hash}.{extension}"
        self.store(file_obj, dst)
        return dst

    def download(self, filename):
        query = f"name='{filename}' and trashed=false"
        response = (
            self.service.files().list(q=query, fields="files(webContentLink)").execute()
        )

        files = response.get("files", [])
        if len(files) == 0:
            return False

        download_link = files[0]["webContentLink"].replace("&export=download", "")
        return redirect(download_link)

    def delete(self, filename):
        query = f"name='{filename}' and trashed=false"
        response = self.service.files().list(q=query, fields="files(id)").execute()

        files = response.get("files", [])
        if len(files) == 0:
            return False
        self.service.files().delete(fileId=files[0]["id"]).execute()
        return True

    def sync(self):
        pass  # Maybe TODO - You don't really need it


def load(app):
    uploads.UPLOADERS.update({"googledrive": GoogleDriveUploader})
