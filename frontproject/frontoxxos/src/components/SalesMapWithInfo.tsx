 // src/components/SalesMapWithInfo.tsx
import {
  GoogleMap,
  Marker,
  InfoWindow,
  useJsApiLoader
} from '@react-google-maps/api';
import Papa from 'papaparse';
import { useEffect, useState } from 'react';

type LocationData = {
  lat: number;
  lng: number;
  venta: number;
  tienda: string;
  fecha: string;
  direccion: string;
  ciudad: string;
};

const containerStyle = {
  width: '100%',
  height: '600px'
};

const center = {
  lat: 19.4326,
  lng: -99.1332
};

const SalesMapWithInfo = () => {
  const [locations, setLocations] = useState<LocationData[]>([]);
  const [selected, setSelected] = useState<LocationData | null>(null);

  const { isLoaded } = useJsApiLoader({
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY as string
  });

  useEffect(() => {
    Papa.parse('/data/data_completa.csv', {
      download: true,
      header: true,
      complete: (result: Papa.ParseResult<Record<string, string>>) => {
        const parsedData: LocationData[] = result.data
          .filter(row =>
            row['LATITUD_NUM'] &&
            row['LONGITUD_NUM'] &&
            row['VENTA_TOTAL']
          )
          .map(row => ({
            lat: parseFloat(row['LATITUD_NUM']),
            lng: parseFloat(row['LONGITUD_NUM']),
            venta: parseFloat(row['VENTA_TOTAL']),
            tienda: row['TIENDA_ID'],
            fecha: row['FECHA'],
            direccion: row['DIRECCION'] || 'Sin dirección',
            ciudad: row['CIUDAD'] || 'Sin ciudad'
          }));

        setLocations(parsedData);
      }
    });
  }, []);

  if (!isLoaded) return <div>Cargando mapa...</div>;

  return (
    <GoogleMap
      mapContainerStyle={containerStyle}
      center={center}
      zoom={8}
    >
      {locations.map((loc, idx) => (
        <Marker
          key={idx}
          position={{ lat: loc.lat, lng: loc.lng }}
          onClick={() => setSelected(loc)}
          icon={{
            path: google.maps.SymbolPath.CIRCLE,
            scale: Math.max(5, Math.log(loc.venta)),
            fillColor: '#4285F4',
            fillOpacity: 0.7,
            strokeWeight: 0
          }}
        />
      ))}

      {selected && (
        <InfoWindow
          position={{ lat: selected.lat, lng: selected.lng }}
          onCloseClick={() => setSelected(null)}
        >
          <div>
            <h2><strong>Tienda:</strong> {selected.tienda}</h2>
            <p><strong>Ventas:</strong> ${selected.venta.toFixed(2)}</p>
            <p><strong>Fecha:</strong> {selected.fecha}</p>
            <p><strong>Dirección:</strong> {selected.direccion}</p>
            <p><strong>Ciudad:</strong> {selected.ciudad}</p>
          </div>
        </InfoWindow>
      )}
    </GoogleMap>
  );
};

export default SalesMapWithInfo;
