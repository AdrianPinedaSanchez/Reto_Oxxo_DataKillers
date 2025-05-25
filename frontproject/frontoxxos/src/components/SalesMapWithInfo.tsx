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
  plaza: string;
  segmento: string;
  entorno: string;
  nivelSocio: string;
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
    Papa.parse('/data/data_completa.csv', {
      download: true,
      header: true,
      complete: (result: Papa.ParseResult<Record<string, string>>) => {
        const grouped: Record<string, LocationData[]> = {};

        result.data.forEach(row => {
          const lat = parseFloat(row['LATITUD_NUM']);
          const lng = parseFloat(row['LONGITUD_NUM']);
          const venta = parseFloat(row['VENTA_TOTAL']);
          const tienda = row['TIENDA_ID'];

          if (!isNaN(lat) && !isNaN(lng) && !isNaN(venta)) {
            const entry: LocationData = {
              lat,
              lng,
              venta,
              tienda,
              fecha: row['FECHA'],
              plaza: row['PLAZA_CVE'],
              segmento: row['SEGMENTO_MAESTRO_DESC'],
              entorno: row['ENTORNO_DES'],
              nivelSocio: row['NIVELSOCIOECONOMICO_DES']
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
                <p><strong>Plaza:</strong> {entry.plaza}</p>
                <p><strong>Segmento:</strong> {entry.segmento}</p>
                <p><strong>Entorno:</strong> {entry.entorno}</p>
                <p><strong>Nivel socioeconómico:</strong> {entry.nivelSocio}</p>
              </div>
            ))}
          </div>
        </InfoWindow>
      )}
    </GoogleMap>
  );
};

export default SalesMapWithInfo;
