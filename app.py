import streamlit as st
from google import genai
from google.genai import types

# Inizializzazione del client Google GenAI
client = genai.Client()

st.set_page_config(
    page_title="Check-In Audio Converter",
    page_icon="🎙️",
    layout="centered"
)

# --- CSS PERSONALIZZATO PER OTTIMIZZAZIONE MOBILE ---
# Ingrandiamo i pulsanti principali, i margini e i tocchi per smartphone
st.markdown("""
    <style>
    /* Pulsanti principali grandi (Full width e ad alto spessore) */
    .stButton > button {
        width: 100% !important;
        height: 3.5rem !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Miglioramento spaziatura e leggibilità mobile */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* Evidenziazione box audio */
    stAudio {
        width: 100% !important;
    }
    </style>
""", unsafe_allow_html=True)

# Inizializzazione della coda tracce audio nella sessione
if "audio_tracks" not in st.session_state:
    st.session_state.audio_tracks = []

st.title("🎙️ Check-In Vocale Coach")
st.markdown("Registra i vocali del cliente, seleziona i KPI di interesse e genera il report istantaneo.")

# --- SIDEBAR: CONFIGURAZIONE CLUSTER E KPI ---
with st.sidebar:
    st.header("⚙️ Configurazione Report")
    st.markdown("Seleziona quali informazioni l'IA deve estrarre e analizzare:")
    
    # Elenco dei cluster selezionabili
    cluster_options = {
        "peso": "⚖️ Variazioni di Peso e Misure",
        "aderenza": "🎯 Aderenza a Dieta e Allenamento (%)",
        "recupero": "🔋 Recupero, Stress e Qualità Sonno",
        "criticita": "⚠️ Infortuni, Fastidi o Problemi",
        "alimentazione": "🍎 Gestione Fame / Sgarri / Digestione",
        "integrazione": "💊 Feedback su Integrazione",
        "domande": "❓ Dubbi specifici posti dal cliente",
        "bozza": "✍️ Bozza di risposta pronta per il coach"
    }
    
    selected_clusters = []
    for key, label in cluster_options.items():
        # Di default selezioniamo i principali per comodità
        default_val = True if key in ["peso", "aderenza", "recupero", "criticita", "bozza"] else False
        if st.checkbox(label, value=default_val, key=f"cluster_{key}"):
            selected_clusters.append(key)

st.markdown("---")

# --- SEZIONE 1: RACCOLTA TRACCE (MOBILE FRIENDLY) ---
st.subheader("1. Registrazione Tracce")
st.caption("Tocca il microfono per registrare un vocale. Puoi aggiungerne quanti ne vuoi prima di inviare.")

uploaded_audio = st.audio_input("Registra vocale check-in")

if uploaded_audio is not None:
    audio_bytes = uploaded_audio.getvalue()
    track_id = len(st.session_state.audio_tracks) + 1
    track_name = f"Vocale #{track_id} ({len(audio_bytes) // 1024} KB)"
    
    # Evitiamo duplicati accidentali sullo stesso stream
    if not st.session_state.audio_tracks or st.session_state.audio_tracks[-1]["bytes"] != audio_bytes:
        st.session_state.audio_tracks.append({
            "id": track_id,
            "name": track_name,
            "bytes": audio_bytes
        })
        st.success(f"Registrato con successo: {track_name}")
        st.rerun()

# Visualizzazione della coda tracce con pulsanti di eliminazione ergonomici
if st.session_state.audio_tracks:
    st.markdown("### 📋 Tracce in Coda")
    for i, track in enumerate(st.session_state.audio_tracks):
        st.write(f"**{track['name']}**")
        st.audio(track["bytes"], format="audio/wav")
        # Pulsante elimina grandi per tap da mobile
        if st.button(f"🗑️ Elimina Vocale #{i+1}", key=f"del_{i}", type="secondary"):
            st.session_state.audio_tracks.pop(i)
            st.rerun()
        st.markdown("---")
else:
    st.info("Nessuna traccia in coda. Registra almeno un vocale per procedere.")

# --- SEZIONE 2: ELABORAZIONE FINALE ---
process_enabled = len(st.session_state.audio_tracks) > 0 and len(selected_clusters) > 0

st.subheader("2. Generazione Analisi")

if st.button("🚀 ELABORA CHECK-IN", type="primary", disabled=not process_enabled):
    with st.spinner("Elaborazione audio e IA in corso..."):
        
        # Costruiamo dinamicamente le istruzioni basate sui cluster scelti dal coach
        clusters_instructions = ""
        for idx, c in enumerate(selected_clusters, 1):
            if c == "peso":
                clusters_instructions += f"{idx}. **Peso e Misure**: Andamento del peso, variazioni e percezione corporea.\n"
            elif c == "aderenza":
                clusters_instructions += f"{idx}. **Aderenza**: Rispetto dei grammi della dieta e dei workout pianificati.\n"
            elif c == "recupero":
                clusters_instructions += f"{idx}. **Recupero e Sonno**: Livelli di stress, energie e ore di sonno.\n"
            elif c == "criticita":
                clusters_instructions += f"{idx}. **Criticità**: Dolori articolari, infortuni o impedimenti.\n"
            elif c == "alimentazione":
                clusters_instructions += f"{idx}. **Alimentazione**: Problemi di digestione, attacchi di fame o gestione sgarri.\n"
            elif c == "integrazione":
                clusters_instructions += f"{idx}. **Integrazione**: Note sull'assunzione di integratori.\n"
            elif c == "domande":
                clusters_instructions += f"{idx}. **Dubbi**: Domande specifiche fatte dal cliente a cui serve risposta.\n"
            elif c == "bozza":
                clusters_instructions += f"{idx}. **Bozza di Risposta**: Testo sintetico e motivazionale pronto da inviare al cliente via chat.\n"

        contents = [
            f"""
            Sei un assistente esperto per coach online di fitness. 
            Ascolta attentamente le tracce audio allegate inviate dal cliente e genera un report strutturato focalizzandoti ESCLUSIVAMENTE sui seguenti cluster richiesti dal coach:
            
            {clusters_instructions}
            
            Usa un linguaggio chiaro, professionale e orientato ai KPI pratici del fitness coaching.
            """
        ]
        
        # Aggiungiamo i file audio binari
        for track in st.session_state.audio_tracks:
            contents.append(
                types.Part.from_bytes(
                    data=track["bytes"],
                    mime_type="audio/wav",
                )
            )
        
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=contents,
        )
        
        report_strutturato = response.text

    st.success("Report generato con successo!")
    st.markdown("---")
    st.subheader("📊 Report per il Coach")
    st.markdown(report_strutturato)
    
    if st.button("🔄 Pulisci e Nuovo Check-In"):
        st.session_state.audio_tracks = []
        st.rerun()
