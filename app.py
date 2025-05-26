# File: app.py
from fastapi import FastAPI
from routes.compare_routes import router as compare_router

app = FastAPI(title="Fuzzy Matcher API")

# Montamos el router de nuestro endpoint
app.include_router(compare_router, prefix="/api")
