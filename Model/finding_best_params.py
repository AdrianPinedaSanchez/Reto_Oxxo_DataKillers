import json
import pandas as pd
import matplotlib.pyplot as plt

def analizar_resultados(json_path='performance_tracking.json', output_params='mejores_parametros.json'):
    # Cargar resultados
    with open(json_path, 'r') as f:
        resultados = json.load(f)

    df = pd.DataFrame(resultados)
    df['index'] = range(len(df))

    # Encontrar el mínimo MAPE test
    idx_min = df['mape_test'].idxmin()
    best_row = df.loc[idx_min]

    print("Mejor resultado por MAPE en test:")
    print(f" MAPE test: {best_row['mape_test']:.2f}%")
    print(f" MAPE train: {best_row['mape_train']:.2f}%")
    print(f" MAE test: {best_row['mae_test']:.2f}")
    print(f" MAE train: {best_row['mae_train']:.2f}")
    print(" Parámetros óptimos:")
    for k, v in best_row['params'].items():
        print(f"   {k}: {v}")

    # Guardar mejores parámetros
    with open(output_params, 'w') as f_out:
        json.dump(best_row['params'], f_out, indent=4)
    print(f"\n Parámetros guardados en '{output_params}'")

    # Gráfica MAPE
    plt.figure(figsize=(10, 5))
    plt.plot(df['index'], df['mape_train'], label='MAPE Train', marker='o')
    plt.plot(df['index'], df['mape_test'], label='MAPE Test', marker='x')
    plt.xlabel('Combinación de parámetros')
    plt.ylabel('MAPE (%)')
    plt.title('MAPE vs Combinaciones de Parámetros')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Gráfica MAE
    plt.figure(figsize=(10, 5))
    plt.plot(df['index'], df['mae_train'], label='MAE Train', marker='o')
    plt.plot(df['index'], df['mae_test'], label='MAE Test', marker='x')
    plt.xlabel('Combinación de parámetros')
    plt.ylabel('MAE')
    plt.title('MAE vs Combinaciones de Parámetros')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return best_row['params']

# Llamada
mejores_parametros = analizar_resultados('performance_tracking.json', 'mejores_parametros.json')
