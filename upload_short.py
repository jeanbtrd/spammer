###############################################################################
#                               LIBRARIES
###############################################################################

import os, shutil
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request


###############################################################################
#                               CONSTANTS
###############################################################################

# Scopes required for uploading to YouTube
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

# Path to your client_secrets.json file
CLIENT_SECRETS_FILE = 'client_secrets.json'

# Path to your token.json file
TOKEN_FILE = 'token.json'

# Path to where you keep the videos
VIDEOS_PATH = './videos'


###############################################################################
#                               FILES
###############################################################################

def read_text_file(file_path):
    """Reads the content of a text file and returns it as a string."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()  # Read full text and strip extra spaces

def find_first_file_by_extension(folder_path, extensions):
    """Finds the first file with a given set of extensions in a folder. Returns its path."""
    for file in os.listdir(folder_path):
        if file.lower().endswith(extensions):
            return os.path.join(folder_path, file)  # Return full path
    return None  # No matching file found

def clear_folder(folder_path):
    """Deletes all files and subdirectories in a folder, but keeps the folder itself"""
    for item in os.listdir(folder_path): # List all items in the folder
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path) # Delete subdirectory and all its contents
        else:
            os.remove(item_path) # Delete file
    print(f"Cleared contents of {folder_path}")


###############################################################################
#                               VIDEO
###############################################################################

class Video():
    """ The video's class. All file managing and uploading will be ported here. """

    def __init__(self, dir):
        """Initialization. Title description etc gotten from dir."""
        # FLAGS
        self.up_yt = False  # Uploaded on youtube
        # INFO
        self.dir = dir      # Folder of the video
        self.path = find_first_file_by_extension(dir, (".mp4", ".mov", ".avi", ".mkv")) # Path
        self.title = os.path.splitext(os.path.basename(self.path))[0]                   # Title
        self.descr = read_text_file(find_first_file_by_extension(dir, "txt"))           # Description

    def __del__(self):
        """Destructor. Eliminates video folder and its contents."""
        if (self.up_yt):
            shutil.rmtree(self.dir)
            return True
        else:
            print("Video not yet uploaded on Youtube. Not removing it.\n")
            return False

    def yt_upload(self, youtube, category_id="22", privacy_status="public"):
        """Uploads the video on youtube."""
        # Set up the request
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": self.title,
                    "description": self.descr,
                    "tags": ["Shorts", "Automation"],
                    "categoryId": category_id,
                },
                "status": {"privacyStatus": privacy_status},
            },
            media_body = MediaFileUpload(self.path, chunksize=-1, resumable=True),
        )

        # Do (try) it
        try:
            print(f"Uploading {self.path} - Title: {self.title}\n")
            response = request.execute()
            print(f"Uploaded: {response['id']} - {self.title}")
            self.up_yt = True
            return True
        except Exception as e:
            print(f"Failed to upload {self.path} - Error: {e}")
            return False


###############################################################################
#                               AUTHENTICATION
###############################################################################

def yt_authenticate():
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


###############################################################################
#                               MAIN
###############################################################################

if __name__ == '__main__':
    # Authenticate and get YouTube API service
    youtube = yt_authenticate() 

    # Upload everything on youtube
    for dir in os.listdir(VIDEOS_PATH):
        dir_path = os.path.join(VIDEOS_PATH, dir)
        if os.path.isdir(dir_path):
            short = Video(dir=dir_path)
            short.yt_upload(youtube=youtube)
            if (short.up_yt): del short

    # Delete everything
    #clear_folder(videos_path)
