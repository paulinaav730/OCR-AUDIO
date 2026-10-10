
import os
import io
import asyncio
import streamlit as st
import cv2
import numpy as np
import pytesseract

from PIL import Image, ImageOps, ImageEnhance
from googletrans import Translator
from gtts import gTTS

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title="OCR Audio | Lee y escucha",
    page_icon="📖",
    layout="wide"
)

# =====================================================
# ESTILOS
# =====================================================

st.markdown("""
<style>
.stApp {
    background-color: #FFF8F0;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.hero {
    background: linear-gradient(135deg, #FFB477, #F07836);
    padding: 35px 25px;
    border-radius: 24px;
    text-align: center;
    margin-bottom: 25px;
}

.hero h1 {
    color: white;
    font-size: 42px;
    margin-bottom: 8px;
}

.hero p {
    color: white;
    font-size: 18px;
    margin: 0;
}

h2, h3 {
    color: #8C451D;
}

div.stButton > button {
    background: #F07836;
    color: white;
    border: none;
    border-radius: 12px;
    min-height: 45px;
    font-weight: 600;
}

div.stButton > button:hover {
    background: #D95D23;
    color: white;
}

[data-testid="stSidebar"] {
    background-color: #FFF0E2;
}

.card {
    background-color: white;
    border: 1px solid #F0D8C5;
    border-radius: 16px;
    padding: 18px;
    margin: 10px 0;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# IDIOMAS
# =====================================================

IDIOMAS = {
    "Español": {"codigo": "es", "ocr": "spa", "voz": "es"},
    "Inglés": {"codigo": "en", "ocr": "eng", "voz": "en"},
    "Francés": {"codigo": "fr", "ocr": "fra", "voz": "fr"},
    "Portugués": {"codigo": "pt", "ocr": "por", "voz": "pt"},
    "Italiano": {"codigo": "it", "ocr": "ita", "voz": "it"},
    "Alemán": {"codigo": "de", "ocr": "deu", "voz": "de"},
    "Coreano": {"codigo": "ko", "ocr": "kor", "voz": "ko"},
    "Japonés": {"codigo": "ja", "ocr": "jpn", "voz": "ja"},
    "Mandarín": {"codigo": "zh-cn", "ocr": "chi_sim", "voz": "zh-cn"},
    "Bengalí": {"codigo": "bn", "ocr": "ben", "voz": "bn"},
    "Árabe": {"codigo": "ar", "ocr": "ara", "voz": "ar"},
    "Hindi": {"codigo": "hi", "ocr": "hin", "voz": "hi"},
}

# =====================================================
# FUNCIONES
# =====================================================

def preparar_imagen(imagen, aplicar_filtro=False):
    """Prepara la imagen para mejorar la lectura OCR."""

    imagen = ImageOps.exif_transpose(imagen).convert("RGB")

    if aplicar_filtro:
        gris = ImageOps.grayscale(imagen)
        gris = ImageEnhance.Contrast(gris).enhance(2.0)
        gris = gris.point(
            lambda pixel: 255 if pixel > 150 else 0
        )
        imagen = gris.convert("RGB")

    return imagen


def extraer_texto(imagen, idioma_ocr):
    """Extrae texto de una imagen con Tesseract."""

    imagen_cv = cv2.cvtColor(
        np.array(imagen),
        cv2.COLOR_RGB2BGR
    )

    texto = pytesseract.image_to_string(
        imagen_cv,
        lang=idioma_ocr
    )

    return texto.strip()


def traducir_texto(texto, origen, destino):
    """Ejecuta la traducción con googletrans 4.0.2."""

    async def ejecutar():
        async with Translator() as traductor:
            resultado = await traductor.translate(
                texto,
                src=IDIOMAS[origen]["codigo"],
                dest=IDIOMAS[destino]["codigo"]
            )
            return resultado.text

    return asyncio.run(ejecutar())


def generar_audio(texto, idioma, acento="Predeterminado"):
    """Convierte texto a voz y devuelve el audio MP3."""

    dominios = {
        "Predeterminado": "com",
        "Estados Unidos": "com",
        "Reino Unido": "co.uk",
        "Australia": "com.au",
        "Canadá": "ca",
        "India": "co.in",
        "Irlanda": "ie",
        "Sudáfrica": "co.za"
    }

    os.makedirs("temp", exist_ok=True)

    ruta_audio = "temp/lectura.mp3"

    tts = gTTS(
        text=texto,
        lang=IDIOMAS[idioma]["voz"],
        tld=dominios.get(acento, "com"),
        slow=False
    )

    tts.save(ruta_audio)

    with open(ruta_audio, "rb") as archivo:
        return archivo.read()


# =====================================================
# ESTADO DE LA APLICACIÓN
# =====================================================

if "texto_ocr" not in st.session_state:
    st.session_state["texto_ocr"] = ""

if "texto_traducido" not in st.session_state:
    st.session_state["texto_traducido"] = ""

if "imagen_procesada" not in st.session_state:
    st.session_state["imagen_procesada"] = None

# =====================================================
# BARRA LATERAL
# =====================================================

with st.sidebar:
    st.title("📖 OCR Audio")

    st.write("Convierte imágenes en texto, traducciones y audio.")

    st.markdown("---")
    st.subheader("¿Cómo funciona?")

    st.write("1. Carga una imagen o toma una foto.")
    st.write("2. Extrae el texto con OCR.")
    st.write("3. Revisa y corrige el resultado.")
    st.write("4. Traduce a otro idioma.")
    st.write("5. Escucha o descarga el audio.")

    st.markdown("---")
    st.caption("Proyecto de procesamiento de lenguaje natural.")

# =====================================================
# ENCABEZADO
# =====================================================

st.markdown("""
<div class="hero">
    <h1>📖 OCR Audio</h1>
    <p>De una imagen a palabras que puedes escuchar.</p>
</div>
""", unsafe_allow_html=True)

st.write(
    "Carga un documento, una fotografía, un apunte o una imagen "
    "con texto. La aplicación lo reconocerá para que puedas editarlo, "
    "traducirlo y escucharlo."
)

# =====================================================
# CARGA DE IMAGEN
# =====================================================

st.markdown("---")
st.subheader("📷 1. Selecciona tu imagen")

modo = st.radio(
    "¿Cómo quieres agregar la imagen?",
    ["Cargar archivo", "Usar cámara"],
    horizontal=True
)

imagen_original = None

if modo == "Cargar archivo":

    archivo = st.file_uploader(
        "Sube una imagen",
        type=["png", "jpg", "jpeg", "webp"],
        help="Usa una imagen clara y con texto legible."
    )

    if archivo is not None:
        try:
            imagen_original = Image.open(
                io.BytesIO(archivo.getvalue())
            )
        except Exception:
            st.error("No fue posible abrir la imagen.")

else:
    foto = st.camera_input("Toma una foto del texto")

    if foto is not None:
        try:
            imagen_original = Image.open(
                io.BytesIO(foto.getvalue())
            )
        except Exception:
            st.error("No fue posible abrir la fotografía.")

if imagen_original is not None:

    col_imagen, col_opciones = st.columns([3, 2])

    with col_imagen:
        st.image(
            imagen_original,
            caption="Imagen original",
            use_container_width=True
        )

    with col_opciones:
        st.markdown("#### Ajustes de imagen")

        aplicar_filtro = st.checkbox(
            "Mejorar contraste para OCR",
            value=True
        )

        idioma_ocr = st.selectbox(
            "Idioma del texto de la imagen",
            list(IDIOMAS.keys()),
            index=0
        )

        imagen_preparada = preparar_imagen(
            imagen_original,
            aplicar_filtro
        )

        st.image(
            imagen_preparada,
            caption="Imagen preparada para reconocimiento",
            use_container_width=True
        )

    if st.button("🔎 Extraer texto de la imagen"):

        try:
            with st.spinner("Reconociendo el texto..."):

                texto_extraido = extraer_texto(
                    imagen_preparada,
                    IDIOMAS[idioma_ocr]["ocr"]
                )

            if texto_extraido:
                st.session_state["texto_ocr"] = texto_extraido
                st.session_state["texto_traducido"] = ""
                st.session_state["imagen_procesada"] = (
                    imagen_preparada
                )
                st.success("¡Texto reconocido correctamente!")
                st.rerun()

            else:
                st.warning(
                    "No encontramos texto. Prueba con una imagen "
                    "más nítida o desactiva el filtro."
                )

        except Exception as error:
            st.error(
                "No se pudo reconocer el texto. Comprueba que "
                "Tesseract esté instalado y que el idioma OCR "
                "esté disponible."
            )
            st.caption(f"Detalle técnico: {error}")

# =====================================================
# TEXTO EXTRAÍDO
# =====================================================

st.markdown("---")
st.subheader("📝 2. Revisa el texto reconocido")

texto_editado = st.text_area(
    "Puedes corregir el texto antes de continuar:",
    key="texto_ocr",
    height=200,
    placeholder="El texto extraído aparecerá aquí..."
)

if st.button("🧹 Limpiar texto"):
    st.session_state["texto_ocr"] = ""
    st.session_state["texto_traducido"] = ""
    st.rerun()

# =====================================================
# TRADUCCIÓN
# =====================================================

st.markdown("---")
st.subheader("🌎 3. Traduce el texto")

col_origen, col_destino = st.columns(2)

with col_origen:
    idioma_origen = st.selectbox(
        "Idioma original del texto",
        list(IDIOMAS.keys()),
        index=0,
        key="idioma_origen"
    )

with col_destino:
    idiomas_destino = [
        idioma for idioma in IDIOMAS
        if idioma != idioma_origen
    ]

    idioma_destino = st.selectbox(
        "Traducir al idioma",
        idiomas_destino,
        index=0,
        key="idioma_destino"
    )

if st.button("🌐 Traducir texto"):

    if not texto_editado.strip():
        st.warning("Primero extrae o escribe algún texto.")

    else:
        try:
            with st.spinner("Traduciendo..."):

                resultado_traduccion = traducir_texto(
                    texto_editado.strip(),
                    idioma_origen,
                    idioma_destino
                )

            st.session_state["texto_traducido"] = (
                resultado_traduccion
            )

            st.success("¡Traducción completada!")

        except Exception as error:
            st.error(
                "No fue posible traducir. Comprueba tu conexión "
                "a internet e inténtalo de nuevo."
            )
            st.caption(f"Detalle técnico: {error}")

if st.session_state["texto_traducido"]:

    st.text_area(
        "Resultado de la traducción:",
        key="resultado_visible",
        value=st.session_state["texto_traducido"],
        height=160,
        disabled=True
    )

# =====================================================
# TEXTO A VOZ
# =====================================================

st.markdown("---")
st.subheader("🔊 4. Escucha el texto")

opcion_audio = st.radio(
    "¿Qué quieres escuchar?",
    ["Texto original", "Texto traducido"],
    horizontal=True
)

if opcion_audio == "Texto original":
    texto_audio = texto_editado
    idioma_audio = idioma_origen
else:
    texto_audio = st.session_state["texto_traducido"]
    idioma_audio = idioma_destino

acento = st.selectbox(
    "Acento de voz (principalmente para inglés)",
    [
        "Predeterminado",
        "Estados Unidos",
        "Reino Unido",
        "Australia",
        "Canadá",
        "India",
        "Irlanda",
        "Sudáfrica"
    ]
)

if st.button("🎧 Generar audio"):

    if not texto_audio.strip():
        st.warning(
            "No hay texto disponible para convertir en audio."
        )

    else:
        try:
            with st.spinner("Generando audio..."):

                audio_bytes = generar_audio(
                    texto_audio.strip(),
                    idioma_audio,
                    acento
                )

            st.success("¡Audio generado!")

            st.audio(
                audio_bytes,
                format="audio/mp3"
            )

            st.download_button(
                "⬇️ Descargar audio MP3",
                data=audio_bytes,
                file_name="ocr_audio.mp3",
                mime="audio/mpeg"
            )

        except Exception as error:
            st.error(
                "No se pudo generar el audio. Comprueba tu "
                "conexión y que el idioma esté soportado por gTTS."
            )
            st.caption(f"Detalle técnico: {error}")

# =====================================================
# PIE DE PÁGINA
# =====================================================

st.markdown("---")

st.markdown("""
<div style="text-align:center; padding:20px; color:#8C451D;">
    <strong>OCR Audio 📖</strong>
    <p>Leer, traducir y escuchar. Tecnología para todos.</p>
</div>
""", unsafe_allow_html=True)
