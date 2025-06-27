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

def eliminar_puntos_antes_de_cuit(texto: str) -> str:
    """
    Elimina los puntos que estén entre caracteres alfanuméricos en las
    dos palabras inmediatamente anteriores a la palabra 'CUIT',
    respetando cualquier coma o espacio que las separe del resto.
    """
    # Captura dos "palabras" antes de ", CUIT"
    patrón = re.compile(
        r'(\b[\w\.]+)\s+([\w\.]+)(?=\s*,\s*CUIT\b)',
        flags=re.IGNORECASE
    )

    def _repl(match: re.Match) -> str:
        w1, w2 = match.group(1), match.group(2)
        # Solo quitamos puntos que estén entre letras/dígitos
        w1_clean = re.sub(r'(?<=\w)\.(?=\w)', '', w1)
        w2_clean = re.sub(r'(?<=\w)\.(?=\w)', '', w2)
        return f"{w1_clean} {w2_clean}"

    return patrón.sub(_repl, texto)

# Extración de texto de un PDF + normalización avanzada
def normalizacion_avanzada_pdf(path_pdf: str = None, raw_text: str = None) -> str:
    """
    Extrae todo el texto de un PDF y luego aplica una normalización enfocada
    en facilitar la detección de DNI y matrículas.
    """
    # 1) Obtener texto: o bien del PDF, o bien usar el raw_text
    # 1.1) Detectamos si es un texto plano
    if raw_text is not None:
        texto = raw_text
    elif path_pdf:
        # 1.2) Detectamos si es un .pdf, en ese caso, realizamos la extracción básica de texto del PDF
        texto = ''
        with fitz.open(path_pdf) as doc:
            for pagina in doc:
                texto += pagina.get_text()
    else:
        raise ValueError("Debe proporcionarse 'path_pdf' o 'raw_text'")

    # 2) Unificar sinónimos (case-insensitive), de forma más genérica
    # — Primero cubrimos “Documento” → “DNI”
    texto = re.sub(r'\bDocumento\b', 'DNI', texto, flags=re.IGNORECASE)
    # — Variantes de “D.N.I.”, “DN-I”, “DNI” con puntos/guiones/espacios entre letras → “DNI”
    texto = re.sub(r'\bD[\W_]*N[\W_]*I\b', 'DNI', texto, flags=re.IGNORECASE)

    # — Primero cubrimos “Matrícula” con o sin acento → “MATRICULA”
    texto = re.sub(r'\bMatr[ií]cula\b', 'MATRICULA', texto, flags=re.IGNORECASE)
    # — Variantes de “M.P.”, “M-P-”, “MP” con puntos/guiones/espacios entre letras → “MATRICULA”
    texto = re.sub(r'\bM[\W_]*P\b', 'MATRICULA', texto, flags=re.IGNORECASE)

    # 3) Eliminar 'N°', 'Nº', guiones o dos puntos solo si van delante de un dígito
    texto = re.sub(r'\bN[º°]?\s*[-:]?\s*(?=\d)', '', texto)

    # 3.1) Asegurar siempre un espacio entre etiqueta y número,
    #      eliminando cualquier caracter no alfanumérico que pueda quedar pegado
    texto = re.sub(
        r'\b(DNI|MATRICULA)[^\w]*(\d+)\b',
        r'\1 \2',
        texto,
        flags=re.IGNORECASE
    )

    # 4) Quitar separadores de miles (puntos o guiones entre dígitos)
    texto = re.sub(r'(?<=\d)[\.\-](?=\d)', '', texto)

    # 5) Eliminar puntos entre letras (Ej, S.R.L. -> SRL.)
    texto = eliminar_puntos_antes_de_cuit(texto)

    # 6) Colapsar cualquier whitespace a un solo espacio y recortar
    texto = re.sub(r'\s+', ' ', texto).strip()

    return texto