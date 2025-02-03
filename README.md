# What's this
This just spams shorts on youtube. You only provide the video files and their description. 
I plan on integrating in the same environment also instagram reels, tiktok, ...

# How to use
## Authentication
Get the Google API. I don't know, I don't remember, look it up. That's where you get that `client_secrets.json` file.

After doing that, cloning this repo, installing the required dependencies and running the script the first time, your browser will open and you'll have to log into a google account (maybe the one for which you activated the API), after this first time that info will be stored in a file named `token_yt.json` and subsequent runs of the script will just use that.

## Content
Create your content, whatever it is. I think this tool is best suited for ai-generated useless 10sec videos, that really shouldn't take up more than 0.5sec of your brain power cpu time.

Create a folder called `videos`, and for each video make a subfolder. This can have any name, but it must contain:
- the video file (currently `.mp4`, `.mov`, `.avi`, or `.mkv`), the name of which will be the yt short title
- a text file (ending in `.txt`), containing the text you want as description (file name is ignored)
Any other thing in there will be ignored, and if the video is successfully uploaded it will be deleted (with the subfolder and all its contents). The script assumes there's no other important stuff other than those two files (the video and its description), which are the first ones it finds in there.

## Upload
Run the script. Google's quotas will stop you at 9 per day. After the 9th of the day, it will try and do the others, but it will fail. Those naturally won't be deleted, as before the deletion there's a check on whether the video was successfully uploaded or not.

# What's next
Instagram, tiktok, ...
