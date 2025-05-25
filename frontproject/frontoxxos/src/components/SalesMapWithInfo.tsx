import {
  GoogleMap,
  Marker,
  InfoWindow,
  useJsApiLoader,
  MarkerClusterer
} from '@react-google-maps/api';
import Papa from 'papaparse';
import { useEffect, useState } from 'react';

type LocationData = {
  lat: number;
  lng: number;
  venta: number;
  tienda: string;
  fecha: string;
  mapetest: number;
  maetest:number;
};

const containerStyle = {
  width: '90vw',
  height: '600px', // O usa 100vh si quieres pantalla completa
};




const center = {
  lat: 25.5,
  lng: -99.5 
};


const SalesMapWithInfo = () => {
  const [locations, setLocations] = useState<Record<string, LocationData[]>>({});
  const [selected, setSelected] = useState<{ tienda: string; lat: number; lng: number } | null>(null);

  const { isLoaded } = useJsApiLoader({
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY as string
  });

  useEffect(() => {
    Papa.parse('/data/Forecast_2025-01.csv', {
      download: true,
      header: true,
      complete: (result: Papa.ParseResult<Record<string, string>>) => {
        const grouped: Record<string, LocationData[]> = {};

        result.data.forEach(row => {
          const lat = parseFloat(row['LATITUD_NUM']);
          const lng = parseFloat(row['LONGITUD_NUM']);
          const venta = parseFloat(row['VENTA_PRED']);
          const tienda = row['TIENDA_ID'];

          if (!isNaN(lat) && !isNaN(lng) && !isNaN(venta)) {
            const entry: LocationData = {
              lat,
              lng,
              venta,
              tienda,
              fecha: row['FECHA'],
              mapetest: parseFloat(row['mape_test']),
              maetest: parseFloat(row['mae_test'])
            };

            if (!grouped[tienda]) {
              grouped[tienda] = [];
            }
            grouped[tienda].push(entry);
          }
        });

        setLocations(grouped);
      }
    });
  }, []);

  if (!isLoaded) return <div>Cargando mapa...</div>;

  return (
    <GoogleMap
      mapContainerStyle={containerStyle}
      center={center}
      zoom={7}
    >
      <MarkerClusterer>
        {(clusterer) =>
          Object.entries(locations).map(([tienda, data]) => (
            <Marker
              key={tienda}
              position={{ lat: data[0].lat, lng: data[0].lng }}
              onClick={() => setSelected({ tienda, lat: data[0].lat, lng: data[0].lng })}
              clusterer={clusterer}
              icon={{
                path: google.maps.SymbolPath.CIRCLE,
                scale: Math.max(5, Math.log(data.reduce((sum, d) => sum + d.venta, 0) + 1) * 2),
                fillColor: '#4285F4',
                fillOpacity: 0.7,
                strokeWeight: 0,
              }}
            />
          ))
        }
      </MarkerClusterer>

      {selected && (
        <InfoWindow
          position={{ lat: selected.lat, lng: selected.lng }}
          onCloseClick={() => setSelected(null)}
        >
          <div style={{ maxHeight: '200px', overflowY: 'auto', width: '300px', color: 'black'}}>
            <h2><strong>Tienda:</strong> {selected.tienda}</h2>
            {locations[selected.tienda].map((entry, idx) => (
              <div key={idx} style={{ borderBottom: '1px solid #ccc', marginBottom: '8px'}}>
                <p><strong>Fecha:</strong> {entry.fecha}</p>
                <p><strong>Ventas:</strong> {entry.venta.toLocaleString('es-MX', { style: 'currency', currency: 'MXN' })}</p>
              </div>
            ))}
          </div>
        </InfoWindow>
      )}
    </GoogleMap>
  );
};

export default SalesMapWithInfo;
