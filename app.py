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

# --- CSS PERSONALIZZATO PER UX MOBILE AVANZATA ---
st.markdown("""
    <style>
    /* 1. Forza la Sidebar a rimanere visibile e fissa anche su schermi stretti (mobile) */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] {
            min-width: 260px !important;
            max-width: 80vw !important;
            transform: none !important;
            visibility: visible !important;
        }
        /* Spinge il contenuto principale per fare spazio alla sidebar fissa */
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }

    /* 2. Ingrandimento drastico dei pulsanti (Rec, Invio, Elimina) per facilitare il tap da mobile */
    .stButton > button {
        width: 100% !important;
        height: 4rem !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        border-radius: 16px !important;
        margin-top: 0.75rem !important;
        margin-bottom: 0.75rem !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* Evidenziazione speciale per il tasto di elaborazione principale */
    button[kind="primary"] {
        background-color: #ff4b4b !important;
        color: white !important;
    }

    /* Spaziatura generale ottimizzata per pollici */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 4rem;
    }
    </style>
""", unsafe_allow_html=True)

# Inizializzazione della coda tracce audio nella sessione
if "audio_tracks" not in st.session_state:
    st.session_state.audio_tracks = []

st.title("🎙️ Check-In Vocale Coach")
st.markdown("Gestisci i check-in dei tuoi clienti in pochi secondi da mobile.")

# --- SIDEBAR FISSA PER CLUSTER E KPI ---
with st.sidebar:
    st.header("⚙️ Configurazione Report")
    st.markdown("Seleziona i cluster da includere nell'analisi:")
    
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

# --- SEZIONE 1: RACCOLTA TRACCE (PULSANTI EXTRA-LARGE) ---
st.subheader("1. Registrazione Tracce Audio")
st.caption("Usa il registratore qui sotto per catturare il vocale del cliente.")

# Widget di registrazione audio nativo
uploaded_audio = st.audio_input("Tocca per registrare")

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

# Visualizzazione della coda tracce con pulsanti di eliminazione grandi
if st.session_state.audio_tracks:
    st.markdown("### 📋 Tracce in Coda")
    for i, track in enumerate(st.session_state.audio_tracks):
        st.write(f"**{track['name']}**")
        st.audio(track["bytes"], format="audio/wav")
        
        # Pulsante Elimina ingrandito per smartphone
        if st.button(f"🗑️ Elimina Vocale #{i+1}", key=f"del_{i}", type="secondary"):
            st.session_state.audio_tracks.pop(i)
            st.rerun()
        st.markdown("---")
else:
    st.info("Nessuna traccia registrata. Registra almeno un vocale per abilitare l'invio.")

# --- SEZIONE 2: ELABORAZIONE FINALE ---
process_enabled = len(st.session_state.audio_tracks) > 0 and len(selected_clusters) > 0

st.subheader("2. Generazione Analisi")

# Pulsante principale grande (full-width grazie al CSS)
if st.button("🚀 ELABORA CHECK-IN COMPLETO", type="primary", disabled=not process_enabled):
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
