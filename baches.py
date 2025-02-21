import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import random
import math
import time

# Cargar los datos
df = pd.read_csv("E:/MMOP/LRP2/Nueva carpeta/dataframe.csv")  # Datos de los baches
distancias = pd.read_csv("E:/MMOP/LRP2/Nueva carpeta/distancias_graph.csv", index_col=0)  # Matriz de distancias

# Convertir los índices de la matriz de distancias a enteros
distancias.index = distancias.index.astype(int)
distancias.columns = distancias.columns.astype(int)

# Excluir el depósito (ID = 0) del clustering, pero mantenerlo en el DataFrame
clientes = df[df["Unnamed: 0"] != 0].copy()  # Crear una copia explícita
coordenadas = clientes[["LAT", "LONG"]]  # Usar solo las coordenadas de los clientes

# Aplicar K-Means para crear 4 clusters (solo en los clientes, excluyendo el depósito)
kmeans = KMeans(n_clusters=4, random_state=42, n_init=13)
clientes["Cluster"] = kmeans.fit_predict(coordenadas)

# Asignar los clusters al DataFrame original (incluyendo el depósito)
df = df.merge(clientes[["Unnamed: 0", "Cluster"]], on="Unnamed: 0", how="left")

# Diccionario para guardar submatrices
submatrices = {}

for cluster_id in range(4):
    clientes_en_cluster = df[df["Cluster"] == cluster_id]["Unnamed: 0"].tolist()
    
    # Asegurar que el depósito (0) está en la submatriz
    clientes_validos = [c for c in clientes_en_cluster if c in distancias.index]
    clientes_validos.append(0)  # Añadir el depósito
    
    if clientes_validos:
        submatrices[cluster_id] = distancias.loc[clientes_validos, clientes_validos]

# Capacidad del vehículo
capacidad_vehiculo = 6

# Función para calcular el costo de una solución (distancia total)
def calcular_costo(rutas, submatriz):
    distancia_total = 0
    for ruta in rutas:
        if len(ruta) > 2:
            d_inicio = submatriz.loc[0, ruta[1]]  # Distancia del depósito al primer cliente
            d_fin = submatriz.loc[ruta[-2], 0]  # Distancia del último cliente al depósito
            
            distancia_total += d_inicio
            for i in range(1, len(ruta) - 1):
                distancia_total += submatriz.loc[ruta[i], ruta[i + 1]]
            distancia_total += d_fin
    return distancia_total

def generar_solucion_inicial(submatriz):
    ruta = [0]  # Comienza en el depósito
    clientes_restantes = [c for c in submatriz.index.tolist() if c != 0]
    
    while clientes_restantes:
        ultimo_nodo = ruta[-1]
        cliente_mas_cercano = min(clientes_restantes, key=lambda c: submatriz.loc[ultimo_nodo, c], default=None)
        
        if cliente_mas_cercano is None:
            break
        else:
            ruta.append(cliente_mas_cercano)
            clientes_restantes.remove(cliente_mas_cercano)
    
    ruta.append(0)  # Regresar al depósito
    return ruta

def generar_vecino(ruta):
    nueva_ruta = ruta.copy()
    if len(nueva_ruta) > 3:
        i, j = random.sample(range(1, len(nueva_ruta) - 1), 2)
        nueva_ruta[i], nueva_ruta[j] = nueva_ruta[j], nueva_ruta[i]
    return nueva_ruta

def recocido_simulado(submatriz, max_iteraciones=1000):
    solucion_actual = generar_solucion_inicial(submatriz)
    distancia_actual = calcular_costo([solucion_actual], submatriz)
    
    mejor_solucion = solucion_actual
    mejor_distancia = distancia_actual
    
    temperatura = 10000
    enfriamiento = 0.98
    
    for _ in range(max_iteraciones):
        solucion_vecina = generar_vecino(solucion_actual)
        distancia_vecina = calcular_costo([solucion_vecina], submatriz)
        
        delta = distancia_vecina - distancia_actual
        if delta < 0 or random.random() < math.exp(-delta / temperatura):
            solucion_actual, distancia_actual = solucion_vecina, distancia_vecina
            if distancia_actual < mejor_distancia:
                mejor_solucion, mejor_distancia = solucion_actual, distancia_actual
        
        temperatura *= enfriamiento
    print("  La temperatura final es: ", temperatura)
    
    return mejor_solucion, mejor_distancia

# Resolver el CVRP para cada cluster usando Recocido Simulado
rutas_por_cluster = {}
prioridades_por_vehiculo = {}
tiempos_por_vehiculo = {}  # Diccionario para almacenar los tiempos de ejecución

df_indexado = df.set_index("Unnamed: 0")

distancia_total = 0
for cluster_id, submatriz in submatrices.items():
    # Medir el tiempo de ejecución del recocido simulado
    inicio_tiempo = time.time()
    ruta, distancia = recocido_simulado(submatriz)
    fin_tiempo = time.time()
    
    tiempo_ejecucion = fin_tiempo - inicio_tiempo
    tiempos_por_vehiculo[cluster_id] = tiempo_ejecucion
    
    rutas_por_cluster[cluster_id] = ruta
    distancia_total += distancia
    
    # Calcular la suma de prioridades para este vehículo
    suma_prioridades = sum(df_indexado.loc[nodo, "Priority"] for nodo in ruta if nodo != 0)
    prioridades_por_vehiculo[cluster_id] = suma_prioridades
    
    print(f"Vehículo {cluster_id + 1} -> Ruta: {ruta}")
    print(f"  Distancia: {distancia}")
    print(f"  Suma de prioridades: {suma_prioridades}")
    print(f"  Tiempo de ejecución: {tiempo_ejecucion:.4f} segundos\n")

print(f"Distancia total recorrida: {distancia_total}")

# Lista para almacenar las rutas formateadas
rutas_formateadas = []

# Generar las rutas en el formato adecuado
for vehiculo, ruta in rutas_por_cluster.items():
    for nodo in ruta:
        if nodo in df.index:
            lat, lon = df.loc[nodo, ["LAT", "LONG"]]
            rutas_formateadas.append({"vuelta": vehiculo, "lat": lat, "lon": lon})
        else:
            print(f"Advertencia: El nodo {nodo} no está en el DataFrame.")

# Crear DataFrame con las rutas
df_rutas_nuevo = pd.DataFrame(rutas_formateadas)

# Guardar en un nuevo archivo CSV
output_path = "E:/MMOP/LRP2/Nueva carpeta/rutas_nuevas.csv"
df_rutas_nuevo.to_csv(output_path, index=False)

# Devolver la ruta del archivo generado
output_path