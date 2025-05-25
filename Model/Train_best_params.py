import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_absolute_error
import json
import matplotlib.pyplot as plt

# ------------------ Cargar datos ------------------ #
path_ventas = 'https://raw.githubusercontent.com/AdrianPinedaSanchez/Reto_Oxxo_DataKillers/main/Reto%20Oxxo/Venta.csv'
df_ventas = pd.read_csv(path_ventas)

path_train = 'https://raw.githubusercontent.com/AdrianPinedaSanchez/Reto_Oxxo_DataKillers/main/Reto%20Oxxo/DIM_TIENDA.csv'
df_tiendas = pd.read_csv(path_train)

tiendas = df_ventas['TIENDA_ID'].unique()
meses = list(df_ventas['MES_ID'].unique()) + [202408, 202409, 202410]
meses = sorted(set(meses))

df_completo = pd.MultiIndex.from_product([tiendas, meses], names=['TIENDA_ID', 'MES_ID']).to_frame(index=False)
df_completo = df_completo.merge(df_ventas, on=['TIENDA_ID', 'MES_ID'], how='left')
df_completo['VENTA_TOTAL'] = df_completo['VENTA_TOTAL'].fillna(0)

def mesid_a_fecha(mes_id):
    anio = mes_id // 100
    mes = mes_id % 100
    return pd.to_datetime(f"{anio}-{mes:02d}") + pd.offsets.MonthEnd(0)

df_completo['FECHA'] = df_completo['MES_ID'].map(mesid_a_fecha)

# ------------------ Rellenar ceros ------------------ #
def rellenar_ceros(df):
    df_nuevo = df.copy()
    for tienda in df_nuevo['TIENDA_ID'].unique():
        mask_tienda = df_nuevo['TIENDA_ID'] == tienda
        mask_final = mask_tienda & (df_nuevo['VENTA_TOTAL'] == 0)
        ventas_validas = df_nuevo.loc[mask_tienda & (df_nuevo['VENTA_TOTAL'] != 0), 'VENTA_TOTAL']
        if len(ventas_validas) == 0:
            continue
        media = ventas_validas.mean()
        std = ventas_validas.std()
        valores_aleatorios = media + std * np.random.rand(mask_final.sum())
        df_nuevo.loc[mask_final, 'VENTA_TOTAL'] = valores_aleatorios
    return df_nuevo

df_completo = rellenar_ceros(df_completo)

# ------------------ Preparar datos ------------------ #
def preparar_datos(df, forecast_days=3, lag_days=12):
    df = df.copy()
    df['FECHA'] = pd.to_datetime(df['FECHA'])
    df.sort_values(by=['TIENDA_ID', 'FECHA'], inplace=True)
    for lag in range(1, lag_days + 1):
        df[f'lag_{lag}'] = df.groupby('TIENDA_ID')['VENTA_TOTAL'].shift(lag)
    for f in range(1, forecast_days + 1):
        df[f'day_{f}'] = df.groupby('TIENDA_ID')['VENTA_TOTAL'].shift(-f)
    df['day'] = df['FECHA'].dt.day
    df['month'] = df['FECHA'].dt.month
    df['weekday'] = df['FECHA'].dt.weekday
    df.dropna(inplace=True)
    return df

df_ready = preparar_datos(df_completo, forecast_days=3, lag_days=12)

# ------------------ Cargar mejores parámetros ------------------ #
with open('mejores_parametros.json', 'r') as f:
    best_params = json.load(f)

num_boost_round = best_params.pop('num_boost_round')

# ------------------ Entrenamiento con TODO el dataset ------------------ #
feature_cols = [col for col in df_ready.columns if col.startswith('lag_')] + ['day', 'month', 'weekday']
target_cols = [f'day_{i}' for i in range(1, 4)]

X = df_ready[feature_cols]
y = df_ready[target_cols]
tienda_ids = df_ready['TIENDA_ID'].values

dtrain = xgb.DMatrix(X, label=y)
model = xgb.train(best_params, dtrain, num_boost_round=num_boost_round)
# ✅ Guardar modelo en JSON
model.save_model("mejor_modelo_xgb.json")
print(" Modelo XGBoost guardado como 'mejor_modelo_xgb.json'")
# ------------------ Evaluación por tienda ------------------ #
y_pred_all = model.predict(dtrain)
y_pred_all = np.maximum(0, np.round(y_pred_all)) + 1
y_true_all = y.values + 1

min_indices = []
for tienda in np.unique(tienda_ids):
    mask = tienda_ids == tienda
    if np.sum(mask) == 0:
        continue

    mape = np.mean(np.abs((y_true_all[mask] - y_pred_all[mask]) / y_true_all[mask]) * 100)
    mae = mean_absolute_error(y_true_all[mask], y_pred_all[mask])

    min_indices.append({
        "TIENDA_ID": int(tienda),
        "mape_test": float(mape),
        "mae_test": float(mae)
    })

# ------------------ Guardar resultados ------------------ #
with open('min_indices.json', 'w') as f_out:
    json.dump(min_indices, f_out, indent=4)

print(" Archivo 'min_indices.json' generado con métricas por tienda.")

# ------------------ Gráficas ------------------ #
df_metrics = pd.DataFrame(min_indices).sort_values(by='mape_test').reset_index(drop=True)

# Gráfica wMAPE
plt.figure(figsize=(12, 5))
plt.plot(df_metrics.index, df_metrics['mape_test'], marker='o', linestyle='-', label='wMAPE')
plt.title('wMAPE por tienda (ordenado)')
plt.xlabel('Ranking de tienda (0 a N)')
plt.ylabel('wMAPE (%)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Gráfica MAE
plt.figure(figsize=(12, 5))
plt.plot(df_metrics.index, df_metrics['mae_test'], marker='x', linestyle='-', label='MAE')
plt.title('MAE por tienda (ordenado)')
plt.xlabel('Ranking de tienda (0 a N)')
plt.ylabel('MAE')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
