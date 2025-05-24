import numpy as np
import pandas as pd
import plotly.express as px

data=pd.read_csv(r'C:\Users\cabal\Desktop\Datathon2025\data_completa.csv')
df = pd.DataFrame(data)

df['FECHA'] = pd.to_datetime(df['FECHA']) 
df.rename(columns={'LATITUD_NUM': 'Latitud', 'LONGITUD_NUM': 'Longitud'}, inplace=True)
df['Fecha_str'] = df['FECHA'].dt.strftime('%Y-%m')  # Para usar como frame de animación

fig = px.scatter_mapbox(df,
                        lat="Latitud",
                        lon="Longitud",
                        size="VENTA_TOTAL",
                        color="VENTA_TOTAL",
                        hover_name="TIENDA_ID",
                        animation_frame="Fecha_str",
                        zoom=8,
                        mapbox_style="open-street-map",
                        title="Animación de Ventas Totales por Tienda OXXO")

fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
fig.show()