from textblob import TextBlob
import streamlit as st
from PIL import Image
from googletrans import Translator

# ── Estilos ────────────────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background-color: #fffde7; color: #333333; }

div.stButton > button {
    background-color: #f9a825;
    color: white;
    border-radius: 10px;
    padding: 10px 24px;
    border: none;
    font-size: 16px;
    transition: background-color 0.3s ease;
}
div.stButton > button:hover { background-color: #f57f17; color: white; }
section[data-testid="stSidebar"] { background-color: #fff9c4; }
h1, h2, h3 { color: #f57f17; }

/* Tarjeta de resultado */
.resultado {
    background-color: #fff8e1;
    border-left: 5px solid #f9a825;
    border-radius: 10px;
    padding: 20px;
    margin: 12px 0;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# ── Encabezado ─────────────────────────────────────────────────────
st.title("😊 Análisis de Sentimiento")

try:
    image = Image.open('emojis.png')
    st.image(image, use_container_width=True)
except:
    st.info("📷 Imagen no encontrada.")

st.subheader("Escribe una frase y descubre qué sentimiento expresa")

# ── Sidebar ────────────────────────────────────────────────────────
with st.sidebar:
    st.title("📖 ¿Cómo funciona?")
    st.markdown("""
    **Polaridad** — indica si el sentimiento es positivo, negativo o neutral.
    - `-1` = muy negativo
    - `0` = neutral
    - `+1` = muy positivo

    ---

    **Subjetividad** — mide cuánto del texto es opinión vs. hecho.
    - `0` = completamente objetivo
    - `1` = completamente subjetivo

    ---
    📝 El texto se traduce al inglés automáticamente antes del análisis,
    ya que TextBlob trabaja mejor en ese idioma.
    """)

# ── Traductor ──────────────────────────────────────────────────────
translator = Translator()

# ── Historial en session_state ─────────────────────────────────────
if "historial" not in st.session_state:
    st.session_state.historial = []

# ── Entrada de texto ───────────────────────────────────────────────
st.markdown("### ✏️ Ingresa tu texto")
text = st.text_area("Escribe la frase a analizar:", height=100)

if st.button("🔍 Analizar sentimiento"):
    if not text.strip():
        st.warning("⚠️ Por favor escribe alguna frase primero.")
    else:
        with st.spinner("Analizando..."):
            translation = translator.translate(text, src="es", dest="en")
            trans_text = translation.text
            blob = TextBlob(trans_text)
            polaridad   = round(blob.sentiment.polarity, 2)
            subjetividad = round(blob.sentiment.subjectivity, 2)

        # Determinar sentimiento
        if polaridad > 0:
            sentimiento = "Positivo 😊"
            color = "success"
        elif polaridad < 0:
            sentimiento = "Negativo 😔"
            color = "error"
        else:
            sentimiento = "Neutral 😐"
            color = "info"

        # Mostrar resultado
        st.markdown("---")
        st.markdown("### 📊 Resultado")
        getattr(st, color)(f"**Sentimiento: {sentimiento}**")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("🎭 Polaridad",    polaridad,
                      delta="positivo" if polaridad > 0 else "negativo" if polaridad < 0 else "neutral")
        with col2:
            st.metric("🧠 Subjetividad", subjetividad)

        # Barra visual de polaridad
        st.markdown("**Escala de polaridad** (−1 negativo → +1 positivo)")
        progreso = int((polaridad + 1) / 2 * 100)  # convierte -1..1 a 0..100
        st.progress(progreso)

        # Barra visual de subjetividad
        st.markdown("**Escala de subjetividad** (0 objetivo → 1 subjetivo)")
        st.progress(int(subjetividad * 100))

        # Traducción mostrada
        with st.expander("🔤 Ver traducción al inglés"):
            st.write(trans_text)

        # Guardar en historial
        st.session_state.historial.append({
            "Frase": text,
            "Polaridad": polaridad,
            "Subjetividad": subjetividad,
            "Sentimiento": sentimiento
        })

# ── Historial ──────────────────────────────────────────────────────
if st.session_state.historial:
    st.markdown("---")
    st.markdown("### 🕓 Historial de análisis")
    import pandas as pd
    df = pd.DataFrame(st.session_state.historial)
    st.dataframe(df, use_container_width=True)

    if st.button("🗑️ Limpiar historial"):
        st.session_state.historial = []
        st.rerun()
