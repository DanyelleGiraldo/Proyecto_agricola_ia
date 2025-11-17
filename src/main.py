from menu import ControladorSistema


if __name__ == "__main__":
    print(f"""

CARACTERÍSTICAS PRINCIPALES:

1.  DESCARGA RED VIAL REAL
   • Usa OSMnx para obtener todas las calles de Bucaramanga
   • Miles de intersecciones y calles reales
   • Información completa: distancias, velocidades, tiempos


ENTRENA IA CON RUTAS REALES
   • Calcula rutas sobre calles verdaderas
   • La IA aprende patrones de rutas reales

VISUALIZACIÓN COMPLETA
   • Mapas interactivos con Folium
   • Muestra red vial + nodos + rutas
   • Zoom, capas, mediciones

""")
    
    controlador = ControladorSistema()
    controlador.menu_interactivo()