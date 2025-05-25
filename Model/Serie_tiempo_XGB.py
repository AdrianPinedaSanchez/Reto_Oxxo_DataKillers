import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xgboost as xgb
from sklearn.model_selection import train_test_split
from datetime import timedelta

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


def preparar_datos(df, forecast_days=3, lag_days=12):
    df = df.copy()
    df['FECHA'] = pd.to_datetime(df['FECHA'])
    df.sort_values(by=['TIENDA_ID', 'FECHA'], inplace=True)

    # Crear columnas de lags por tienda
    for lag in range(1, lag_days + 1):
        df[f'lag_{lag}'] = df.groupby('TIENDA_ID')['VENTA_TOTAL'].shift(lag)

    # Crear columnas target (futuros días)
    for f in range(1, forecast_days + 1):
        df[f'day_{f}'] = df.groupby('TIENDA_ID')['VENTA_TOTAL'].shift(-f)

    # Features de calendario
    df['day'] = df['FECHA'].dt.day
    df['month'] = df['FECHA'].dt.month
    df['weekday'] = df['FECHA'].dt.weekday

    # Eliminar NaNs generados por los shifts
    df.dropna(inplace=True)

    return df

def entrenar_xgb(df, forecast_days=3):
    # Separar features y targets
    feature_cols = [col for col in df.columns if col.startswith('lag_')] + ['day', 'month', 'weekday']
    target_cols = [f'day_{i}' for i in range(1, forecast_days + 1)]

    X = df[feature_cols]
    y = df[target_cols]

    # Separar conjunto de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)

    # Convertir a DMatrix
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test, label=y_test)

    # Definir parámetros y entrenar modelo
    params = {
        'objective': 'reg:squarederror',
        'tree_method': 'hist',
        'max_depth': 6,
        'learning_rate': 0.1,
        'device': 'cuda'
    }

    model = xgb.train(params, dtrain, num_boost_round=300)
    # Guardar modelo localmente
    model.save_model("Reto_Oxxo_DataKillers/Model/modelo_xgb_serie.json")


    return model, dtest, y_test

def calcular_mape(y_true, y_pred):
    y_pred = np.maximum(0, np.round(y_pred)) + 1
    y_true = y_true.values + 1
    mape = np.abs((y_true - y_pred) / y_true) * 100
    return np.mean(mape, axis=0), np.mean(mape)

#
df_ready = preparar_datos(df_completo_rellenado, forecast_days=3, lag_days=12)
# Entrenar modelo
model, dtest, y_test = entrenar_xgb(df_ready, forecast_days=3)
# Predicciones y MAPE
y_pred = model.predict(dtest)
mape_por_dia, mape_promedio = calcular_mape(y_test, y_pred)

print(f"MAPE promedio de los 3 meses: {mape_promedio:.2f}%")
print(f"MAPE por mes: {mape_por_dia}")