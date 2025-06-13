import re
from funcs.extraer_texto_pdf import extraer_texto_pdf

def detectar_personas_dni_matricula(path_pdf: str):
    texto = extraer_texto_pdf(path_pdf)

    # Regex para DNI y Matrícula
    regex_dni = r'([A-ZÁÉÍÓÚÑ]{2,}(?:\s+[A-ZÁÉÍÓÚÑ]{2,}){1,2})\s*,?\s*DNI\s*N[º°]?\s*(\d{1,3}(?:\.\d{3}){1,2})'
    regex_mat = r'([A-ZÁÉÍÓÚÑ]{2,}(?:\s+[A-ZÁÉÍÓÚÑ]{2,}){0,2})\s*,?\s*(?:abogado[a]?,?\s*)?inscripto[a]?\s+en\s+la\s+matr[ií]cula\s+N[º°]?\s*(\d{1,3}(?:\.\d{3}){1,2})'

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
