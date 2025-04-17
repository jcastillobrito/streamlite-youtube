# app.py
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import re
import os
import io

def format_time(seconds):
    """Formatea el tiempo en formato HH:MM:SS o segundos según corresponda"""
    if seconds >= 60:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{seconds:.2f} segundos"

def extract_video_id(youtube_url):
    """Extrae el ID del video de YouTube desde una URL"""
    # Patrón para URLs de YouTube completas
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, youtube_url)
    
    if match:
        return match.group(1)
    return youtube_url  # Si no coincide con el patrón, asumimos que ya es un ID

def get_transcript(video_id, languages=['es']):
    """Obtiene la transcripción del video y la devuelve como texto"""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        
        # Preparar el contenido para el archivo
        transcript_text = ""
        for line in transcript:
            start_seconds = line['start']
            time_format = format_time(start_seconds)
            
            transcript_text += f"{line['text']}\n"
            transcript_text += f"Start: {time_format}, Duration: {line['duration']}\n"
            transcript_text += "\n"
        
        return transcript_text
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def main():
    st.set_page_config(
        page_title="Transcriptor de YouTube",
        page_icon="📝",
        layout="centered"
    )
    
    st.title("📝 Transcriptor de YouTube")
    st.markdown("""
    Esta aplicación te permite obtener la transcripción de videos de YouTube y descargarla como archivo de texto.
    """)
    
    # Formulario de entrada
    youtube_url = st.text_input("URL del video o ID de YouTube:", placeholder="https://www.youtube.com/watch?v=...")
    
    # Opciones de idioma
    languages = {
        "Español": "es",
        "Inglés": "en",
        "Francés": "fr",
        "Alemán": "de",
        "Italiano": "it",
        "Portugués": "pt"
    }
    
    language = st.selectbox("Idioma de la transcripción:", list(languages.keys()))
    
    # Botón para obtener la transcripción
    if st.button("Obtener Transcripción"):
        if youtube_url:
            with st.spinner("Obteniendo transcripción..."):
                # Extraer el ID del video
                video_id = extract_video_id(youtube_url)
                
                if video_id:
                    # Obtener la transcripción
                    transcript_text = get_transcript(video_id, languages=[languages[language]])
                    
                    if transcript_text:
                        st.success("¡Transcripción obtenida con éxito!")
                        
                        # Mostrar una vista previa de la transcripción
                        with st.expander("Vista previa de la transcripción", expanded=True):
                            st.text_area("", transcript_text, height=250)
                        
                        # Botón para descargar la transcripción
                        transcript_file = io.BytesIO(transcript_text.encode())
                        st.download_button(
                            label="Descargar Transcripción",
                            data=transcript_file,
                            file_name=f"transcripcion_{video_id}.txt",
                            mime="text/plain"
                        )
                        
                        # Mostrar el video embebido
                        st.markdown(f"""
                        ### Video original:
                        <iframe width="100%" height="400" src="https://www.youtube.com/embed/{video_id}" 
                        frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; 
                        gyroscope; picture-in-picture" allowfullscreen></iframe>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("No se pudo obtener la transcripción. Asegúrate de que el video tenga subtítulos en el idioma seleccionado.")
                else:
                    st.error("URL o ID de video no válido.")
        else:
            st.warning("Por favor, introduce una URL de YouTube o un ID de video.")
    
    # Instrucciones
    st.markdown("""
    ---
    ### Instrucciones:
    1. Introduce la URL completa del video de YouTube o solo el ID del video (ej: dQw4w9WgXcQ)
    2. Selecciona el idioma de la transcripción
    3. Haz clic en "Obtener Transcripción"
    4. Descarga el archivo cuando esté listo
    
    **Nota:** El video debe tener subtítulos en el idioma seleccionado para que la transcripción funcione.
    """)

if __name__ == "__main__":
    main()