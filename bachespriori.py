import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import random
import math
import time  # Importar la librería time para medir el tiempo

# Cargar los datos
df = pd.read_csv("E:/MMOP/LRP2/Nueva carpeta/dataframe.csv")  # Datos de los baches
distancias = pd.read_csv("E:/MMOP/LRP2/Nueva carpeta/distancias_graph.csv", index_col=0)  # Matriz de distancias

# Convertir los índices de la matriz de distancias a enteros
distancias.index = distancias.index.astype(int)
distancias.columns = distancias.columns.astype(int)

# Excluir el depósito (ID = 0) del clustering, pero mantenerlo en el DataFrame
clientes = df[df["Unnamed: 0"] != 0].copy()  # Crear una copia explícita

# Normalizar las coordenadas y las prioridades
scaler = StandardScaler()
coordenadas_prioridades = clientes[["LAT", "LONG", "Priority"]]  # Asegúrate de que "Priority" es el nombre correcto de la columna
coordenadas_prioridades_normalizadas = scaler.fit_transform(coordenadas_prioridades)

# Aplicar K-Means con las características combinadas
kmeans = KMeans(n_clusters=4, random_state=42, n_init=13)
clientes["Cluster"] = kmeans.fit_predict(coordenadas_prioridades_normalizadas)

# Asignar los clusters al DataFrame original (incluyendo el depósito)
df = df.merge(clientes[["Unnamed: 0", "Cluster"]], on="Unnamed: 0", how="left")

# Función para calcular la suma de prioridades por cluster
def calcular_suma_prioridades(df, cluster_id):
    return df[df["Cluster"] == cluster_id]["Priority"].sum()

# Calcular la suma de prioridades para cada cluster
suma_prioridades = {cluster_id: calcular_suma_prioridades(df, cluster_id) for cluster_id in range(4)}

# Mostrar las sumas de prioridades
print("Suma de prioridades por cluster antes del ajuste:", suma_prioridades)

# Ajustar los clusters para equilibrar las prioridades
for _ in range(100):  # Número máximo de iteraciones para ajustar
    # Encontrar el cluster con la mayor y menor suma de prioridades
    cluster_max = max(suma_prioridades, key=suma_prioridades.get)
    cluster_min = min(suma_prioridades, key=suma_prioridades.get)
    
    # Encontrar un cliente en el cluster_max que pueda ser movido al cluster_min
    clientes_en_cluster_max = df[df["Cluster"] == cluster_max]
    cliente_a_mover = clientes_en_cluster_max.sample(1).iloc[0]
    
    # Mover el cliente al cluster_min
    df.loc[df["Unnamed: 0"] == cliente_a_mover["Unnamed: 0"], "Cluster"] = cluster_min
    
    # Recalcular las sumas de prioridades
    suma_prioridades[cluster_max] = calcular_suma_prioridades(df, cluster_max)
    suma_prioridades[cluster_min] = calcular_suma_prioridades(df, cluster_min)
    
    # Verificar si las sumas están equilibradas
    if max(suma_prioridades.values()) - min(suma_prioridades.values()) < 0.5:  # Umbral de diferencia
        break

# Mostrar las sumas de prioridades después del ajuste
print("Suma de prioridades por cluster después del ajuste:", suma_prioridades)

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
output_path = "E:/MMOP/LRP2/Nueva carpeta/rutas_priori.csv"
df_rutas_nuevo.to_csv(output_path, index=False)

# Devolver la ruta del archivo generado
output_path