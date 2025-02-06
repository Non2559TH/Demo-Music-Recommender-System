import pickle
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import numpy as np
import os

CLIENT_ID = "eb6a3de8147842788ca4572b06728b08"
CLIENT_SECRET = "ffed6e5600e24157ada66d2dae3c1773"

# ตรวจสอบว่าโฟลเดอร์มีอยู่
os.makedirs('C:/JN/data', exist_ok=True)

# ตรวจสอบการมีอยู่ของไฟล์ df.pkl
if not os.path.exists('C:/JN/data/df.pkl'):
    music_df = pd.DataFrame({
        'song': ['Song1', 'Song2', 'Song3', 'Song4', 'Song5'],
        'artist': ['Artist1', 'Artist2', 'Artist3', 'Artist4', 'Artist5']
    })
    music_df.to_pickle('C:/JN/data/df.pkl')

# ตรวจสอบการมีอยู่ของไฟล์ similarity.pkl
if not os.path.exists('C:/JN/data/similarity.pkl'):
    similarity_matrix = np.random.rand(5, 5)
    with open('C:/JN/data/similarity.pkl', 'wb') as f:
        pickle.dump(similarity_matrix, f)

# Initialize the Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_song_album_cover_url(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")

    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        album_cover_url = track["album"]["images"][0]["url"]
        print(album_cover_url)
        return album_cover_url
    else:
        return "https://i.postimg.cc/0QNxYz4V/social.png"

def recommend(song):
    index = music[music['song'] == song].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_music_names = []
    recommended_music_posters = []
    for i in distances[1:6]:
        artist = music.iloc[i[0]].artist
        print(artist)
        print(music.iloc[i[0]].song)
        recommended_music_posters.append(get_song_album_cover_url(music.iloc[i[0]].song, artist))
        recommended_music_names.append(music.iloc[i[0]].song)

    return recommended_music_names, recommended_music_posters

st.header('Music Recommender System')

# โหลดไฟล์ df.pkl และ similarity.pkl
music = pickle.load(open('C:/JN/data/df.pkl', 'rb'))
similarity = pickle.load(open('C:/JN/data/similarity.pkl', 'rb'))

music_list = music['song'].values
selected_song = st.selectbox(
    "Type or select a song from the dropdown",
    music_list
)

if st.button('Show Recommendation'):
    recommended_music_names, recommended_music_posters = recommend(selected_song)
    
    if len(recommended_music_names) >= 5 and len(recommended_music_posters) >= 5:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.text(recommended_music_names[0])
            st.image(recommended_music_posters[0])
        with col2:
            st.text(recommended_music_names[1])
            st.image(recommended_music_posters[1])
        with col3:
            st.text(recommended_music_names[2])
            st.image(recommended_music_posters[2])
        with col4:
            st.text(recommended_music_names[3])
            st.image(recommended_music_posters[3])
        with col5:
            st.text(recommended_music_names[4])
            st.image(recommended_music_posters[4])
    else:
        st.error("ไม่สามารถแสดงคำแนะนำได้ เนื่องจากไม่มีคำแนะนำเพียงพอ")
