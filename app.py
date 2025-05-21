from funcs.extraer_datos_json import extraer_valores_txt
from funcs.extraer_texto_pdf import extraer_texto_pdf

def comparar_datos():
    # Extraer los valores del archivo JSON
    json_data = extraer_valores_txt('datos.txt')
    print("Valores extraídos del archivo JSON:")
    print(json_data)

    # Extraer el texto del archivo PDF (ambos: original y normalizado)
    texto_original, texto_normalizado = extraer_texto_pdf('ley.pdf')

    # Imprimir el texto original del PDF
    print("\nTexto extraído del archivo PDF (original):")
    print(texto_original)  # Imprimir todo el texto original

    # Imprimir el texto normalizado del PDF
    print("\nTexto extraído del archivo PDF (normalizado):")
    print(texto_normalizado)  # Imprimir todo el texto normalizado

if __name__ == "__main__":
    comparar_datos()
