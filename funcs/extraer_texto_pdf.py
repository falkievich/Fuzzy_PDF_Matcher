"""
Abre un archivo PDF, extrae todo su texto concatenado y luego lo normaliza al eliminar saltos de línea, convertirlos en espacios y colapsar múltiples espacios consecutivos, devolviendo una sola línea de texto limpia.
"""
import fitz  # PyMuPDF se usa en vez de PyPDF2 para extraer texto de PDF
import re

def extraer_texto_pdf(path_pdf='ley.pdf'):
    texto = ''
    with fitz.open(path_pdf) as doc:
        for pagina in doc:
            texto += pagina.get_text()

    # Normalizar el texto: eliminar saltos de línea y espacios múltiples
    texto = texto.replace('\n', ' ').replace('\r', ' ')
    texto = re.sub(r'\s+', ' ', texto).strip()

    return texto
