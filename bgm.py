import streamlit as st

def play_bgm_in_sidebar():
    # bgmフォルダ内のmp3ファイルを読み込む
    audio_file = open('bgm/pokemongym.mp3', 'rb')
    audio_bytes = audio_file.read()

    # Streamlitのサイドバー内で音声を再生
    st.sidebar.audio(audio_bytes, format='audio/mp3', loop=True)