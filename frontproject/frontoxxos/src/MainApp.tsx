// src/MainApp.tsx
import App from './App';
import AppPredictionPoint from './AppPredictionPoint';

function MainApp() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column'}}>
      <App />
      <AppPredictionPoint />
    </div>
  );
}

export default MainApp;
