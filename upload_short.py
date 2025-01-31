import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Scopes required for uploading to YouTube
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

# Path to your client_secrets.json file
CLIENT_SECRETS_FILE = 'client_secrets.json'
TOKEN_FILE = 'token.json'

def authenticate():
    """Authenticate and return the YouTube API service."""
    credentials = None

    # Check if token already exists
    if os.path.exists(TOKEN_FILE):
        print('Loading credentials from file...')
        with open(TOKEN_FILE, 'rb') as token:
            credentials = pickle.load(token)

    # If no valid credentials are available, let the user log in
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print('Refreshing expired credentials...')
            credentials.refresh(Request())
        else:
            print('Authentication required...')
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=8080)
        
        # Save credentials to a file for future runs
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(credentials, token)

    # Build the YouTube API client
    youtube = build('youtube', 'v3', credentials=credentials)
    return youtube

def upload_video(youtube, video_path, title, description, category_id="22", privacy_status="public"):
    """Uploads a video to YouTube Shorts."""
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
        media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True),
    )

    response = request.execute()
    print(f"Uploaded: {response['id']} - {title}")

    #pass

if __name__ == '__main__':
    # Authenticate and get YouTube API service
    youtube = authenticate() 

    # Upload video, then delete it
    video_path = './videos/video.mp4'                       # specs
    title = 'test short'
    description = 'this is a test'
    upload_video(youtube, video_path, title, description)   # upload
    os.remove(video_path)                                   # delete


