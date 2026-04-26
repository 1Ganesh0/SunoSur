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

# ------------------------
# YOUTUBE SEARCH
# ------------------------
def search_youtube(query):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "key": API_KEY,
        "maxResults": 5,
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
# SMART RADIO FUNCTION
# ------------------------
def generate_radio(song_title):
    words = song_title.split()

    # take first 2–3 meaningful words
    base = " ".join(words[:3])

    queries = [
        base,
        base + " songs",
        base + " playlist",
        base + " similar songs"
    ]

    radio_results = []

    for q in queries:
        res = search_youtube(q)
        radio_results.extend(res)

    # remove duplicates
    seen = set()
    unique = []
    for r in radio_results:
        if r["video_id"] not in seen:
            unique.append(r)
            seen.add(r["video_id"])

    return unique[:8]   # limit queue size

# ------------------------
# SIDEBAR
# ------------------------
st.sidebar.title("🎵 SunoSur")
page = st.sidebar.radio("Navigate", ["Search", "Queue"])

radio_mode = st.sidebar.toggle("🎧 Radio Mode")

# ------------------------
# PLAYER
# ------------------------
if st.session_state.current_video:
    st.markdown("### ▶ Now Playing")
    st.video(f"https://www.youtube.com/watch?v={st.session_state.current_video}")

    if st.button("⏭ Next"):
        if st.session_state.queue:
            next_song = st.session_state.queue.pop(0)
            st.session_state.current_video = next_song["video_id"]
            st.rerun()

    st.markdown("---")

# ------------------------
# SEARCH PAGE
# ------------------------
if page == "Search":
    st.title("🔍 Search Songs")

    query = st.text_input("Search")

    if query:
        results = search_youtube(query)

        for video in results:
            st.image(video["thumbnail"])
            st.write(video["title"])

            if st.button("▶ Play", key=video["video_id"]):
                st.session_state.current_video = video["video_id"]

                # 🎧 RADIO LOGIC
                if radio_mode:
                    st.session_state.queue.clear()
                    radio_songs = generate_radio(video["title"])
                    st.session_state.queue.extend(radio_songs)

            if st.button("➕ Queue", key=f"q_{video['video_id']}"):
                st.session_state.queue.append(video)

# ------------------------
# QUEUE PAGE
# ------------------------
if page == "Queue":
    st.title("⏭ Queue")

    if not st.session_state.queue:
        st.write("Queue is empty")
    else:
        for i, song in enumerate(st.session_state.queue):
            st.write(song["title"])

            if st.button("❌", key=f"remove_{i}"):
                st.session_state.queue.pop(i)
                st.rerun()
