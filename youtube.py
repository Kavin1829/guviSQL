import streamlit as st
import pandas as pd
import plotly.express as px
from googleapiclient.discovery import build
import mysql.connector


api_key = "AIzaSyCkglXpsoXo7QjsLDBAL8mzCfX4YZzpdtg"  
youtube = build('youtube', 'v3', developerKey=api_key)


def search_youtube(query):
    request = youtube.search().list(
        part="snippet",
        maxResults=5,
        q=query
    )
    response = request.execute()
    return response['items']


def create_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  
        database="youtube"
    )
    return connection


def store_results_in_db(results):
    connection = create_connection()
    cursor = connection.cursor()
    for item in results:
        title = item['snippet']['title']
        description = item['snippet']['description']
        channel_title = item['snippet']['channelTitle']
        cursor.execute("INSERT INTO youtube_Guvi (title, description, channel_title) VALUES (%s, %s, %s)",
                       (title, description, channel_title))
    connection.commit()
    cursor.close()
    connection.close()


def results_to_dataframe(results):
    data = []
    for item in results:
        title = item['snippet']['title']
        description = item['snippet']['description']
        channel_title = item['snippet']['channelTitle']
        video_id = item['id']['videoId']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        data.append([title, description, channel_title, video_url])
    df = pd.DataFrame(data, columns=["Title", "Description", "Channel", "URL"])
    return df


def create_bar_chart(df):
    
    channel_counts = df['Channel'].value_counts().reset_index()
    channel_counts.columns = ['Channel', 'Video Count']
    
    fig = px.bar(channel_counts, x='Channel', y='Video Count', title='Number of Videos per Channel')
    return fig


st.title("YouTube Search App")
query = st.text_input("Enter search query")

if st.button("Search"):
    if query:
        results = search_youtube(query)
        store_results_in_db(results)
        df = results_to_dataframe(results)

        for index, row in df.iterrows():
            st.subheader(row["Title"])
            st.write(f"Channel: {row['Channel']}")
            st.write(row["Description"])
            st.markdown(f"[Watch Video]({row['URL']})")

        
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download results as CSV",
            data=csv,
            file_name="youtube_search_results.csv",
            mime="text/csv"
        )

        
        fig = create_bar_chart(df)
        st.plotly_chart(fig)
    else:
        st.error("Please enter a search query")
