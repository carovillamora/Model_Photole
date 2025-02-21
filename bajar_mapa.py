import osmnx as ox
import matplotlib.pyplot as plt

##### MAPA GENERAL  #####
# Lugar necesario
place_name = "Municipio de Mérida"
# Carga la red de calles 
graph = ox.graph_from_place(place_name, network_type='drive')
# Guarda el grafo en formato .graphml
ox.save_graphml(graph, "merida_general.graphml")

##### MAPA CALLES PRINCIPALES #####
# Filtado de calles principlaes
edges_to_plot = [(u, v, k) for u, v, k, data in graph.edges(keys=True, data=True) if data.get("highway") == "trunk" or data.get("highway") == "primary" or data.get("highway") == "secondary"]
# Crea un subgrafo solo con las aristas filtradas
subgraph = graph.edge_subgraph(edges_to_plot)
# Guarda el grafo en formato .graphml
ox.save_graphml(subgraph, "merida_principales.graphml")

##### GRAFICAR #####
# Proyecta los grafos a una proyección adecuada
projected_graph = ox.project_graph(graph)
projected_subgraph = ox.project_graph(subgraph)
# Graficar el grafo general
fig, ax = plt.subplots(figsize=(10, 10))  # Establece el tamaño de la figura
ox.plot_graph(projected_graph, ax=ax, node_size=0, edge_linewidth=0.5, edge_color='blue')
# Muestra la visualización
plt.show()

# Graficar el grafo de vialidades principales
fig, ax = plt.subplots(figsize=(10, 10))  # Establece el tamaño de la figura
ox.plot_graph(projected_subgraph, ax=ax, node_size=0, edge_linewidth=0.5, edge_color='red')
# Muestra la visualización
plt.show()