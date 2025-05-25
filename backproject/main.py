from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import joblib
from sklearn.metrics.pairwise import haversine_distances
from math import radians
import numpy as np
from fastapi.encoders import jsonable_encoder

import requests
from dotenv import load_dotenv
import os
from pandas.tseries.offsets import DateOffset

import xgboost as xgb
from datetime import timedelta
app = FastAPI()

# Permitir peticiones desde tu frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # o ["http://localhost:5173"] si usas Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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



#model prediction

def predictByYears(years:int):
    def preparar_features_para_forecast(df, fecha_inicio_forecast, forecast_days=years, lag_days=12):
        df = df.copy()
        df['FECHA'] = pd.to_datetime(df['FECHA'])
        df.sort_values(by=['TIENDA_ID', 'FECHA'], inplace=True)

        # Recortar el DataFrame hasta justo antes del forecast
        df = df[df['FECHA'] < fecha_inicio_forecast]

        # ✅ Nueva forma: usar meses, no días
        fecha_minima_requerida = fecha_inicio_forecast - DateOffset(months=lag_days)
        fechas_validas = df.groupby('TIENDA_ID')['FECHA'].max() >= fecha_minima_requerida
        tiendas_validas = fechas_validas[fechas_validas].index
        df = df[df['TIENDA_ID'].isin(tiendas_validas)]

        # Generar lags por tienda
        for lag in range(1, lag_days + 1):
            df[f'lag_{lag}'] = df.groupby('TIENDA_ID')['VENTA_TOTAL'].shift(lag)

        # Tomar solo la fila más reciente por tienda
        ultima_fecha = df.groupby('TIENDA_ID')['FECHA'].transform('max') == df['FECHA']
        df = df[ultima_fecha]

        # Features temporales
        df['day'] = df['FECHA'].dt.day
        df['month'] = df['FECHA'].dt.month
        df['weekday'] = df['FECHA'].dt.weekday

        df.dropna(inplace=True)

        feature_cols = [col for col in df.columns if col.startswith('lag_')] + ['day', 'month', 'weekday']
        X_forecast = df[feature_cols]
        tiendas = df['TIENDA_ID'].values

        return X_forecast, tiendas
    def predecir_ventas(model_path, df_completo_rellenado, fecha_inicio_forecast_str, forecast_days=years, lag_days=12):
        from pandas.tseries.offsets import MonthEnd

        fecha_inicio_forecast = pd.to_datetime(fecha_inicio_forecast_str)

        # Preparar features
        X_forecast, tiendas = preparar_features_para_forecast(
            df_completo_rellenado, fecha_inicio_forecast, forecast_days, lag_days
        )

        # Cargar modelo XGBoost
        model = xgb.Booster()
        model.load_model(model_path)

        # Predecir
        dmatrix = xgb.DMatrix(X_forecast)
        pred = model.predict(dmatrix)
        pred = np.maximum(0, np.round(pred))  # Asegurar no-negativas

        # Armar resultados
        pred_df = pd.DataFrame(pred, columns=[f'sales_month_{i}' for i in range(1, forecast_days + 1)])
        pred_df['TIENDA_ID'] = tiendas

        # Convertir a formato largo
        pred_long = pred_df.melt(id_vars='TIENDA_ID', var_name='month_offset', value_name='VENTA_PRED')
        pred_long['MES_REL'] = pred_long['month_offset'].str.extract(r'(\d+)').astype(int)

        # Calcular la fecha del último día de cada mes futuro
        pred_long['FECHA'] = fecha_inicio_forecast + pred_long['MES_REL'].apply(lambda x: pd.DateOffset(months=x - 1))
        pred_long['FECHA'] = pred_long['FECHA'] + MonthEnd(0)

        # Limpiar columnas
        pred_long.drop(columns=['month_offset', 'MES_REL'], inplace=True)

        return pred_long.sort_values(['TIENDA_ID', 'FECHA'])

    path_ventas= 'https://raw.githubusercontent.com/AdrianPinedaSanchez/Reto_Oxxo_DataKillers/main/Reto%20Oxxo/Venta.csv'
    df_ventas=pd.read_csv(path_ventas)

    path_train = 'https://raw.githubusercontent.com/AdrianPinedaSanchez/Reto_Oxxo_DataKillers/main/Reto%20Oxxo/DIM_TIENDA.csv'
    df_tiendas=pd.read_csv(path_train)


    tiendas = df_ventas['TIENDA_ID'].unique()
    meses = list(df_ventas['MES_ID'].unique())

    faltantes = [202408, 202409, 202410]
    for m in faltantes:
        if m not in meses:
            meses.append(m)

    meses.sort()

    df_completo = pd.MultiIndex.from_product([tiendas, meses], names=['TIENDA_ID', 'MES_ID']).to_frame(index=False)

    df_completo = df_completo.merge(df_ventas, on=['TIENDA_ID', 'MES_ID'], how='left')

    df_completo['VENTA_TOTAL'] = df_completo['VENTA_TOTAL'].fillna(0)

    def mesid_a_fecha(mes_id):
        anio = mes_id // 100
        mes = mes_id % 100
        return pd.to_datetime(f"{anio}-{mes:02d}") + pd.offsets.MonthEnd(0)

    mapa_mesid_fecha = {mes: mesid_a_fecha(mes) for mes in meses}

    df_completo['FECHA'] = df_completo['MES_ID'].map(mapa_mesid_fecha)

    tienda_loc=df_tiendas[['LATITUD_NUM','LONGITUD_NUM','TIENDA_ID']]

    df_completo=df_completo.merge(tienda_loc,on='TIENDA_ID',how='left')

    # Función para rellenar los ceros por tienda
    def rellenar_ceros(df):
        df_nuevo = df.copy()
        tiendas = df_nuevo['TIENDA_ID'].unique()
        conteo = 0
        remplazos = {}
        for tienda in tiendas:
            remplazos[f'{tienda}'] = 0
            mask_tienda = df_nuevo['TIENDA_ID'] == tienda
            mask_venta_0 = df_nuevo['VENTA_TOTAL'] == 0
            mask_final = mask_tienda & mask_venta_0

            ventas_validas = df_nuevo.loc[mask_tienda & (df_nuevo['VENTA_TOTAL'] != 0), 'VENTA_TOTAL']
            if len(ventas_validas) == 0:
                continue  # evitar división por cero

            media = ventas_validas.mean()
            std = ventas_validas.std()

            # generar valores aleatorios entre 0 y 1, luego multiplicar por std y sumar a la media
            n = mask_final.sum()
            conteo +=n
            remplazos[f'{tienda}'] = n
            valores_aleatorios = media + std * np.random.rand(n)

            df_nuevo.loc[mask_final, 'VENTA_TOTAL'] = valores_aleatorios

        return df_nuevo

    # Aplicar función
    df_completo_rellenado = rellenar_ceros(df_completo)

    # Ruta al modelo entrenado
    model_path = r"C:\Users\danyO\Documents\project-front\Model\modelo_xgb_serie.json"
    # Definir desde qué fecha quieres predecir
    fecha_forecast = "2024-08-01"

    # Ejecutar predicción
    predicciones = predecir_ventas(model_path, df_completo_rellenado, fecha_forecast)

    return predicciones


@app.get("/predict")
def predict(lat: float = Query(...), lng: float = Query(...)):
    result = modelitocachondo(lat, lng)
    print(result)

    # Retornar el resultado en un formato serializable
    resultado_fake = {
        "lat": lat,
        "lng": lng,
        "result": result,    }
    
    return resultado_fake

load_dotenv()
GOOGLE_API_KEY = os.getenv("VITE_GOOGLE_MAPS_API_KEY")

@app.get("/elevation")
def get_elevation(lat: float, lng: float):
    url = f"https://maps.googleapis.com/maps/api/elevation/json?locations={lat},{lng}&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    return response.json()

@app.get("/predictionFuture")
def predict_future(valor:int):
    print(valor)
    # df=predictByYears(valor)
    # output_path=r"C:\Users\danyO\Documents\project-front\frontproject\frontoxxos\public\data\Forecast_2025-01.csv"
    # df.to_csv(output_path, index=False)
    return {"resultado": valor * 10}  # Ejemplo simple
 


