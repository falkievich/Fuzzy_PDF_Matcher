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
    name_pat_natural = re.compile(
        r'\b([A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñ]+'
        r'(?:\s+[A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñ]+){1,2})\b'
    )

    window_natural  = 100  # caracteres hacia atrás desde el inicio del match

    # 4) Patrón de nombre “jurídico”: hasta 7 palabras, admitiendo puntos y & en cada token
    name_pat_juridico = re.compile(
        r'\b('
        r'[A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñ\.\&]+'              # primera “palabra” con letras, puntos o &
        r'(?:\s+[A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñ\.\&]+){1,7}'  # de 1 a 7 palabras adicionales iguales
        r')\b'
    )
    window_juridico = 70

    # Extrae el último nombre que coincide con name_pattern dentro de los window_size caracteres anteriores a idx
    def extraer_nombre(idx: int, name_pattern: re.Pattern, window_size: int) -> str:
        start = max(0, idx - window_size)
        segmento = texto[start:idx]
        matches = name_pattern.findall(segmento)
        return matches[-1] if matches else ""

    # 5) Stop-words
    STOP_WORDS = {"dni", "matricula", "mp", "cuif", "cuit", "cuil"}

    # 6) Primer pase: detección “natural” para todas las etiquetas
    raw_grouped = defaultdict(list)  # raw_name -> [ "DNI N° xxx", ... ]
    for etiqueta, pat in doc_patterns.items():
        regex = re.compile(pat, flags=re.IGNORECASE)
        for m in regex.finditer(texto):
            num = m.group(1)
            # usar patrón natural
            raw_name = extraer_nombre(m.start(), name_pat_natural, window_natural)
            if not raw_name:
                continue
            # filtrar stop-words
            tokens = [t for t in raw_name.split() if t.lower() not in STOP_WORDS]
            if len(tokens) < 2:
                continue
            clean_name = " ".join(tokens)
            clave = f"{etiqueta} N° {num}"
            if clave not in raw_grouped[clean_name]:
                raw_grouped[clean_name].append(clave)

    # 7) Segundo pase: rehacer nombres para entradas SOLO CUIT
    for name, tags in list(raw_grouped.items()):
        # comprobar si solo tiene CUIT
        if len(tags) == 1 and tags[0].upper().startswith("CUIT "):
            # extraer el número
            num = tags[0].split("N°")[1].strip()
            # buscar la posición de CUIT num en el texto
            pat_cuit = re.compile(r'\bCUIT\s+' + re.escape(num) + r'\b', flags=re.IGNORECASE)
            m = pat_cuit.search(texto)
            if m:
                # extraer nombre con ventana reducida y patrón jurídico
                new_raw = extraer_nombre(m.start(), name_pat_juridico, window_juridico)
                if new_raw:
                    tokens = [t for t in new_raw.split() if t.lower() not in STOP_WORDS]
                    if len(tokens) >= 2:
                        new_clean = " ".join(tokens)
                        # reasignar tags al nuevo nombre
                        raw_grouped[new_clean] = raw_grouped.pop(name)

    # 8) Agrupación por subconjunto de tokens (tolerancia k=1)
    k = 1
    merged = []
    for raw_name, tags in raw_grouped.items():
        toks = set(raw_name.lower().split())
        placed = False

        for entry in merged:
            existing = entry['tokens']
            # nuevo ⊆ existente? - Si toks es subconjunto de existing con diferencia <= k
            if toks <= existing and len(existing) - len(toks) <= k:
                entry['tags'] += [t for t in tags if t not in entry['tags']]
                placed = True
                break
            # existente ⊆ nuevo? - Si existing es subconjunto de new con diferencia <= k
            if existing <= toks and len(toks) - len(existing) <= k:
                entry['tokens'] = toks
                entry['name']   = raw_name
                entry['tags']   = list(set(entry['tags'] + tags))
                placed = True
                break

        if not placed:
            merged.append({'tokens': toks, 'name': raw_name, 'tags': list(tags)})

    # 9) Formatear resultado
    resultado = []
    for e in merged:
        resultado.append(f"{e['name'].title()} | " + " | ".join(e['tags']))

    return resultado