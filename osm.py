import pandas as pd
import time

inicio = time.time()

# Lectura del archivo CSV 'rutas.csv'
data = pd.read_csv('E:/MMOP/LRP2/Nueva carpeta/rutas_priori.csv', header=0, names=['vuelta', 'lat', 'lot'])

# Definir las coordenadas de la panadería (depósito) como punto de origen y destino para las rutas
depot = "20.98180316475204,-89.66551613593404"

# Crear una lista para almacenar los enlaces
links = []

# Iterar sobre cada vuelta única en el archivo CSV
for j in data['vuelta'].unique():
    # Lista para los puntos de paso (waypoints)
    waypoints = []
    
    # Iterar sobre todas las filas del archivo 'data' para agregar los waypoints correspondientes a la ruta
    for i in range(len(data)):
        # Si la vuelta de la fila i coincide con la vuelta j
        if data.iloc[i]['vuelta'] == j:
            # Obtener las coordenadas latitud y longitud de la fila
            a = str(data.iloc[i]['lat'])
            b = str(data.iloc[i]['lot'])
            # Cadena con las coordenadas lat, lon en el formato requerido
            c = f"{a},{b}"
            # Añadir el punto de paso a la lista de waypoints
            waypoints.append(c)

    # Convertir la lista de waypoints en una cadena de texto, separando los puntos con '&point='
    res = '&point='.join(waypoints)
    
    # Link final de GraphHopper con todos los waypoints
    link = f"https://graphhopper.com/maps/?point={depot}&point={res}&point={depot}&vehicle=car&locale=es"
    
    # Agregar el enlace generado a la lista 'links'
    links.append(link)

    # Crear un archivo HTML para cada vuelta con el enlace de redirección
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta http-equiv="refresh" content="0; url={link}">
        <title>Redirigiendo a la Ruta {j}</title>
    </head>
    <body>
        Si no eres redirigido automáticamente, <a href="{link}">haz clic aquí</a>.
    </body>
    </html>
    """
    
    # Guardar el archivo HTML con un nombre basado en la vuelta
    with open(f"vuelta_{j+1}_priori_graphhopper.html", "w") as file:
        file.write(html_content)

# Calcular el tiempo de ejecución
fin = time.time()
print(f"Tiempo de ejecución: {fin-inicio:.4f} segundos")