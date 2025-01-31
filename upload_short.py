import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import googleapiclient.http

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def authenticate():
    """Authenticate and return the YouTube API client."""
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        "client_secrets.json", SCOPES
    )
    credentials = flow.run_local_server(port=8080)
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
    return youtube

def upload_video(video_path, title, description, category_id="22", privacy_status="public"):
    """Uploads a video to YouTube Shorts."""
    youtube = authenticate()

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["Shorts", "Automation"],
                "categoryId": category_id,
            },
            "status": {"privacyStatus": privacy_status},
        },
        media_body=googleapiclient.http.MediaFileUpload(video_path, chunksize=-1, resumable=True),
    )

    response = request.execute()
    print(f"Uploaded: {response['id']} - {title}")

if __name__ == "__main__":
    video_file = "./videos/video.mp4"  # Change this to your video file path
    upload_video(video_file, "My Automated YouTube Short", "This is an automated upload!")