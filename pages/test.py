import streamlit as st

# Set the title of the Streamlit app
st.title("Embedding Another Streamlit App")

# URL of the public Streamlit app you want to embed
app_url = "https://rainfall-prediction-app-volkan-ai.streamlit.app/"

# Embed the Streamlit app using an iframe
st.components.v1.iframe(app_url, width=700, height=1000, scrolling=True)
