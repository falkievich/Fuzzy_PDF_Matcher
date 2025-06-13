import re
from funcs.extraer_texto_pdf import extraer_texto_pdf

def detectar_personas_dni_matricula(path_pdf: str):
    texto = extraer_texto_pdf(path_pdf)

    # Regex para DNI y Matrícula
    regex_dni = r'([A-ZÁÉÍÓÚÑ]{2,}(?:\s+[A-ZÁÉÍÓÚÑ]{2,}){1,2})\s*,?\s*D\.?\s*N\.?\s*I\.?\s*(?:[º°])?\s*(\d{1,3}(?:\.\d{3}){0,2}|\d+)'
    regex_mat = (
        r'([A-ZÁÉÍÓÚÑ]{2,}(?:\s+[A-ZÁÉÍÓÚÑ]{2,}){0,2})'     # Nombre/apellido 1 a 3 palabras
        r'\s*,?\s*'                                        # Coma opcional y espacios
        r'(?:.*?\babogado[a]?\b.*?,?\s*)?'                 # Opcional: "abogado" o "abogada" en cualquier parte, con texto antes/después
        r'(?:de|con|en)?\s*matr[ií]cula\b'                 # "de matrícula", "con matrícula" o "en matrícula"
        r'(?:\s*N[º°]?)?\s*'                               # Opcional: N°, Nº, etc.
        r'([A-Z0-9\.\-]{3,})'                              # Matrícula alfanumérica (mínimo 3 caracteres)
    )

    personas = {}

    # Detectar nombres + DNI
    for nombre, dni in re.findall(regex_dni, texto):
        clave = f"DNI N° {dni}"
        if clave not in personas:
            personas[clave] = nombre.strip().title()

    # Detectar nombres + Matrícula
    for nombre, matricula in re.findall(regex_mat, texto):
        clave = f"Matrícula N° {matricula}"
        if clave not in personas:
            personas[clave] = nombre.strip().title()

    # Resultado final
    resultado = [f"{nombre} | {clave}" for clave, nombre in personas.items()]

    return resultado
