"""
Abre un archivo PDF, extrae todo su texto concatenado y luego lo normaliza al eliminar saltos de línea, convertirlos en espacios y colapsar múltiples espacios consecutivos, devolviendo una sola línea de texto limpia.
"""
import fitz  # PyMuPDF se usa en vez de PyPDF2 para extraer texto de PDF
import re

# Extración de texto de un PDF + normalización simple
def normalizacion_simple_pdf(path_pdf='ley.pdf'):
    texto = ''
    with fitz.open(path_pdf) as doc:
        for pagina in doc:
            texto += pagina.get_text()

    # Normalizar el texto: eliminar saltos de línea y espacios múltiples
    texto = texto.replace('\n', ' ').replace('\r', ' ')
    texto = re.sub(r'\s+', ' ', texto).strip()

    return texto

# Extración de texto de un PDF + normalización avanzada
def normalizacion_avanzada_pdf(path_pdf: str) -> str:
    """
    Extrae todo el texto de un PDF y luego aplica una normalización enfocada
    en facilitar la detección de DNI y matrículas.
    """
    # 1) Extracción básica de texto
    texto = ''
    with fitz.open(path_pdf) as doc:
        for pagina in doc:
            texto += pagina.get_text()

    # 2) Unificar sinónimos (case-insensitive)
    texto = re.sub(r'\bDocumento\b', 'DNI', texto, flags=re.IGNORECASE)
    texto = re.sub(r'\bMatr[ií]cula\b', 'MATRICULA', texto, flags=re.IGNORECASE)

    # 3) Eliminar 'N°', 'Nº', guiones o dos puntos solo si van delante de un dígito
    texto = re.sub(r'\bN[º°]?\s*[-:]?\s*(?=\d)', '', texto)

    # 4) Quitar separadores de miles (puntos o guiones entre dígitos)
    texto = re.sub(r'(?<=\d)[\.\-](?=\d)', '', texto)

    # 5) Colapsar cualquier whitespace a un solo espacio y recortar
    texto = re.sub(r'\s+', ' ', texto).strip()

    return texto