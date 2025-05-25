from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import joblib
from sklearn.metrics.pairwise import haversine_distances
from math import radians
import numpy as np
from fastapi.encoders import jsonable_encoder

app = FastAPI()

def modelitocachondo(latitude: float, longitud: float):
    model = joblib.load(r"C:\Users\danyO\Documents\project-front\Model\modelo_regresion_succ.pkl")
    enc_nivel = joblib.load(r"C:\Users\danyO\Documents\project-front\Model\enc_nivel.pkl")
    enc_entorno = joblib.load(r"C:\Users\danyO\Documents\project-front\Model\enc_entorno.pkl")
    enc_segmento = joblib.load(r"C:\Users\danyO\Documents\project-front\Model\enc_segmento.pkl")

    print("PRIMERA ETAPA")
    latitude = float(latitude) % 10000
    longitud = float(longitud) % 10000

    # Cargar test
    test_path = 'https://raw.githubusercontent.com/AdrianPinedaSanchez/Reto_Oxxo_DataKillers/main/Reto%20Oxxo/DIM_TIENDA_TEST.csv'
    df_test = pd.read_csv(test_path)

    # Dataset base para rellenar
    path_train = 'https://raw.githubusercontent.com/AdrianPinedaSanchez/Reto_Oxxo_DataKillers/main/Reto%20Oxxo/DIM_TIENDA.csv'
    df_train = pd.read_csv(path_train)
    df_train['lat_rad'] = df_train['LATITUD_NUM'].apply(radians)
    df_train['lon_rad'] = df_train['LONGITUD_NUM'].apply(radians)

    # Convertir a radianes
    coords_input = np.array([[radians(latitude), radians(longitud)]])

    # Calcular distancias haversine
    coords_train = df_train[['lat_rad', 'lon_rad']].values
    distancias = haversine_distances(coords_input, coords_train)[0]

    # Obtener índice de la tienda más cercana
    idx_min = np.argmin(distancias)
    tienda_mas_cercana = df_train.iloc[idx_min]

    print("Segunda ETAPA")
    # Construir fila para predicción
    data_pred = pd.DataFrame([{
        'LATITUD_NUM': latitude,
        'LONGITUD_NUM': longitud,
        'PLAZA_CVE': tienda_mas_cercana['PLAZA_CVE'],
        'NIVELSOCIOECONOMICO_DES': enc_nivel.transform([tienda_mas_cercana['NIVELSOCIOECONOMICO_DES']])[0],
        'ENTORNO_DES': enc_entorno.transform([tienda_mas_cercana['ENTORNO_DES']])[0],
        'SEGMENTO_MAESTRO_DESC': enc_segmento.transform([tienda_mas_cercana['SEGMENTO_MAESTRO_DESC']])[0],
    }])

    print("TERCERA ETAPA")
    # Predecir
    pred_succ = model.predict(data_pred)[0]
    print(pred_succ)
    # Convertir el valor a tipo float (Python estándar) para evitar problemas de serialización
    return float(pred_succ)

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
    result = modelitocachondo(lat, lng)

    # Retornar el resultado en un formato serializable
    resultado_fake = {
        "lat": lat,
        "lng": lng,
        "result": result,    }
    
    return resultado_fake
