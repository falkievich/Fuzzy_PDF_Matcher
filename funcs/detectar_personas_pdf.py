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

    # 4) Stop-words que no forman parte de un nombre
    STOP_WORDS = {"dni", "matricula", "mp", "cuif", "cuit", "cuil"}

    # 5) Recolectar etiquetas por nombre crudo
    raw_grouped = defaultdict(list)  # raw_name -> [ "DNI N° xxx", ... ]
    for etiqueta, pat in doc_patterns.items():
        regex = re.compile(pat, flags=re.IGNORECASE)
        for m in regex.finditer(texto):
            numero = m.group(1)
            raw_name = nombre_cercano(m.start())
            if not raw_name:
                continue
            # Filtrar stop-words del raw_name
            tokens = [tok for tok in raw_name.split() if tok.lower() not in STOP_WORDS]
            if len(tokens) < 2:
                continue
            clean_name = " ".join(tokens)
            clave = f"{etiqueta} N° {numero}"
            if clave not in raw_grouped[clean_name]:
                raw_grouped[clean_name].append(clave)

    # 6) Agrupación por subconjunto de tokens (tolerancia k)
    k = 1  # máximo número de tokens faltantes permitidos
    merged = []  # lista de dicts: {'tokens': set, 'name': str, 'tags': [str,...]}

    for raw_name, tags in raw_grouped.items():
        new_tokens = set(tok.lower() for tok in raw_name.split())
        placed = False

        for entry in merged:
            existing = entry['tokens']
            # Si new es subconjunto de existing con diferencia <= k
            if new_tokens <= existing and len(existing) - len(new_tokens) <= k:
                for tag in tags:
                    if tag not in entry['tags']:
                        entry['tags'].append(tag)
                placed = True
                break
            # Si existing es subconjunto de new con diferencia <= k
            if existing <= new_tokens and len(new_tokens) - len(existing) <= k:
                entry['tokens'] = new_tokens
                entry['name'] = raw_name
                for tag in tags:
                    if tag not in entry['tags']:
                        entry['tags'].append(tag)
                placed = True
                break

        if not placed:
            merged.append({'tokens': new_tokens, 'name': raw_name, 'tags': list(tags)})

    # 7) Formatear resultado
    resultado = []
    for entry in merged:
        nombre = entry['name'].title()
        etiquetas = entry['tags']
        resultado.append(f"{nombre} | " + " | ".join(etiquetas))

    return resultado