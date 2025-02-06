import streamlit as st
import pandas as pd
import numpy as np
import pickle
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from sklearn.metrics.pairwise import cosine_similarity

# กำหนด CLIENT_ID และ CLIENT_SECRET ของคุณ (กรุณาเก็บข้อมูลนี้เป็นความลับ)
CLIENT_ID = "eb6a3de8147842788ca4572b06728b08"
CLIENT_SECRET = "ffed6e5600e24157ada66d2dae3c1773"

# สร้างไดเรกทอรี 'data' หากยังไม่มี
if not os.path.exists('data'):
    os.makedirs('data')

# **ส่วนที่คุณควรใส่โค้ดสำหรับนำเข้าชุดข้อมูลจาก CSV**
# โหลดข้อมูลเพลงจากไฟล์ CSV
music_df = pd.read_csv('spotify_millsongdata.csv')
# บันทึก DataFrame เป็นไฟล์ 'df.pkl'
music_df.to_pickle('data/df.pkl')

# **ส่วนที่คุณควรใส่โค้ดสำหรับคำนวณเมทริกซ์ความคล้ายคลึง**
from sklearn.metrics.pairwise import cosine_similarity

# เลือกคอลัมน์คุณสมบัติของเพลง
# แทนที่ด้วยชื่อคอลัมน์ของคุณ
features = music_df[['feature1', 'feature2', 'feature3']]

# หากคอลัมน์คุณสมบัติเป็นสตริง ต้องแปลงเป็นตัวเลขก่อน
# ตัวอย่างการใช้ One-Hot Encoding
# features = pd.get_dummies(features)

# คำนวณเมทริกซ์ความคล้ายคลึง
similarity_matrix = cosine_similarity(features)

# บันทึกเมทริกซ์ความคล้ายคลึงเป็นไฟล์ 'similarity.pkl'
with open('data/similarity.pkl', 'wb') as f:
    pickle.dump(similarity_matrix, f)

# โหลด DataFrame และเมทริกซ์ความคล้ายคลึง
music_df = pd.read_pickle('data/df.pkl')
with open('data/similarity.pkl', 'rb') as f:
    similarity_matrix = pickle.load(f)

# Initialize the Spotify client
client_credentials_manager = SpotifyClientCredentials(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET
)
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

# รายการเพลงสำหรับเลือก
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
