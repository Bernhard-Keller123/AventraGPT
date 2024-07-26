import openai
import streamlit as st
import os
import json
import requests

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Function to load training data from GitHub
def lade_trainingsdaten_von_github(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return []

# URL to trainingsdaten.json in your GitHub repository
trainingsdaten_url = "https://raw.githubusercontent.com/Bernhard-Keller123/AventraGPT/main/trainingdata.json"

# Load training data
trainingsdaten = lade_trainingsdaten_von_github(trainingsdaten_url)
chat_history = [{"role": "system", "content": json.dumps(trainingsdaten)}]

def generiere_antwort(prompt):
    chat_history.append({"role": "user", "content": prompt})
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=chat_history,
            max_tokens=600,
            n=1,
            stop=None,
            temperature=0.7
        )
        st.write(response)  # Print the response to debug
        antwort = response.choices[0].message['content'].strip()
        chat_history.append({"role": "assistant", "content": antwort})
        return antwort
    except openai.error.OpenAIError as e:
        st.error(f"OpenAI API Error: {e}")
        return "There was an issue with the OpenAI API."
    except Exception as e:
        st.error(f"Unexpected Error: {e}")
        return "An unexpected error occurred."

# Streamlit App
st.title("AventraGPT_Play")

# Input field for the prompt
prompt = st.text_input("Du: ")

# Button to send the prompt
if st.button("Senden"):
    if prompt:
        antwort = generiere_antwort(prompt)
        st.text_area("AventraGPT", value=antwort, height=200, max_chars=None)

# Display chat history
st.subheader("Gesprächsverlauf")
for eintrag in chat_history:
    if eintrag['role'] == 'user':
        st.write(f"Du: {eintrag['content']}")
    elif eintrag['role'] == 'assistant':
        st.write(f"AventraGPT: {eintrag['content']}")
    elif eintrag['role'] == 'system':
        st.write(f"System: {eintrag['content']}")
