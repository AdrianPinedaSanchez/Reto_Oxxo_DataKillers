from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Permitir peticiones desde tu frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # o ["http://localhost:5173"] si usas Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/predict")
def predict(lat: float = Query(...), lng: float = Query(...)):
    # Aquí iría la llamada a tu modelo real
    resultado_fake = {
        "categoria": "Zona de Riesgo",
        "puntuacion": 0.87,
        "lat": lat,
        "lng": lng,
    }
    return resultado_fake
