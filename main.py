#!/usr/bin/python3
import os
import shutil
from ytmusicapi import YTMusic
from yt_dlp import YoutubeDL
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# --- CONFIG ---
PORT = int(os.environ.get("PORT", 8000))
CACHE_DIR = "static/cache"
audioformat = "webm"

# Optimized for speed and compatibility
ydl_opts = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "outtmpl": f"{CACHE_DIR}/%(id)s.{audioformat}",
    "quiet": False,
}

# --- STARTUP SETUP ---
if os.path.exists(CACHE_DIR):
    shutil.rmtree(CACHE_DIR)
os.makedirs(CACHE_DIR, exist_ok=True)

def SearchMusic(query, searchtype, limit):
    ytmusic = YTMusic()
    return ytmusic.search(query, searchtype, None, limit, ignore_spelling=False)

def GetChannel(id):
    ytmusic = YTMusic()
    return ytmusic.get_artist(id)

def GetAlbum(id):
    ytmusic = YTMusic()
    return ytmusic.get_album(id)

@app.route("/", methods=("GET", "POST"))
def home():
    if request.method == "POST":
        searchkeyword = request.form["searchbar"]
        songresults = SearchMusic(searchkeyword, "songs", 40)
        albumresults = SearchMusic(searchkeyword, "albums", 6)
        return render_template("main.html", results=songresults, albumresults=albumresults, searchkeyword=searchkeyword)
    
    songresults = SearchMusic("music", "songs", 40)
    albumresults = SearchMusic("music", "albums", 40)
    return render_template("main.html", results=songresults, albumresults=albumresults, startPage=True)

@app.route('/music/<id>')
def music(id):
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([id])
        info = YoutubeDL(ydl_opts).extract_info(id, download=False)
        results = GetChannel(info["channel_id"])
        return render_template("player.html", audiourl=f"/{CACHE_DIR}/{id}.{audioformat}", info=info, results=results)
    except Exception as e:
        print(f"Error playing music: {e}")
        return str(e), 500

@app.route('/api/album/<id>/<number>')
def apialbum(id, number):
    try:
        results = GetAlbum(id)
        song_id = results["tracks"][int(number)]["videoId"]
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([song_id])
        return redirect(f"/{CACHE_DIR}/{song_id}.{audioformat}")
    except Exception as e:
        print(f"API Error: {e}")
        return str(e), 500

@app.route('/album/<id>')
def album(id):
    results = GetAlbum(id)
    return render_template("albumview.html", results=results, albumid=id)

if __name__ == "__main__":
    from waitress import serve
    print(f"Server starting on port {PORT}...")
    serve(app, host="0.0.0.0", port=PORT)
