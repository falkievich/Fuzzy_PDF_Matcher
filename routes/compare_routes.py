# File: routes/compare_routes.py
import os
import tempfile

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from funcs.comparar_json_pdf import comparar_valores_json_pdf

#---------------------------------------------------------- Router
router = APIRouter()

# ---------------------------------------------------------- Post - Cargar un archivo JSON y un PDF para realizar la comparación de valores
@router.post("/upload_files", summary="Comparar JSON vs PDF con lógica difusa")
async def compare(
    data_file: UploadFile = File(..., description="Archivo de datos (.json, .txt)"),
    pdf_file: UploadFile = File(..., description="Archivo PDF")
):
    ext_data = os.path.splitext(data_file.filename)[1].lower()
    if ext_data not in (".json", ".txt"):
        raise HTTPException(400, "El archivo de datos debe ser .json o .txt")
    if not pdf_file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "El archivo de PDF debe tener extensión .pdf")

    # Guardar archivos temporales
    tmp_data = tempfile.NamedTemporaryFile(delete=False, suffix=ext_data)
    tmp_pdf  = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    try:
        tmp_data.write(await data_file.read())
        tmp_pdf.write(await pdf_file.read())
    finally:
        tmp_data.close()
        tmp_pdf.close()

    # Ejecutar comparación y obtener resultado estructurado
    result = comparar_valores_json_pdf(tmp_data.name, tmp_pdf.name)

    # Limpiar temporales
    try: os.unlink(tmp_data.name)
    except: pass
    try: os.unlink(tmp_pdf.name)
    except: pass

    return JSONResponse(result)
