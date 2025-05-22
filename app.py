# File: app.py
from funcs.comparar_json_pdf import comparar_valores_json_pdf

if __name__ == "__main__":
    # Ejecuta la comparación avanzada con lógica difusa
    comparar_valores_json_pdf('datos.txt', 'ley.pdf')
