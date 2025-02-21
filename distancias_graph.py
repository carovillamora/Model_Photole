import osmnx as ox
import networkx as nx
import pandas as pd
import numpy as np
import time

inicio = time.time()
# Lectura del grafo
graph = ox.load_graphml("merida_general.graphml")

# Lectura de la base de datos
data = pd.read_csv("bachesInstances.csv")

# Funcion para calcular distancia entre dos puntos
def graph_distance(origin,destination):
    # Calcular nodos más cercanos al punto de origen dentro del grafo
    nodo_o = ox.distance.nearest_nodes(graph, X=origin[1], Y=origin[0])
    # Calcular nodos más cercanos al punto de destino dentro del grafo
    nodo_d = ox.distance.nearest_nodes(graph, X=destination[1], Y=destination[0])
    # Calcular la distancia del camino más corto entre los puntos
    km = nx.shortest_path_length(graph, nodo_o, nodo_d, weight="length")
    # Retornar la ddistancia
    return km

# Inicialización de matriz en ceros
dist = np.zeros((len(data),len(data)))

# Llenado de matriz de distancias
for i in range(len(data)):
    for j in range(len(data)):
        if i!=j:
            # Definición de puntos
            origin = (data.iloc[i]["LAT"], data.iloc[i]["LONG"])
            destination = (data.iloc[j]["LAT"], data.iloc[j]["LONG"])
            # Cálculo de la distancia del camino mas corto
            dist[i][j] = graph_distance(origin, destination)

# Guardar la matriz de distancias en un archivo CSV
df_distancias = pd.DataFrame(dist, index=data.index, columns=data.index)
df_distancias.to_csv("distancias_graph.csv", float_format="%.4f")

fin = time.time()
print(f"Tiempo de ejecución: {fin - inicio:.4f} segundos")