import re
from collections import defaultdict
from funcs.extraer_texto_pdf import normalizacion_avanzada_pdf

def detectar_personas_dni_matricula(path_pdf: str = None, raw_text: str = None):
    """
    Extrae y normaliza el texto de un PDF (normalizacion_avanzada_pdf), luego detecta pares
    Nombre + DNI y Nombre + Matrícula (ambos casos pueden tener CUIF, CUIT e CUIL) usando patrones adaptados
    al texto preprocesado.
    """
    # 1) Obtener texto normalizado
    if raw_text is not None:
        texto = normalizacion_avanzada_pdf(raw_text=raw_text)
    elif path_pdf:
        texto = normalizacion_avanzada_pdf(path_pdf=path_pdf)
    else:
        raise ValueError("Se debe pasar path_pdf o raw_text")
    
    print("texto pdf: ", texto)

    # 2) Mapear cada etiqueta a su regex de número
    doc_patterns = {
        "DNI":      r'\bDNI\s+(\d+)\b',
        "MATRICULA":r'\bMATRICULA\s+(\d+)\b',
        "CUIF":     r'\bCUIF\s+(\d+)\b',
        "CUIT":     r'\bCUIT\s+(\d+)\b',
        "CUIL":     r'\bCUIL\s+(\d+)\b',
    }

    # 3) Patrón de nombre: mínimo 1 palabra que empiecen en mayúscula, máximo 3 (la palabra iniclal (1) + 2 más que cumplan los requisitos)
    name_pattern = re.compile(
        r'\b([A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñ]+'
        r'(?:\s+[A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñ]+){1,2})\b'
    )

    window_size = 100  # caracteres hacia atrás desde el inicio del match

    def nombre_cercano(idx: int) -> str:
        start = max(0, idx - window_size)
        window = texto[start:idx]
        matches = name_pattern.findall(window)
        return matches[-1] if matches else ""

    # 4) Recolectar etiquetas por nombre crudo
    raw_grouped = defaultdict(list)  # raw_name -> [ "DNI N° xxx", ... ]
    for etiqueta, pat in doc_patterns.items():
        regex = re.compile(pat, flags=re.IGNORECASE)
        for m in regex.finditer(texto):
            numero = m.group(1)
            nombre = nombre_cercano(m.start())
            if not nombre:
                continue
            clave = f"{etiqueta} N° {numero}"
            if clave not in raw_grouped[nombre]:
                raw_grouped[nombre].append(clave)

    # 5) Unificar variantes de nombre (orden de tokens)
    merged = {}  # key (frozenset tokens) -> { 'name': canonical, 'tags': [] }
    for raw_name, tags in raw_grouped.items():
        tokens = [tok.lower() for tok in raw_name.split()]
        key = tuple(sorted(tokens))
        if key not in merged:
            merged[key] = {'name': raw_name, 'tags': list(tags)}
        else:
            for tag in tags:
                if tag not in merged[key]['tags']:
                    merged[key]['tags'].append(tag)

    # 6) Formatear resultado final
    resultado = []
    for entry in merged.values():
        nombre = entry['name'].title()
        etiquetas = entry['tags']
        resultado.append(f"{nombre} | " + " | ".join(etiquetas))

    return resultado