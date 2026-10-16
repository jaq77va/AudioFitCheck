import streamlit as st
from google import genai
from google.genai import types

# Inizializzazione del client Google GenAI (legge automaticamente GEMINI_API_KEY)
client = genai.Client()

st.set_page_config(
    page_title="Check-In Audio Converter (Gemini Edition)",
    page_icon="🎙️",
    layout="centered"
)

# Inizializzazione della coda tracce audio nella sessione di Streamlit
if "audio_tracks" not in st.session_state:
    st.session_state.audio_tracks = []

st.title("🎙️ Check-In Audio-First Converter (Powered by Gemini)")
st.markdown("Raccogli i vocali del cliente ed elaborali in un sol colpo con l'intelligenza artificiale multimodale.")

# --- SEZIONE 1: RACCOLTA TRACCE ---
st.subheader("1. Raccolta Vocali della Settimana")
uploaded_audio = st.audio_input("Registra una traccia audio (o carica un file)")

if uploaded_audio is not None:
    audio_bytes = uploaded_audio.getvalue()
    track_id = len(st.session_state.audio_tracks) + 1
    track_name = f"Traccia #{track_id} ({len(audio_bytes) // 1024} KB)"
    
    if not st.session_state.audio_tracks or st.session_state.audio_tracks[-1]["bytes"] != audio_bytes:
        st.session_state.audio_tracks.append({
            "id": track_id,
            "name": track_name,
            "bytes": audio_bytes
        })
        st.success(f"Aggiunta: {track_name}")

if st.session_state.audio_tracks:
    st.markdown("---")
    st.write(f"**Tracce in coda pronte per l'invio ({len(st.session_state.audio_tracks)}):**")
    
    for i, track in enumerate(st.session_state.audio_tracks):
        cols = st.columns([3, 1])
        with cols[0]:
            st.audio(track["bytes"], format="audio/wav")
            st.caption(track["name"])
        with cols[1]:
            if st.button("Elimina", key=f"del_{i}", type="secondary"):
                st.session_state.audio_tracks.pop(i)
                st.rerun()
else:
    st.info("Nessuna traccia registrata. Registra almeno un vocale per abilitare l'elaborazione.")

st.markdown("---")

# --- SEZIONE 2: ELABORAZIONE FINALE CON GEMINI ---
st.subheader("2. Generazione Report")
process_enabled = len(st.session_state.audio_tracks) > 0

if st.button("🚀 Elabora Check-In con Gemini", type="primary", disabled=not process_enabled):
    with st.spinner("Gemini sta ascoltando e analizzando le tracce..."):
        
        # Prepariamo la lista dei contenuti da inviare a Gemini (Testo + Parti Audio)
        contents = [
            """
            Sei un assistente esperto per coach online di fitness e performance. 
            Ascolta attentamente le tracce audio allegate inviate dal cliente durante la settimana e sintetizzale in un report strutturato per il coach.
            
            Il report deve contenere chiaramente:
            1. **Peso attuale / Variazioni** (se menzionate)
            2. **Aderenza a dieta e allenamento** (feedback percentuale o qualitativo)
            3. **Recupero, Stress e Sonno** (livelli energetici dichiarati)
            4. **Criticità, infortuni o problemi riscontrati**
            5. **Richieste specifiche o dubbi posti dal cliente**
            6. **Bozza di risposta consigliata** (un breve testo che il coach può mandare al cliente per incoraggiarlo).
            """
        ]
        
        # Aggiungiamo ogni traccia audio direttamente come parte binaria
        for index, track in enumerate(st.session_state.audio_tracks):
            contents.append(
                types.Part.from_bytes(
                    data=track["bytes"],
                    mime_type="audio/wav",  # Streamlit produce generalmente wav o webm
                )
            )
        
        # Chiamata al modello Gemini (es. flash per la massima velocità ed efficienza)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
        )
        
        report_strutturato = response.text

    st.success("Analisi completata con successo!")
    st.subheader("📊 Report Strutturato per il Coach")
    st.markdown(report_strutturato)
    
    if st.button("Pulisci tutto e inizia nuovo check-in"):
        st.session_state.audio_tracks = []
        st.rerun()