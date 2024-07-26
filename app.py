import openai
import streamlit as st
import json
import chardet
import requests

# Setze deinen OpenAI API-Schlüssel hier ein
openai.api_key = os.getenv('OPENAI_API_KEY')

# GitHub URL zum Trainingsdaten-JSON
GITHUB_JSON_URL = 'https://raw.githubusercontent.com/Bernhard-Keller123/AventraGPT/main/trainingdata.json'

# Funktion zum Laden der Trainingsdaten aus der GitHub-Datei
def lade_default_trainingsdaten():
    try:
        response = requests.get(GITHUB_JSON_URL)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.json()
    except requests.RequestException as e:
        st.error(f"Fehler beim Laden der Standard-Trainingsdaten: {e}")
        return []

# Funktion zum Speichern der Trainingsdaten in eine Datei
def speichere_trainingsdaten_in_datei(trainingsdaten, dateipfad):
    with open(dateipfad, 'w', encoding='utf-8') as file:
        json.dump(trainingsdaten, file, ensure_ascii=False, indent=4)

# Initialisieren der Trainingsdaten und des Gesprächsverlaufs
if 'trainingsdaten' not in st.session_state:
    st.session_state['trainingsdaten'] = lade_default_trainingsdaten()
    st.session_state['chat_history'] = [{"role": "system", "content": json.dumps(td, ensure_ascii=False, indent=4)} for td in st.session_state['trainingsdaten']]

def generiere_antwort(prompt):
    chat_history = st.session_state['chat_history']
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
        st.session_state['chat_history'] = chat_history
        return antwort
    except openai.error.OpenAIError as e:
        if "quota" in str(e):
            return "Du hast dein aktuelles Nutzungslimit überschritten. Bitte überprüfe deinen Plan und deine Abrechnungsdetails unter https://platform.openai.com/account/usage."
        return str(e)

def lade_trainingsdaten(uploaded_file):
    if uploaded_file is not None:
        try:
            # Versuche, die Datei zu lesen und die Kodierung zu erkennen
            raw_data = uploaded_file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            training_data = raw_data.decode(encoding)

            st.session_state['trainingsdaten'].append(training_data)
            speichere_trainingsdaten_in_datei(st.session_state['trainingsdaten'], 'trainingsdaten.json')
            st.session_state['chat_history'].append({"role": "system", "content": training_data})
            return "Trainingsdaten erfolgreich geladen."
        except Exception as e:
            return f"Fehler beim Laden der Datei: {e}"

# Streamlit App
st.title("AventraGPT_Play")

# Eingabefeld für den Prompt
prompt = st.text_input("Du: ")

# Schaltfläche zum Senden des Prompts
if st.button("Senden"):
    if prompt:
        antwort = generiere_antwort(prompt)
        st.text_area("AventraGPT", value=antwort, height=200, max_chars=None)

# Datei-Upload für Trainingsdaten
uploaded_file = st.file_uploader("Trainingsdaten hochladen", type=["txt"])

# Schaltfläche zum Laden der Trainingsdaten
if st.button("Trainingsdaten laden"):
    if uploaded_file:
        meldung = lade_trainingsdaten(uploaded_file)
        st.write(meldung)

# Anzeige des Gesprächsverlaufs
st.subheader("Gesprächsverlauf")
for eintrag in st.session_state['chat_history']:
    if eintrag['role'] == 'user':
        st.write(f"Du: {eintrag['content']}")
    elif eintrag['role'] == 'assistant':
        st.write(f"AventraGPT: {eintrag['content']}")
    elif eintrag['role'] == 'system':
        st.write(f"System: {eintrag['content']}")
