#!/usr/bin/env python3
"""Upload rendered GPP assets to Google Drive."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]


def get_credentials():
    service_json = os.getenv("GDRIVE_SERVICE_ACCOUNT_JSON")
    service_path = os.getenv("GDRIVE_CREDENTIALS_PATH")

    if service_json:
        info = json.loads(service_json)
        return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)

    if service_path and Path(service_path).exists():
        return service_account.Credentials.from_service_account_file(service_path, scopes=SCOPES)

    if Path("credentials.json").exists():
        return service_account.Credentials.from_service_account_file("credentials.json", scopes=SCOPES)

    raise RuntimeError("Missing Google Drive credentials. Set GDRIVE_SERVICE_ACCOUNT_JSON or GDRIVE_CREDENTIALS_PATH.")


def drive_service():
    return build("drive", "v3", credentials=get_credentials())


def find_folder(service, name: str, parent_id: str | None) -> str | None:
    escaped = name.replace("'", "\\'")
    parts = ["mimeType = 'application/vnd.google-apps.folder'", "trashed = false", f"name = '{escaped}'"]
    if parent_id:
        parts.append(f"'{parent_id}' in parents")
    query = " and ".join(parts)
    res = service.files().list(q=query, fields="files(id, name)", pageSize=10).execute()
    files = res.get("files", [])
    return files[0]["id"] if files else None


def ensure_folder(service, name: str, parent_id: str | None) -> str:
    existing = find_folder(service, name, parent_id)
    if existing:
        return existing
    metadata: dict[str, Any] = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id:
        metadata["parents"] = [parent_id]
    folder = service.files().create(body=metadata, fields="id").execute()
    return folder["id"]


def upload_file(service, path: Path, folder_id: str) -> str:
    metadata = {"name": path.name, "parents": [folder_id]}
    media = MediaFileUpload(str(path), resumable=True)
    created = service.files().create(body=metadata, media_body=media, fields="id, webViewLink").execute()
    return created["id"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wave", required=True)
    parser.add_argument("--folder-name", required=True)
    parser.add_argument("--local-dir", required=True)
    parser.add_argument("--sidecars", default="sidecars")
    parser.add_argument("--root-folder-id", default=os.getenv("GDRIVE_ROOT_FOLDER_ID"))
    args = parser.parse_args()

    if not args.root_folder_id:
        raise RuntimeError("Missing GDRIVE_ROOT_FOLDER_ID")

    service = drive_service()

    first_printing_id = ensure_folder(service, "First_Printing", args.root_folder_id)
    wave_folder_id = ensure_folder(service, args.folder_name, first_printing_id)

    local_dir = Path(args.local_dir)
    sidecar_dir = Path(args.sidecars)

    upload_records: list[dict[str, str]] = []
    for path in sorted(local_dir.glob("*.png")) + sorted(sidecar_dir.glob(f"{args.wave.lower()}*.json")) + sorted(sidecar_dir.glob(f"{args.wave}_*.json")):
        if path.exists():
            file_id = upload_file(service, path, wave_folder_id)
            upload_records.append({"filename": path.name, "drive_file_id": file_id})
            print(f"Uploaded {path.name}: {file_id}")

    upload_log = sidecar_dir / f"{args.wave.lower()}_gdrive_uploads.json"
    upload_log.write_text(json.dumps({"wave": args.wave, "drive_folder_id": wave_folder_id, "files": upload_records}, indent=2), encoding="utf-8")
    print(f"Drive folder id: {wave_folder_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
