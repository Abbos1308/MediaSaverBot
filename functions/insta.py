# That file provides all external functions for instagram part
import glob
import subprocess
import instaloader

shortcode = "DQFgIhRjOA4"



def get_files(shortcode):
    try:
        files = {"files":glob.glob(f"{shortcode}/*.mp4"),"video":True}
        if len(glob.glob(f"{shortcode}/*.jpg")) > 1:
            files["files"] += glob.glob(f"{shortcode}/*.jpg")
    except:
        files = {"files":glob.glob(f"{shortcode}/*.jpg"),"video":False}
    return files



def post(shortcode):
    L = instaloader.Instaloader()
    post = instaloader.Post.from_shortcode(L.context, shortcode)
    L.download_post(post, target=shortcode)   
    files = get_files(shortcode)
    print("All files : ",files)
    if files["video"] and len(files["files"])>2:
        files["files"].remove(f"{shortcode}/{post.date_utc.strftime("%Y-%m-%d_%H-%M-%S_UTC_1.jpg")}")

    return files["files"]

#print(post("DQ9s1PagMYr"))


