import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from xgboost import XGBClassifier
from itertools import groupby
import joblib
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score
import os

path_ventas= 'https://raw.githubusercontent.com/AdrianPinedaSanchez/Reto_Oxxo_DataKillers/main/Reto%20Oxxo/Venta.csv'
df_ventas=pd.read_csv(path_ventas)

path_train = 'https://raw.githubusercontent.com/AdrianPinedaSanchez/Reto_Oxxo_DataKillers/main/Reto%20Oxxo/DIM_TIENDA.csv'
df_tiendas=pd.read_csv(path_train)

combined=df_tiendas.merge(df_ventas,on='TIENDA_ID',how='right')

# Diccionario con metas por entorno
meta_dict = {
    "Base": 480000,
    "Hogar": 490000,
    "Peatonal": 420000,
    "Receso": 516000
}
df=combined.copy()
df['over_meta'] = df.apply(
    lambda row: row['VENTA_TOTAL'] > meta_dict.get(row['ENTORNO_DES'], float('inf')),
    axis=1
)

resultados = []

for tienda_id, grupo in df.groupby('TIENDA_ID'):
    valores = grupo.sort_values('MES_ID')['over_meta'].astype(int).tolist()

    prop_meses = sum(valores) / len(valores)

    max_racha = max((len(list(streak)) for val, streak in groupby(valores) if val == 1), default=0)
    prop_racha = max_racha / len(valores)
    succ = (prop_meses + prop_racha) / 2 #> 0.51

    resultados.append([tienda_id, prop_meses, prop_racha, succ])

df_metricas = pd.DataFrame(resultados, columns=[
    'TIENDA_ID',
    'prop_meses_sobre_meta',
    'prop_racha_sobre_meta',
    'succ'
])

df_final = df.merge(df_metricas, on='TIENDA_ID', how='left')

df_final.dropna(inplace=True)


#Entrenamiento

df = df_final.copy()

# Codificar las columnas categóricas
enc_nivel = LabelEncoder()
enc_entorno = LabelEncoder()
enc_segmento = LabelEncoder()

df['NIVELSOCIOECONOMICO_DES'] = enc_nivel.fit_transform(df['NIVELSOCIOECONOMICO_DES'])
df['ENTORNO_DES'] = enc_entorno.fit_transform(df['ENTORNO_DES'])
df['SEGMENTO_MAESTRO_DESC'] = enc_segmento.fit_transform(df['SEGMENTO_MAESTRO_DESC'])

# Guardar encoders
joblib.dump(enc_nivel, "enc_nivel.pkl")
joblib.dump(enc_entorno, "enc_entorno.pkl")
joblib.dump(enc_segmento, "enc_segmento.pkl")

# --------------------------
# Variables de entrada y salida
X = df[['LATITUD_NUM', 'LONGITUD_NUM', 'PLAZA_CVE',
        'NIVELSOCIOECONOMICO_DES', 'ENTORNO_DES', 'SEGMENTO_MAESTRO_DESC']]

y = df['succ'].astype(float)  # continua entre 0 y 1

# Entrenamiento
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = XGBRegressor(objective='reg:squarederror', eval_metric='rmse')
model.fit(X_train, y_train)

# --------------------------
# Evaluación
y_pred = model.predict(X_test)
print("R2:", r2_score(y_test, y_pred))
print("RMSE:", np.sqrt(mean_squared_error(y_test, y_pred)))

# Guardar modelo
# Crear carpeta si no existe

# Guardar el modelo dentro de la carpeta Model del repositorio
joblib.dump(model, "Reto_Oxxo_DataKillers/Model/modelo_regresion_succ.pkl")
