import { useEffect, useState } from 'react';
import { GoogleMap, Marker, InfoWindow, useJsApiLoader } from '@react-google-maps/api';
import Papa from 'papaparse';
import axios from 'axios';

const containerStyle = {
  width: '100%',
  height: '600px',
};

const center = {
  lat: 23.6345,
  lng: -102.5528,
};

type Prediction = {
  TIENDA_ID: number;
  VENTA_PRED: number;
  FECHA: string;
};

type StoreLocation = {
  TIENDA_ID: number;
  LATITUD_NUM: number;
  LONGITUD_NUM: number;
};

export default function ShowMapPrediction() {
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [locations, setLocations] = useState<StoreLocation[]>([]);
  const [selectedStore, setSelectedStore] = useState<number | null>(null);

  const { isLoaded } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY as string,
  });

  // Cargar predicciones del backend
  useEffect(() => {
    axios.get('/ruta/del/backend') // Cambia esta ruta por la real
      .then(res => setPredictions(res.data))
      .catch(err => console.error(err));
  }, []);

  // Cargar CSV y filtrar por tiendas presentes en las predicciones
  useEffect(() => {
    Papa.parse('/data/data_completa.csv', {
      download: true,
      header: true,
      complete: (results: any) => {
        const rows = results.data;
        const tiendasUnicas = new Set(predictions.map(p => p.TIENDA_ID));
        const filteredLocations = rows
          .filter((row: any) => tiendasUnicas.has(Number(row.TIENDA_ID)))
          .map((row: any) => ({
            TIENDA_ID: Number(row.TIENDA_ID),
            LATITUD_NUM: parseFloat(row.LATITUD_NUM),
            LONGITUD_NUM: parseFloat(row.LONGITUD_NUM),
          }));
        setLocations(filteredLocations);
      }
    });
  }, [predictions]);

  const renderMarkers = () => {
    return locations.map(loc => {
      const tiendaPreds = predictions.filter(p => p.TIENDA_ID === loc.TIENDA_ID);
      return (
        <Marker
          key={loc.TIENDA_ID}
          position={{ lat: loc.LATITUD_NUM, lng: loc.LONGITUD_NUM }}
          onClick={() => setSelectedStore(loc.TIENDA_ID)}
        >
          {selectedStore === loc.TIENDA_ID && (
            <InfoWindow onCloseClick={() => setSelectedStore(null)}>
              <div>
                <h3>Tienda {loc.TIENDA_ID}</h3>
                {tiendaPreds.map((pred, idx) => (
                  <p key={idx}>
                    {new Date(pred.FECHA).toLocaleDateString()}: ${pred.VENTA_PRED.toLocaleString()}
                  </p>
                ))}
              </div>
            </InfoWindow>
          )}
        </Marker>
      );
    });
  };

  return isLoaded ? (
    <GoogleMap mapContainerStyle={containerStyle} center={center} zoom={5}>
      {renderMarkers()}
    </GoogleMap>
  ) : <p>Cargando mapa...</p>;
}
