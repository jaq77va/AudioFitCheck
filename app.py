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

# --- CSS PERSONALIZZATO PER LA NUOVA UX MOBILE ---
st.markdown("""
    <style>
    /* 1. Sidebar fissa sempre visibile */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] {
            min-width: 260px !important;
            max-width: 80vw !important;
            transform: none !important;
            visibility: visible !important;
        }
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }

    /* 2. Stile unificato e gigante per i pulsanti principali */
    .stButton > button {
        width: 100% !important;
        height: 4rem !important;
        font-size: 1.15rem !important;
        font-weight: 600 !important;
        border-radius: 16px !important;
        border: 1px solid #e0e0e0 !important;
        background-color: #ffffff !important;
        color: #31333F !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* Evidenziazione per il tasto di invio finale */
    button[kind="primary"] {
        background-color: #ffffff !important;
        color: #ff4b4b !important;
        border: 2px solid #ff4b4b !important;
    }

    /* 3. Blocco widget audio pulito */
    [data-testid="stAudioInput"] {
        width: 100% !important;
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 16px;
        padding: 10px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    }
    
    [data-testid="stAudioInput"] button {
        border-radius: 12px !important;
        border: 1px solid #d0d5dd !important;
        background-color: #ffffff !important;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 4rem;
    }
    </style>
""", unsafe_allow_html=True)

# Inizializzazione della coda tracce audio
if "audio_tracks" not in st.session_state:
    st.session_state.audio_tracks = []

st.title("🎙️ Check-In Vocale Coach")

# --- SEZIONE: CONFIGURAZIONE REPORT (SIDEBAR FISSA) ---
with st.sidebar:
    st.header("⚙️ Configurazione Report")
    st.markdown("Seleziona i cluster da includere:")
    
    cluster_options = {
        "peso": "⚖️ Variazioni di Peso e Misure",
        "aderenza": "🎯 Aderenza a Dieta e Allenamento (%)",
        "recupero": "🔋 Recupero, Stress e Sonno",
        "criticita": "⚠️ Infortuni o Fastidi",
        "alimentazione": "🍎 Gestione Fame / Sgarri",
        "integrazione": "💊 Feedback Integrazione",
        "domande": "❓ Dubbi specifici del cliente",
        "bozza": "✍️ Bozza di Risposta per il Coach"
    }
    
    selected_clusters = []
    for key, label in cluster_options.items():
        default_val = True if key in ["peso", "aderenza", "recupero", "criticita", "bozza"] else False
        if st.checkbox(label, value=default_val, key=f"cluster_{key}"):
            selected_clusters.append(key)

st.markdown("---")

# --- SEZIONE 1: REGISTRAZIONE TRACCE AUDIO ---
st.subheader("1. Registrazione Tracce Audio")
st.caption("Tocca per registrare un nuovo vocale dal microfono.")

uploaded_audio = st.audio_input("Tasto per Start/Stop Registrazione Vocale")

if uploaded_audio is not None:
    audio_bytes = uploaded_audio.getvalue()
    track_id = len(st.session_state.audio_tracks) + 1
    track_name = f"Vocale #{track_id} ({len(audio_bytes) // 1024} KB)"
    
    if not st.session_state.audio_tracks or st.session_state.audio_tracks[-1]["bytes"] != audio_bytes:
        st.session_state.audio_tracks.append({
            "id": track_id,
            "name": track_name,
            "bytes": audio_bytes
        })
        st.success(f"Registrato: {track_name}")
        st.rerun()

st.markdown("---")

# --- SEZIONE: TRACCIA IN REGISTRAZIONE / ELENCO TRACCE IN CODA ---
st.subheader("📋 Elenco Registrazioni e Rimozione Tracce")

if st.session_state.audio_tracks:
    for i, track in enumerate(st.session_state.audio_tracks):
        st.write(f"**{track['name']}**")
        st.audio(track["bytes"], format="audio/wav")
        
        if st.button(f"🗑️ Rimuovi Traccia #{i+1}", key=f"del_{i}", type="secondary"):
            st.session_state.audio_tracks.pop(i)
            st.rerun()
        st.markdown("---")
else:
    st.info("Nessuna traccia registrata al momento.")

st.markdown("---")

# --- SEZIONE 2: GENERAZIONE ANALISI ---
st.subheader("2. Generazione Analisi")

process_enabled = len(st.session_state.audio_tracks) > 0 and len(selected_clusters) > 0

if st.button("🚀 Tasto per Sottomissione Tracce Audio", type="primary", disabled=not process_enabled):
    with st.spinner("L'IA sta elaborando le tracce audio..."):
        
        clusters_instructions = ""
        for idx, c in enumerate(selected_clusters, 1):
            if c == "peso":
                clusters_instructions += f"{idx}. **Peso e Misure**: Andamento del peso e variazioni.\n"
            elif c == "aderenza":
                clusters_instructions += f"{idx}. **Aderenza**: Rispetto di dieta e workout.\n"
            elif c == "recupero":
                clusters_instructions += f"{idx}. **Recupero e Sonno**: Livelli di stress ed energie.\n"
            elif c == "criticita":
                clusters_instructions += f"{idx}. **Criticità**: Infortuni o impedimenti.\n"
            elif c == "alimentazione":
                clusters_instructions += f"{idx}. **Alimentazione**: Problemi di digestione o gestione sgarri.\n"
            elif c == "integrazione":
                clusters_instructions += f"{idx}. **Integrazione**: Note sugli integratori.\n"
            elif c == "domande":
                clusters_instructions += f"{idx}. **Dubbi**: Domande specifiche del cliente.\n"
            elif c == "bozza":
                clusters_instructions += f"{idx}. **Bozza di Risposta**: Testo motivazionale pronto da inviare.\n"

        contents = [
            f"""
            Sei un assistente esperto per coach online di fitness. 
            Ascolta attentamente le tracce audio allegate e genera un report strutturato focalizzandoti sui seguenti cluster:
            
            {clusters_instructions}
            """
        ]
        
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

    st.success("Analisi completata!")
    st.markdown("---")
    st.subheader("📊 Report per il Coach")
    st.markdown(report_strutturato)
    
    if st.button("🔄 Pulisci e Nuovo Check-In"):
        st.session_state.audio_tracks = []
        st.rerun()
