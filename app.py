import streamlit as st
import requests
import os
from dotenv import load_dotenv

# ------------------------
# CONFIG
# ------------------------
st.set_page_config(page_title="SunoSur", layout="wide")

# ------------------------
# STYLE
# ------------------------
st.markdown("""
<style>
body { background-color: #0b0b0c; color: white; }
.stTextInput > div > div > input {
    background-color: #1c1c1e;
    color: white;
    border-radius: 10px;
}
.stButton>button {
    background-color: #ff2d55;
    color: white;
    border-radius: 8px;
    height: 35px;
    border: none;
}
[data-testid="stSidebar"] { background-color: #111; }
</style>
""", unsafe_allow_html=True)

# ------------------------
# LOAD API KEY
# ------------------------
load_dotenv()
API_KEY = st.secrets["YOUTUBE_API_KEY"]

# ------------------------
# SESSION STATE
# ------------------------
if "current_video" not in st.session_state:
    st.session_state.current_video = None

if "queue" not in st.session_state:
    st.session_state.queue = []

if "playlist" not in st.session_state:
    st.session_state.playlist = []

# ------------------------
# SEARCH FUNCTION
# ------------------------
def search_youtube(query):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "key": API_KEY,
        "maxResults": 9,
        "type": "video"
    }

    res = requests.get(url, params=params).json()

    results = []
    for item in res.get("items", []):
        results.append({
            "video_id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"]
        })

    return results

# ------------------------
# SIDEBAR
# ------------------------
st.sidebar.title("🎵 SunoSur")
page = st.sidebar.radio("Navigate", ["Home", "Search", "Queue", "Playlist"])

# ------------------------
# PLAYER
# ------------------------
if st.session_state.current_video:
    st.markdown("### ▶ Now Playing")
    st.video(f"https://www.youtube.com/watch?v={st.session_state.current_video}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⏭ Next"):
            if st.session_state.queue:
                next_song = st.session_state.queue.pop(0)
                st.session_state.current_video = next_song["video_id"]
                st.rerun()

    st.markdown("---")

# ------------------------
# HOME
# ------------------------
if page == "Home":
    st.title("🏠 Home")

    mood = st.text_input("🎭 Mood (chill, gym, sad, focus)")

    if mood:
        results = search_youtube(mood + " music")

        cols = st.columns(3)

        for i, video in enumerate(results):
            with cols[i % 3]:
                st.image(video["thumbnail"], width="stretch")
                st.markdown(f"**{video['title']}**")

                if st.button("▶ Play", key=f"home_play_{video['video_id']}"):
                    st.session_state.current_video = video["video_id"]

                if st.button("➕ Queue", key=f"home_queue_{video['video_id']}"):
                    st.session_state.queue.append(video)

                if st.button("💾 Save", key=f"home_save_{video['video_id']}"):
                    st.session_state.playlist.append(video)

# ------------------------
# SEARCH
# ------------------------
if page == "Search":
    st.title("🔍 Search")

    query = st.text_input("Search songs")

    if query:
        results = search_youtube(query)

        cols = st.columns(3)

        for i, video in enumerate(results):
            with cols[i % 3]:
                st.image(video["thumbnail"], width="stretch")
                st.markdown(f"**{video['title']}**")

                if st.button("▶ Play", key=f"search_play_{video['video_id']}"):
                    st.session_state.current_video = video["video_id"]

                if st.button("➕ Queue", key=f"search_queue_{video['video_id']}"):
                    st.session_state.queue.append(video)

                if st.button("💾 Save", key=f"search_save_{video['video_id']}"):
                    st.session_state.playlist.append(video)

# ------------------------
# QUEUE PAGE
# ------------------------
if page == "Queue":
    st.title("⏭ Queue")

    if not st.session_state.queue:
        st.write("Queue is empty")
    else:
        for i, song in enumerate(st.session_state.queue):
            col1, col2 = st.columns([5,1])

            with col1:
                st.write(song["title"])

            with col2:
                if st.button("❌", key=f"remove_q_{i}"):
                    st.session_state.queue.pop(i)
                    st.rerun()

# ------------------------
# PLAYLIST PAGE
# ------------------------
if page == "Playlist":
    st.title("📁 Your Playlist")

    if not st.session_state.playlist:
        st.write("No songs saved yet")
    else:
        for i, song in enumerate(st.session_state.playlist):
            col1, col2, col3 = st.columns([5,1,1])

            with col1:
                st.write(song["title"])

            with col2:
                if st.button("▶", key=f"plist_play_{i}"):
                    st.session_state.current_video = song["video_id"]

            with col3:
                if st.button("❌", key=f"plist_remove_{i}"):
                    st.session_state.playlist.pop(i)
                    st.rerun()
