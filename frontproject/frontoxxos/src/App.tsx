// // src/App.tsx
// import SalesMapWithInfo from './components/SalesMapWithInfo';

// function App() {
//   return (
    
//     <div style={{ 
//   display: 'flex', 
//   flexDirection: 'column', 
//   justifyContent: 'center', 
//   alignItems: 'center', 
//   height: '100vh', // Esto asegura que el contenido esté centrado verticalmente
//   margin: 0, 
//   padding: 0
// }}>
//   <h1 style={{ textAlign: 'center', fontSize: '24px', fontWeight: 'bold', margin: '1rem 0' }}>
//     Mapa de Ventas por Tienda
//   </h1>
//   <SalesMapWithInfo />
// </div>

//   );
// }



// export default App;




//APP QUE MUESTRA LO DE CUANDO CLICKEAS
// src/App.tsx
// import './App.css';
// import MapaConClick from './components/MapaConClick';

// function App() {
//   return (
//     <div style={{ padding: '2rem' }}>
//       <h1>Mapa Interactivo con React y TypeScript</h1>
//       <MapaConClick />
//     </div>
//   );
// }

// export default App;



// src/App.tsx
import './App.css';
import ShowMapPrediction from './components/showMapPrediction';

function App() {
  return (
    <div>
      <h1>Predicción de Ventas por Tienda</h1>
      <ShowMapPrediction />
    </div>
  );
}

export default App;
