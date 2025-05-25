import './App.css';
import MapaConClick from './components/MapaConClick';

function AppPredictionPoint() {
  return (
    <div style={{ padding: '2rem' }}>
      <h1>Mapa Predictivo</h1>
      <p>Por favor seleccione un punto y se le proporcionara segun nuestro modelo si funcionara o no la tienda</p>
      <p>Esto en una escala de 0 a 1</p>
      <MapaConClick />
    </div>
  );
}

export default AppPredictionPoint;
