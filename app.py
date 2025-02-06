import streamlit as st
import pandas as pd
import numpy as np
import pickle
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

# กำหนด CLIENT_ID และ CLIENT_SECRET ของคุณ (กรุณาเก็บข้อมูลนี้เป็นความลับ)
CLIENT_ID = "your_spotify_client_id"
CLIENT_SECRET = "your_spotify_client_secret"

# สร้างไดเรกทอรี 'data' หากยังไม่มี
if not os.path.exists('data'):
    os.makedirs('data')

# **โหลด DataFrame จากไฟล์ 'df.pkl'**
music_df = pd.read_pickle('C:/JN/data/df.pkl')

# **โหลดเมทริกซ์ความคล้ายคลึงจากไฟล์ 'similarity.pkl'**
with open('C:/JN/data/similarity.pkl', 'rb') as f:
    similarity_matrix = pickle.load(f)

# **ตรวจสอบข้อมูล**
print("แสดงข้อมูล 5 แถวแรกของ DataFrame:")
print(music_df.head())
print(f"\nขนาดของ DataFrame: {music_df.shape}")

# **Initialize the Spotify client**
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_song_album_cover_url(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track", limit=1)
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        album_cover_url = track['album']['images'][0]['url']
        return album_cover_url
    else:
        # ใช้รูปภาพสำรองหากไม่พบ
        return "https://i.postimg.cc/0QNxYz4V/social.png"

def recommend(song):
    if song not in music_df['song'].values:
        return [], []
    index = music_df[music_df['song'] == song].index[0]
    distances = list(enumerate(similarity_matrix[index]))
    distances = sorted(distances, key=lambda x: x[1], reverse=True)
    
    recommended_music_names = []
    recommended_music_posters = []
    for i in distances[1:6]:
        song_name = music_df.iloc[i[0]]['song']
        artist_name = music_df.iloc[i[0]]['artist']
        recommended_music_names.append(song_name)
        album_cover_url = get_song_album_cover_url(song_name, artist_name)
        recommended_music_posters.append(album_cover_url)
    return recommended_music_names, recommended_music_posters

st.header('🎵 Music Recommender System')

# **รายการเพลงสำหรับเลือก**
song_list = music_df['song'].tolist()
selected_song = st.selectbox("เลือกเพลงที่คุณชื่นชอบ", song_list)

if st.button('แสดงเพลงแนะนำ'):
    recommendations, posters = recommend(selected_song)
    if recommendations:
        cols = st.columns(len(recommendations))
        for idx, col in enumerate(cols):
            with col:
                st.text(recommendations[idx])
                st.image(posters[idx])
    else:
        st.write("ขออภัย ไม่พบคำแนะนำสำหรับเพลงนี้")
