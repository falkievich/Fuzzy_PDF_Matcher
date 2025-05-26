# File: funcs/comparar_json_pdf.py
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
        return {"fields": []}

    texto_pdf = extraer_texto_pdf(pdf_path)
    words = texto_pdf.split()

    resultado = {"fields": []}

    for key, value in json_data.items():
        field_entry = {"name": key, "comparisons": []}

        # Preparar lista de valores a comparar
        items = []
        if isinstance(value, dict):
            items = list(value.values())
        elif isinstance(value, list):
            for item in value:
                items.extend(item.values())
        else:
            items = [value]

        for val in items:
            val_str = str(val).strip()
            if not val_str:
                continue

            # Buscar el mejor candidato y su score
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
                best_score, best = -1.0, None
                json_norm = re.sub(r'\s+', ' ', val_str).lower()
                for i in range(len(words) - n + 1):
                    cand = ' '.join(words[i:i+n])
                    sc = fuzz.ratio(json_norm, cand.lower())
                    if sc > best_score:
                        best_score, best = sc, cand

            label, _ = infer_label(best_score)

            field_entry["comparisons"].append({
                "json_value": val_str,
                "pdf_value": best,
                "similarity": round(best_score, 2),
                "label": label
            })

        resultado["fields"].append(field_entry)

    return resultado
