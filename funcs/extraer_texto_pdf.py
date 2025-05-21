import fitz  # PyMuPDF se usa en vez de PyPDF2 para extraer texto de PDF
import re
import unicodedata

def normalizar_texto(texto):
    """Normaliza el texto: minúsculas, elimina acentos y signos extraños."""
    # Pasamos todo a minúsculas
    texto = texto.lower()
    
    # Eliminar acentos y otros caracteres especiales
    texto = ''.join(c for c in unicodedata.normalize('NFKD', texto) if not unicodedata.combining(c))

    # Eliminar signos especiales (opcional, puedes personalizar esto)
    texto = re.sub(r'[^\w\s]', '', texto)
    
    # Eliminar saltos de línea y espacios múltiples
    texto = texto.replace('\n', ' ').replace('\r', ' ')
    texto = re.sub(r'\s+', ' ', texto).strip()

    return texto

def extraer_texto_pdf(path_pdf='ley.pdf'):
    texto_original = ''
    texto_normalizado = ''
    
    with fitz.open(path_pdf) as doc:
        for pagina in doc:
            texto = pagina.get_text()
            texto_original += texto
            texto_normalizado += normalizar_texto(texto)

    # Devolver tanto el texto original como el normalizado
    return texto_original, texto_normalizado
