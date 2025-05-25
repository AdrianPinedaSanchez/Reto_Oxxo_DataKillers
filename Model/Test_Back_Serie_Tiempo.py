import pandas as pd
import numpy as np
import xgboost as xgb
from datetime import timedelta
import os
import json
def preparar_features_para_forecast(df, fecha_inicio_forecast, forecast_days=3, lag_days=12):
    from pandas.tseries.offsets import DateOffset

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


def predecir_ventas(model_path, df_completo_rellenado, fecha_inicio_forecast_str, forecast_days=3, lag_days=12):
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

path_min_ind = r'C:\Users\cabal\Desktop\Datathon2025\Reto_Oxxo_DataKillers\min_indices.json'

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
# model_path = os.path.join("Reto_Oxxo_DataKillers", "Model", "modelo_xgb_serie.json")
model_path = "mejor_modelo_xgb.json"

# Definir desde qué fecha quieres predecir
fecha_forecast = "2024-08-01"

# Ejecutar predicción
predicciones = predecir_ventas(model_path, df_completo_rellenado, fecha_forecast)

# Ruta destino dentro del repo
output_path = os.path.join("Reto_Oxxo_DataKillers", "Forecasts", f"Forecast_{fecha_forecast[:7]}.csv")

# Crear carpeta si no existe
os.makedirs(os.path.dirname(output_path), exist_ok=True)
df_tiendas=df_tiendas[['TIENDA_ID','LATITUD_NUM','LONGITUD_NUM']]
predicciones=predicciones.merge(df_tiendas,on='TIENDA_ID')
with open(path_min_ind, 'r') as f:
    min_indices = json.load(f)

# Convertir a DataFrame
df_metrics = pd.DataFrame(min_indices)

# Unir las métricas por TIENDA_ID al DataFrame de predicciones
predicciones = predicciones.merge(df_metrics, on='TIENDA_ID', how='left')
# Guardar predicciones
predicciones.to_csv(output_path, index=False)
print(f"Predicciones guardadas en: {output_path}")