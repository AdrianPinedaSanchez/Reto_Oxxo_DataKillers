// // src/components/MapaConClick.tsx
// import { useState, useCallback } from 'react';
// import {
//   GoogleMap,
//   useJsApiLoader,
// } from '@react-google-maps/api';

// type Coords = {
//   lat: number;
//   lng: number;
// };

// const containerStyle = {
//   width: '100%',
//   height: '400px',
// };

// const center = {
//   lat: 19.4326, // Ciudad de México
//   lng: -99.1332,
// };

// const MapaConClick = () => {
//   const [coords, setCoords] = useState<Coords | null>(null);

//   const { isLoaded } = useJsApiLoader({
//     googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY as string
//   });

//   const onMapClick = useCallback((event: google.maps.MapMouseEvent) => {
//     if (event.latLng) {
//       setCoords({
//         lat: event.latLng.lat(),
//         lng: event.latLng.lng(),
//       });
//     }
//   }, []);

//   if (!isLoaded) return <div>Cargando mapa...</div>;

//   return (
//     <div>
//       <GoogleMap
//         mapContainerStyle={containerStyle}
//         center={center}
//         zoom={12}
//         onClick={onMapClick}
//       />
//       <div style={{ marginTop: '20px' }}>
//         {coords ? (
//           <>
//             <p><strong>Latitud:</strong> {coords.lat}</p>
//             <p><strong>Longitud:</strong> {coords.lng}</p>
//           </>
//         ) : (
//           <p>Haz clic en el mapa para obtener coordenadas</p>
//         )}
//       </div>
//     </div>
//   );
// };

// export default MapaConClick;

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

  const onMapClick = useCallback((event: google.maps.MapMouseEvent) => {
    if (event.latLng) {
      const lat = event.latLng.lat();
      const lng = event.latLng.lng();
      setCoords({ lat, lng });
      fetchResultado(lat, lng); // Llama a la API al hacer clic
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
          </>
        )}
      </div>
    </div>
  );
};

export default MapaConClick;
