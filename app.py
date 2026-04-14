import streamlit as st
import requests
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ------------------------
# CONFIG
# ------------------------
st.set_page_config(page_title="SunoSur", layout="wide")

# ------------------------
# STYLE
# ------------------------
st.markdown("""
<style>
body {
    background-color: #0b0b0c;
}

/* Buttons */
.stButton>button {
    border-radius: 8px;
    height: 36px;
    background-color: #ff2d55;
    color: white;
    border: none;
    font-size: 12px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #111;
}

/* Card look */
.card {
    padding: 10px;
    border-radius: 10px;
    background-color: #1c1c1e;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ------------------------
# LOAD API
# ------------------------
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_recommendations(query, results):
    titles = [video["title"] for video in results]

    # Convert to embeddings
    embeddings = model.encode(titles)
    query_embedding = model.encode([query])

    # Compute similarity
    similarities = cosine_similarity(query_embedding, embeddings)[0]

    # Sort results
    sorted_indices = similarities.argsort()[::-1]

    recommended = [results[i] for i in sorted_indices[:5]]

    return recommended

# ------------------------
# YOUTUBE SEARCH
# ------------------------
def search_youtube(query):
    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": query,
        "key": API_KEY,
        "maxResults": 6,
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
# SESSION
# ------------------------
if "current_video" not in st.session_state:
    st.session_state.current_video = None

if "playlist" not in st.session_state:
    st.session_state.playlist = []

# ------------------------
# SIDEBAR
# ------------------------
st.sidebar.title("🎵 SunoSur")
page = st.sidebar.radio("Navigate", ["Home", "Search", "Library"])

# ------------------------
# MINI PLAYER (TOP)
# ------------------------
if st.session_state.current_video:
    col1, col2 = st.columns([1, 5])

    with col1:
        st.markdown("▶")

    with col2:
        st.video(f"https://www.youtube.com/watch?v={st.session_state.current_video}")

    st.markdown("---")

# ------------------------
# HOME TAB
# ------------------------
if page == "Home":
    st.title("🏠 Home")

    st.subheader("🎭 Mood")
    mood = st.text_input("Enter mood (chill, gym, sad, focus)")

    if mood:
        results = search_youtube(mood + " music")

        cols = st.columns(3)
        for i, video in enumerate(results):
            with cols[i % 3]:
                st.image(video["thumbnail"], use_container_width=True)
                st.caption(video["title"])

                if st.button("▶", key=f"home_{video['video_id']}"):
                    st.session_state.current_video = video["video_id"]

                if st.button("➕", key=f"home_add_{video['video_id']}"):
                    st.session_state.playlist.append(video)

# ------------------------
# SEARCH TAB
# ------------------------
if page == "Search":
    st.title("🔍 Search")

    query = st.text_input("Search songs")

    if query:
        results = search_youtube(query)

        st.subheader("Results")
        cols = st.columns(3)

        for i, video in enumerate(results):
            with cols[i % 3]:
                st.image(video["thumbnail"], use_container_width=True)
                st.caption(video["title"])

                if st.button("▶", key=f"search_{video['video_id']}"):
                    st.session_state.current_video = video["video_id"]

                if st.button("➕", key=f"search_add_{video['video_id']}"):
                    st.session_state.playlist.append(video)

        st.subheader("🤖 Recommended")
        rec = get_recommendations(query, results)

        cols = st.columns(3)
        for i, video in enumerate(rec):
            with cols[i % 3]:
                st.image(video["thumbnail"], use_container_width=True)
                st.caption(video["title"])

                if st.button("▶", key=f"rec_{video['video_id']}"):
                    st.session_state.current_video = video["video_id"]

# ------------------------
# LIBRARY TAB
# ------------------------
if page == "Library":
    st.title("📁 Your Library")

    if st.session_state.playlist:
        for i, song in enumerate(st.session_state.playlist):
            col1, col2, col3 = st.columns([5, 1, 1])

            with col1:
                st.write(song["title"])

            with col2:
                if st.button("▶", key=f"plist_{i}"):
                    st.session_state.current_video = song["video_id"]

            with col3:
                if st.button("❌", key=f"remove_{i}"):
                    st.session_state.playlist.pop(i)
                    st.rerun()
    else:
        st.write("No songs added yet")