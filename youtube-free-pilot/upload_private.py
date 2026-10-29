#!/usr/bin/env python3
"""Upload one generated Shorts video as PRIVATE. Do not embed credentials in code."""
import json
import os
import sys
from pathlib import Path

YOUTUBE_SCOPE = "https://www.googleapis.com/auth/youtube.upload"

def upload(metadata_path):
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    names = ("YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN")
    absent = [name for name in names if not os.environ.get(name)]
    if absent:
        raise RuntimeError("Missing required GitHub Actions secrets: " + ", ".join(absent))

    meta_file = Path(metadata_path)
    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    video = Path(meta["video_path"])
    if not video.is_file():
        raise FileNotFoundError("The generated MP4 is missing: " + str(video))

    creds = Credentials(
        token=None,
        refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"],
        client_id=os.environ["YOUTUBE_CLIENT_ID"],
        client_secret=os.environ["YOUTUBE_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=[YOUTUBE_SCOPE],
    )
    creds.refresh(Request())
    youtube = build("youtube", "v3", credentials=creds, cache_discovery=False)
    body = {
        "snippet": {
            "title": meta["title"],
            "description": meta["description"],
            "tags": meta.get("tags", []),
            "categoryId": str(meta.get("category_id", "28")),
            "defaultLanguage": "ar",
        },
        "status": {
            "privacyStatus": "private",  # hardcoded safety rule; never public in pilot
            "selfDeclaredMadeForKids": bool(meta.get("made_for_kids", False)),
        },
    }
    media = MediaFileUpload(str(video), mimetype="video/mp4", resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print("Upload progress: {:.0f}%".format(status.progress() * 100))
    video_id = response.get("id")
    if not video_id:
        raise RuntimeError("Upload response did not include a video id")
    url = "https://studio.youtube.com/video/" + video_id + "/edit"
    print(json.dumps({"uploaded": True, "privacy": "private", "video_id": video_id, "studio_url": url}))
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write("\n### Private YouTube upload successful\n")
            f.write("Video editor: " + url + "\n")
    return url

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python upload_private.py path/to/TRY-001.json")
    upload(sys.argv[1])
