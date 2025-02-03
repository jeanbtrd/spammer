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

# Path to where you keep the videos
VIDEOS_PATH = './videos'

####    Youtube     ####
#
# Scopes required for uploading to YouTube
SCOPES_YT = ['https://www.googleapis.com/auth/youtube.upload']
# Path to your client_secrets.json file
CLIENT_SECRETS_YT = 'client_secrets_yt.json'
# Paths to your youtube token file
TOKEN_FILE_YT = 'token_yt.json'

####    Instagram   ####
#
CLIENT_ID_IG = 'YOUR_CLIENT_ID'
CLIENT_SECRET_IG = 'YOUR_CLIENT_SECRET'
REDIRECT_URI_IG = 'YOUR_REDIRECT_URI'
TOKEN_FILE_IG = 'instagram_token.json'
SCOPES_IG = 'user_profile,user_media'


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
    if os.path.exists(TOKEN_FILE_YT):
        print('Loading credentials from file...')
        with open(TOKEN_FILE_YT, 'rb') as token:
            credentials = pickle.load(token)

    # If no valid credentials are available, let the user log in
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print('Refreshing expired credentials...')
            credentials.refresh(Request())
        else:
            print('Authentication required...')
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_YT, SCOPES_YT)
            credentials = flow.run_local_server(port=8080)
        
        # Save credentials to a file for future runs
        with open(TOKEN_FILE_YT, 'wb') as token:
            pickle.dump(credentials, token)

    # Build the YouTube API client
    youtube = build('youtube', 'v3', credentials=credentials)
    return youtube

def ig_authenticate():
    """Authenticate and return the Instagram API access token."""
    access_token = None

    # Check if token already exists
    if os.path.exists(TOKEN_FILE_IG):
        print('Loading credentials from file...')
        with open(TOKEN_FILE_IG, 'r') as token_file:
            data = json.load(token_file)
            access_token = data.get('access_token')

    # If no token or token is invalid, start OAuth flow
    if not access_token:
        print('Authentication required...')
        auth_url = (
            f'https://api.instagram.com/oauth/authorize'
            f'?client_id={CLIENT_ID_IG}'
            f'&redirect_uri={REDIRECT_URI_IG}'
            f'&scope={SCOPES_IG}'
            f'&response_type=code'
        )
        print(f'Please visit this URL to authorize the app: {auth_url}')

        auth_code = input('Enter the code from the redirect URL: ')

        # Exchange code for access token
        token_url = 'https://api.instagram.com/oauth/access_token'
        payload = {
            'client_id': CLIENT_ID_IG,
            'client_secret': CLIENT_SECRET_IG,
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI_IG,
            'code': auth_code
        }
        response = requests.post(token_url, data=payload)
        if response.status_code == 200:
            access_data = response.json()
            access_token = access_data['access_token']

            # Save token for future use
            with open(TOKEN_FILE_IG, 'w') as token_file:
                json.dump(access_data, token_file)
        else:
            print('Error obtaining access token:', response.text)
            return None

    return access_token


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
