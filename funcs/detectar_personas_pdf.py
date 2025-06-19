import re
from funcs.extraer_texto_pdf import normalizacion_avanzada_pdf

def detectar_personas_dni_matricula(path_pdf: str):
    """
    Extrae y normaliza el texto de un PDF (normalizacion_avanzada_pdf), luego detecta pares
    Nombre + DNI y Nombre + Matrícula usando patrones adaptados
    al texto preprocesado.
    """
    texto = normalizacion_avanzada_pdf(path_pdf)
    personas = {}
    #print("texto pdf: ", texto)

    # Patrón para encontrar solo el número de DNI o MATRÍCULA
    pattern_dni_num = re.compile(r'\bDNI\s+(\d+)\b', flags=re.IGNORECASE)
    pattern_mat_num = re.compile(r'\bMATRICULA\s+(\d+)\b', flags=re.IGNORECASE)

    # Patrón para nombres: cada palabra empieza con mayúscula seguida de letras
    name_pattern = re.compile(
        r'\b([A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñ]+'
        r'(?:\s+[A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñ]+){0,2})\b'
    )

    window_size = 100  # caracteres hacia atrás desde el inicio del match

    # Función auxiliar para extraer el nombre más cercano antes de `idx`
    def nombre_cercano(idx: int) -> str:
        start = max(0, idx - window_size)
        window = texto[start:idx]
        nombres = name_pattern.findall(window)
        return nombres[-1] if nombres else ""

    # Procesar todos los DNIs encontrados
    for m in pattern_dni_num.finditer(texto):
        dni = m.group(1)
        nombre = nombre_cercano(m.start())
        if nombre:
            clave = f"DNI N° {dni}"
            personas.setdefault(clave, nombre.title())

    # Procesar todas las MATRÍCULAS encontradas
    for m in pattern_mat_num.finditer(texto):
        mat = m.group(1)
        nombre = nombre_cercano(m.start())
        if nombre:
            clave = f"Matrícula N° {mat}"
            personas.setdefault(clave, nombre.title())

    # Formatear resultado
    return [f"{nombre} | {clave}" for clave, nombre in personas.items()]