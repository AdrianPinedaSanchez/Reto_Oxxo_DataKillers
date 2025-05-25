import pandas as pd
import joblib
from sklearn.metrics.pairwise import haversine_distances
from math import radians
import numpy as np


# Cargar modelo y encoders
model = joblib.load("Reto_Oxxo_DataKillers/Model/modelo_regresion_succ.pkl")
# enc_nivel = joblib.load("Reto_Oxxo_DataKillers/Model/enc_nivel.pkl")
# enc_entorno = joblib.load("Reto_Oxxo_DataKillers/Model/enc_entorno.pkl")
# enc_segmento = joblib.load("Reto_Oxxo_DataKillers/Model/enc_segmento.pkl")

# # Cargar test
# test_path = 'https://raw.githubusercontent.com/AdrianPinedaSanchez/Reto_Oxxo_DataKillers/main/Reto%20Oxxo/DIM_TIENDA_TEST.csv'
# df_test = pd.read_csv(test_path)

# # Dataset base para rellenar
# path_train = 'https://raw.githubusercontent.com/AdrianPinedaSanchez/Reto_Oxxo_DataKillers/main/Reto%20Oxxo/DIM_TIENDA.csv'
# df_train = pd.read_csv(path_train)
# df_train['lat_rad'] = df_train['LATITUD_NUM'].apply(radians)
# df_train['lon_rad'] = df_train['LONGITUD_NUM'].apply(radians)



# Datos nuevos (solo lat y lon)
lat = 25.682  # ejemplo
lon = -98.26  # ejemplo
plaza = 1
puertas = 1
cajones = 1
m2 = 1 
#Convertir a radianes
# coords_input = np.array([[radians(lat), radians(lon)]])

# Calcular distancias haversine
# coords_train = df_train[['lat_rad', 'lon_rad']].values
# distancias = haversine_distances(coords_input, coords_train)[0]

# Obtener índice de la tienda más cercana
# idx_min = np.argmin(distancias)
# tienda_mas_cercana = df_train.iloc[idx_min]


# Construir fila para predicción
data_pred = pd.DataFrame([{
    'LATITUD_NUM': lat,
    'LONGITUD_NUM': lon,
    'PLAZA_CVE': plaza,
    'MTS2VENTAS_NUM': m2,
    'PUERTASREFRIG_NUM': puertas,
    'CAJONESESTACIONAMIENTO_NUM': cajones,
}])

# Predecir
pred_succ = model.predict(data_pred)[0]

# Ver resultados
print(pred_succ)