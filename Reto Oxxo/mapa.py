import numpy as np
import pandas as pd
import plotly.express as px

path = r'C:\Users\cabal\Desktop\Datathon2025\Reto_Oxxo_DataKillers\Reto Oxxo\DIM_TIENDA.csv' 
path = path.replace("\\", "/")

df_tiendas = pd.read_csv(path)
df_tiendas = df_tiendas.dropna(subset=['LATITUD_NUM', 'LONGITUD_NUM'])

Tiendas = df_tiendas['TIENDA_ID'].values
Latitud = df_tiendas['LATITUD_NUM'].values
Longitud = df_tiendas['LONGITUD_NUM'].values
N_Tiendas = len(Tiendas)
Volumen = np.random.uniform(0, 1, N_Tiendas)

data_tiendas = {'Tiendas': Tiendas, 'Latitud': Latitud, 'Longitud': Longitud}#, 'Volumen': Volumen}
df_plot = pd.DataFrame(data_tiendas)

# Crear gráfico
fig = px.scatter_mapbox(df_plot, lat="Latitud", lon="Longitud", zoom=10,
                        title='OXXO Tiendas', hover_name="Tiendas",
                        mapbox_style="open-street-map")#size='Volumen'

fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
fig.show()
