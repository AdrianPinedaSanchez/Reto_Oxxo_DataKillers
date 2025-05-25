import { useState, useCallback } from 'react';
import {
  GoogleMap,
  useJsApiLoader,
} from '@react-google-maps/api';

type Coords = {
  lat: number;
  lng: number;
};

const containerStyle = {
  width: '100%',
  height: '400px',
};

const center = {
  lat: 19.4326,
  lng: -99.1332,
};

const isInMexico = (lat: number, lng: number): boolean => {
  return lat >= 14.5 && lat <= 32.7 && lng >= -118.5 && lng <= -86.5;
};


const verificarAguaEnUbicacion = async (lat: number, lng: number): Promise<boolean> => {
  const url = `http://localhost:8000/elevation?lat=${lat}&lng=${lng}`;
  try {
    const res = await fetch(url);
    const data = await res.json();
    if (data.status === "OK" && data.results.length > 0) {
      const elevation = data.results[0].elevation;
      return elevation <= 0.5;
    } else {
      console.error("Error en Elevation API:", data.status);
      return false;
    }
  } catch (error) {
    console.error("Error al consultar Elevation API:", error);
    return false;
  }
};


const MapaConClick = () => {
  const [coords, setCoords] = useState<Coords | null>(null);
  const [resultado, setResultado] = useState<any>(null);

  const { isLoaded } = useJsApiLoader({
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY as string
  });

  const fetchResultado = async (lat: number, lng: number) => {
    try {
      const res = await fetch(`http://localhost:8000/predict?lat=${lat}&lng=${lng}`);
      const data = await res.json();
      setResultado(data);
    } catch (error) {
      console.error("Error al obtener el resultado del modelo", error);
    }
  };

const onMapClick = useCallback(async (event: google.maps.MapMouseEvent) => {
  if (event.latLng) {
    const lat = event.latLng.lat();
    const lng = event.latLng.lng();
    setCoords({ lat, lng });

    if (!isInMexico(lat, lng)) {
      setResultado({
        lat,
        lng,
        result: "Ubicación fuera de México ❌",
        hayAgua: null,
        mensaje: "Ubicación fuera de México ❌"
      });
      return;
    }

    fetchResultado(lat, lng); // tu modelo

    const hayAgua = await verificarAguaEnUbicacion(lat, lng);

    setResultado(prev => ({
      ...prev,
      hayAgua,
      result: hayAgua ? 0 : prev.result,
    }));
  }
}, []);


  if (!isLoaded) return <div>Cargando mapa...</div>;




  return (
    <div>
      <GoogleMap
        mapContainerStyle={containerStyle}
        center={center}
        zoom={12}
        onClick={onMapClick}
      />
      <div style={{ marginTop: '20px' }}>
        {coords && (
          <>
            <p><strong>Latitud:</strong> {coords.lat}</p>
            <p><strong>Longitud:</strong> {coords.lng}</p>
          </>
        )}
        {resultado && (
          <>
            <h3>Resultado del Modelo:</h3>
            <p><strong>latitud:</strong> {resultado.lat}</p>
            <p><strong>longitud:</strong> {resultado.lng}</p>

            <p><strong>Puntuación:</strong> {resultado.result}</p>
            <p><strong>¿Hay agua en esta ubicación?</strong> {resultado.hayAgua ? 'Sí 💧' : 'No 🌍'}</p>
          </>
        )}
        
      </div>
    </div>
  );
};

export default MapaConClick;
