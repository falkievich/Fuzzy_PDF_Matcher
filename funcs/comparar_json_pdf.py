import re
from funcs.extraer_datos_json import extraer_valores_txt
from funcs.extraer_texto_pdf import extraer_texto_pdf

def comparar_valores_json_pdf(json_path='datos.txt', pdf_path='ley.pdf'):
    """
    Compara los valores extraídos del JSON con el texto extraído del PDF sin lógica difusa.
    Imprime los resultados de cada comparación.
    """
    # Extraer los valores del archivo JSON
    json_data = extraer_valores_txt(json_path)
    
    # Si el JSON no tiene claves, salir
    if not json_data:
        return

    # Extraer el texto del archivo PDF
    texto_pdf = extraer_texto_pdf(pdf_path)

    # Limitar el texto del PDF para facilitar la visualización
    print(f"Texto extraído del PDF (primeros 500 caracteres):\n{texto_pdf[:500]}\n{'-'*50}\n")
    
    # Recorrer los datos extraídos del JSON
    for key, value in json_data.items():
        print(f"\nComparando para el campo: {key}")
        
        # Si el valor del JSON es un diccionario, recorrer sus valores
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                comparar_sub_valor(sub_key, sub_value, texto_pdf)
        
        # Si el valor del JSON es una lista, recorrer los elementos de la lista
        elif isinstance(value, list):
            for item in value:
                for sub_key, sub_value in item.items():
                    comparar_sub_valor(sub_key, sub_value, texto_pdf)
        
        # Si el valor del JSON es un valor simple (string, número, etc.)
        else:
            comparar_sub_valor(key, value, texto_pdf)

def comparar_sub_valor(clave, valor, texto_pdf):
    """
    Compara el valor extraído del JSON con el texto extraído del PDF, e imprime el resultado.
    """
    # Convertir a cadena y recortar espacios
    valor_str = str(valor).strip()
    
    # Si está vacío, no hacer nada
    if not valor_str:
        return
    
    # Buscar coincidencias exactas (sin considerar acentos ni variaciones)
    matches = re.findall(rf'\b{re.escape(valor_str)}\b', texto_pdf, re.IGNORECASE)
    
    if matches:
        # Mostrar todas las coincidencias bajo el mismo campo
        for match in matches:
            print(f"Coincidencia exacta encontrada: {clave} -> {valor_str} | PDF: {match}")
    else:
        print(f"No se encontró coincidencia exacta para: {clave} -> {valor_str}")

if __name__ == "__main__":
    comparar_valores_json_pdf('datos.txt', 'ley.pdf')
