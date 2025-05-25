// components/showdata.tsx
import React, { useEffect, useState } from "react";
import Papa from "papaparse";

type DataRow = {
  TIENDA_ID: string;
  MES_ID: string;
  VENTA_TOTAL: string;
  FECHA: string;
  LATITUD_NUM: string;
  LONGITUD_NUM: string;
  PLAZA_CVE: string;
  NIVELSOCIOECONOMICO_DES: string;
  ENTORNO_DES: string;
  MTS2VENTAS_NUM: string;
  PUERTASREFRIG_NUM: string;
  CAJONESESTACIONAMIENTO_NUM: string;
  SEGMENTO_MAESTRO_DESC: string;
  LID_UBICACION_TIENDA: string;
  DATASET: string;
};

const Showdata: React.FC = () => {
  const [data, setData] = useState<DataRow[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Cambia esta ruta si tu build requiere otro path, aquí se asume que el CSV está en public/data
    fetch("../data/data_completa.csv")
      .then((response) => {
        if (!response.ok) throw new Error("No se pudo cargar el archivo CSV");
        return response.text();
      })
      .then((csvText) => {
        const results = Papa.parse<DataRow>(csvText, {
          header: true,
          skipEmptyLines: true,
        });
        if (results.errors.length) {

          setError("Error al parsear CSV: " + results.errors[0].message+csvText);
        } else {
          setData(results.data);
        }
      })
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <div>Error: {error}</div>;

  if (data.length === 0) return <div>Cargando datos...</div>;

  return (
    <div>
      <h2>Datos del CSV</h2>
      <table border={1} style={{ borderCollapse: "collapse", width: "100%" }}>
        <thead>
          <tr>
            {Object.keys(data[0]).map((key) => (
              <th key={key} style={{ padding: "4px" }}>{key}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={idx}>
              {Object.values(row).map((val, i) => (
                <td key={i} style={{ padding: "4px" }}>{val}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Showdata;
