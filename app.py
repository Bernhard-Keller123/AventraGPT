import openai
import streamlit as st
import os
import json
import requests

# Setze deinen OpenAI API-Schlüssel hier ein
openai.api_key = os.getenv('OPENAI_API_KEY')

# Funktion zum Laden der Trainingsdaten von GitHub
def lade_trainingsdaten_von_github(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return []

# URL zur trainingsdaten.json in deinem GitHub-Repository
trainingsdaten_url = "https://raw.githubusercontent.com/Bernhard-Keller123/AventraGPT/main/trainingdata.json"

# Trainingsdaten laden
trainingsdaten = lade_trainingsdaten_von_github(trainingsdaten_url)
chat_history = [{"role": "system", "content": td} for td in trainingsdaten]

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
        antwort = response.choices[0].message['content'].strip()
        chat_history.append({"role": "assistant", "content": antwort})
        return antwort
    except openai.error.OpenAIError as e:
        if "quota" in str(e):
            return "Du hast dein aktuelles Nutzungslimit überschritten. Bitte überprüfe deinen Plan und deine Abrechnungsdetails unter https://platform.openai.com/account/usage."
        return str(e)

# Streamlit App
st.title("AventraGPT_Play")

# Eingabefeld für den Prompt
prompt = st.text_input("Du: ")

# Schaltfläche zum Senden des Prompts
if st.button("Senden"):
    if prompt:
        antwort = generiere_antwort(prompt)
        st.text_area("AventraGPT", value=antwort, height=200, max_chars=None)

# Anzeige des Gesprächsverlaufs
st.subheader("Gesprächsverlauf")
for eintrag in chat_history:
    if eintrag['role'] == 'user':
        st.write(f"Du: {eintrag['content']}")
    elif eintrag['role'] == 'assistant':
        st.write(f"AventraGPT: {eintrag['content']}")
    elif eintrag['role'] == 'system':
        st.write(f"System: {eintrag['content']}")
