import folium
import pandas as pd
import osmnx as ox

#Lectura de la base de datos
data = pd.read_csv("bachesInstances.csv")
# Renombrar la columna 'Type' a 'Type by pothole'
data.rename(columns={'Type': 'Type by pothole'}, inplace=True)

# Lectura del grafo
graph = ox.load_graphml("Merida_principales.graphml")
# Listas contenedoras
dist_to_main = [] # Distancia hacia avenidas principales
type2 = [] # Tipo de bache por cercania a avenidas principales
priotity = [] # Prioridad ponderada por tipo de bache y cercania a avenidas principales
for i in range(len(data)):
    # Calculo de distancia entre nodo dentro del grafo y avenidas principales
    edge, dist = ox.distance.nearest_edges(graph, X = data.iloc[i]["LONG"], Y = data.iloc[i]["LAT"], return_dist=True)
    dist *= 100000
    # Agregar a la lista
    dist_to_main.append(int(dist))
    # Calcular tipo en función de la distancia
    if dist <= 50:
        p = 3
    elif 50 < dist <= 100:
        p = 2
    elif dist > 100:
        p = 1
    # Agregar a la lista
    type2.append(p)
    # Calculo de Prioridad ponderada
    prio = (p + data.iloc[i]["Type by pothole"])/5
    # Agregar a la lista
    priotity.append(prio)

# Agregar columnas
data["Dist to Main"] = dist_to_main 
data["Type by distance"] = type2
data["Priority"] = priotity

# Guardar csv
data.to_csv('dataframe.csv', index=True)

# Centro de la ciudad de Mérida
centro = [20.97537, -89.61696]
# Crear un mapa de Folium centrado en los datos
m = folium.Map(location=centro, zoom_start=12)

# Añadir los puntos al mapa (usando CircleMarker para representar mejor los puntos geográficos)
for i in range(0, len(data)):
    folium.Circle(
        location=[data.iloc[i]["LAT"], data.iloc[i]["LONG"]],  # Coordenadas del nodo (latitud, longitud)
        radius=5,  # Tamaño del círculo
        color="red" if i != 0 else "blue",
        fill=True,
        fill_color="red" if i != 0 else "blue"
    ).add_to(m)

    # Construir la información emergente (popup) con toda la información de la fila, excluyendo "Dist to Main"
    popup_info = f"ID: {i}<br>"
    for col in data.columns:
        if col != "Dist to Main":  # Excluir la columna "Dist to Main"
            popup_info += f"{col}: {data.iloc[i][col]}<br>"

    # Añadir el marcador con el popup al mapa
    folium.Marker(
        location=[data.iloc[i]["LAT"], data.iloc[i]["LONG"]],  # Coordenadas del nodo (latitud, longitud)
        popup=popup_info if i != 0 else "Deposito",  # Información emergente
        icon=folium.Icon(icon="glyphicon-exclamation-sign" if i != 0 else "glyphicon-home",
                         icon_color="white",
                         color="red" if i != 0 else "blue")  # Icono de advertencia o de depósito
    ).add_to(m)
# Guardar el mapa interactivo en un archivo HTML
m.save("fothole.html")