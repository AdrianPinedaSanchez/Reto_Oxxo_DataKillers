import {
  GoogleMap,
  Marker,
  InfoWindow,
  useJsApiLoader,
  MarkerClusterer
} from '@react-google-maps/api';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';

import Papa from 'papaparse';
import { useEffect, useState } from 'react';

type LocationData = {
  lat: number;
  lng: number;
  venta: number;
  tienda: string;
  fecha: string;
  mapetest: number;
  maetest: number;
};

const containerStyle = {
  width: '90vw',
  height: '600px',
};

const center = {
  lat: 25.5,
  lng: -99.5
};

const SalesMapWithInfo = () => {
  const [newVenta, setNewVenta] = useState<number>(0); // Valor inicial 0
  const [isSubmitting, setIsSubmitting] = useState(false);
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
            if (!grouped[tienda]) grouped[tienda] = [];
            grouped[tienda].push(entry);
          }
        });
        setLocations(grouped);
      }
    });
  }, []);

  if (!isLoaded) return <div>Cargando mapa...</div>;

  return (
    <div>
      {/* Formulario de número
      <div style={{ marginBottom: '10px' }}>
        <input
          type="number"
          value={newVenta}
          onChange={(e) => {
            // Asegurarse que solo se guarde número entero o 0 si vacío
            const val = e.target.value;
            setNewVenta(val === '' ? 0 : parseInt(val, 10));
          }}
          placeholder="Ingresa un número entero"
          style={{
            padding: '6px',
            width: '200px',
            marginRight: '10px'
          }}
          min={0}
          step={1}
        />
        <button
          onClick={async () => {
            // Validación estricta de entero positivo
            if (!Number.isInteger(newVenta) || newVenta <= 0) {
              return alert('Ingresa un número entero válido mayor que cero');
            }

            setIsSubmitting(true);
            try {
              const response = await fetch(`http://localhost:8000/predictionFuture?valor=${newVenta}`);
              if (!response.ok) throw new Error('Error en el servidor');
              const data = await response.json();
              console.log('Respuesta del backend:', data);
              alert('Número enviado con éxito');
            } catch (error) {
              console.error(error);
              alert('Hubo un error al enviar el número');
            } finally {
              setIsSubmitting(false);
            }
          }}
          disabled={isSubmitting}
          style={{
            padding: '6px 12px',
            backgroundColor: '#4285F4',
            color: 'white',
            border: 'none',
            cursor: 'pointer'
          }}
        >
          {isSubmitting ? 'Enviando...' : 'Enviar'}
        </button>
      </div> */}

      {/* Mapa */}
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
    <div style={{ width: '300px', height: '250px', color: 'black' }}>
      <h3 style={{ textAlign: 'center' }}><strong>Tienda:</strong> {selected.tienda}</h3>
      <ResponsiveContainer width="100%" height="85%">
        <LineChart data={locations[selected.tienda]}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="fecha" tickFormatter={(str) => str.slice(5, 10)} />
          <YAxis tickFormatter={(val) => `${(val / 1000).toFixed(0)}k`} />
          <Tooltip formatter={(val: number) => `$${val.toLocaleString('es-MX')}`} />
          <Line type="monotone" dataKey="venta" stroke="#4285F4" strokeWidth={2} dot />
          <Line type="monotone" dataKey="mapetest" stroke="#FB8C00" strokeDasharray="5 5" />
          <Line type="monotone" dataKey="maetest" stroke="#43A047" strokeDasharray="5 5" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  </InfoWindow>
)}

      </GoogleMap>
    </div>
  );
};

export default SalesMapWithInfo;
