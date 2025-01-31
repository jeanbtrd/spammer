import os, shutil
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

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

def read_text_file(file_path):
    """Reads the content of a text file and returns it as a string."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()  # Read full text and strip extra spaces

def find_first_file_by_extension(folder_path, extensions):
    """Finds the first file with a given set of extensions in a folder."""
    for file in os.listdir(folder_path):
        if file.lower().endswith(extensions):
            return os.path.join(folder_path, file)  # Return full path
    return None  # No matching file found

def upload_all_videos(youtube, folder_path="./videos"):
    """Uploads all videos in the specified folder."""
    for folder in os.listdir(folder_path):
        folder_full_path = os.path.join(folder_path, folder)

        if os.path.isdir(folder_full_path):
            video_path = find_first_file_by_extension(folder_full_path, (".mp4", ".mov", ".avi", ".mkv"))
            text_file_path = find_first_file_by_extension(folder_full_path, (".txt",))

            if video_path and text_file_path:
                title = os.path.splitext(os.path.basename(video_path))[0]  # Extract title from video filename
                description = read_text_file(text_file_path)  # Read the first .txt file as description

                try:
                    print(f"Uploading {video_path} - Title: {title}")
                    upload_video(youtube, video_path, title, description)  # Upload
                except Exception as e:
                    print(f"Failed to upload {video_path} - Error: {e}")
            else:
                print(f"Skipping {folder} - Missing video or text file")

def clear_folder(folder_path):
    """Deletes all files and subdirectories in a folder, but keeps the folder itself"""
    for item in os.listdir(folder_path): # List all items in the folder
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path) # Delete subdirectory and all its contents
        else:
            os.remove(item_path) # Delete file
    print(f"Cleared contents of {folder_path}")

if __name__ == '__main__':
    # Authenticate and get YouTube API service
    youtube = authenticate() 

    # Upload everything
    videos_path = './videos'
    upload_all_videos(youtube, videos_path)

    # Delete everything
    clear_folder(videos_path)
