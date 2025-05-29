"""
Carga un archivo JSON y un PDF, extrae valores del JSON (en la raíz, diccionarios o listas) y del PDF (numéricos y n-gramas de texto), calcula la similitud fuzzy entre cada par JSON ↔ PDF, aplica la inferencia difusa para etiquetar cada comparación y agrupa los resultados en categorías exacta, alta, media y baja.
"""
import re
from rapidfuzz import fuzz
from funcs.extraer_datos_json import extraer_valores_txt
from funcs.extraer_texto_pdf import extraer_texto_pdf
from funcs.fuzzy_logic import infer_label

# Regex para extraer números con separadores
NUM_REGEX = re.compile(r"\b\d{1,3}(?:[.\-]\d{1,3})*\b")

def comparar_valores_json_pdf(json_path: str, pdf_path: str):
    json_data = extraer_valores_txt(json_path)
    if not json_data:
        return {"exacta": [], "alta": [], "media": [], "baja": []}

    texto_pdf = extraer_texto_pdf(pdf_path)
    words = texto_pdf.split()

    # Lista plana de todas las comparaciones
    all_comparisons = []

    # Recorremos todos los campos del JSON (raíz, dicts o listas)
    for key, value in json_data.items():
        # Preparamos la lista de valores a comparar
        if isinstance(value, dict):
            items = list(value.values())
        elif isinstance(value, list):
            items = []
            for item in value:
                items.extend(item.values())
        else:
            items = [value]

        for val in items:
            val_str = str(val).strip()
            if not val_str:
                continue

            # 1) Detectar numérico vs texto
            if NUM_REGEX.fullmatch(val_str):
                # Numérico: extraer y comparar tokens numéricos
                candidates = NUM_REGEX.findall(texto_pdf)
                clean_json = re.sub(r"\D", "", val_str)
                best_score, best = -1.0, None
                for tok in candidates:
                    clean_tok = re.sub(r"\D", "", tok)
                    sc = fuzz.ratio(clean_json, clean_tok)
                    if sc > best_score:
                        best_score, best = sc, tok
            else:
                # Texto: generar n-gramas según número de palabras
                n = len(val_str.split())
                json_norm = re.sub(r'\s+', ' ', val_str).strip().lower()
                best_score, best = -1.0, None
                for i in range(len(words) - n + 1):
                    cand = ' '.join(words[i:i+n])
                    sc = fuzz.ratio(json_norm, cand.lower())
                    if sc > best_score:
                        best_score, best = sc, cand

            # 2) Inferencia difusa
            label, _ = infer_label(best_score)

            # 3) Añadir a la lista general
            all_comparisons.append({
                "field": key,
                "json_value": val_str,
                "pdf_value": best,
                "similarity": round(best_score, 2),
                "label": label
            })

    # 4) Agrupar y ordenar por categoría
    result = {
        "exacta": [c for c in all_comparisons if c["label"] == "exacta"],
        "alta":   [c for c in all_comparisons if c["label"] == "alta"],
        "media":  [c for c in all_comparisons if c["label"] == "media"],
        "baja":   [c for c in all_comparisons if c["label"] == "baja"],
    }
    return result
