from funcs.extraer_datos_json import extraer_valores_txt
from funcs.extraer_texto_pdf import extraer_texto_pdf
from funcs.comparar_json_pdf import comparar_valores_json_pdf
#from funcs.fuzzy_logic import comparar_valores  # Importa la función de comparación fuzzy

def comparar_datos():
    # Extraer los valores del archivo JSON
    #json_data = extraer_valores_txt('datos.txt')
    #print("Valores extraídos del archivo JSON:")
    #print(json_data)

    # Extraer el texto del archivo PDF
    #texto_pdf = extraer_texto_pdf('ley.pdf')
    #print("\nTexto extraído del archivo PDF:")
    #print(texto_pdf)

    # Llamamos a la función de comparación
    comparar_valores_json_pdf('datos.txt', 'ley.pdf')


if __name__ == "__main__":
    comparar_datos()
