from menu import ControladorSistema


if __name__ == "__main__":
    print(f"""

CARACTERÍSTICAS PRINCIPALES:

1.  DESCARGA RED VIAL 
   • Usa OSMnx para obtener todas las calles de Bucaramanga
   • Miles de intersecciones y calles 
   • Información completa: distancias, velocidades, tiempos


ENTRENA IA CON RUTAS 
   • Calcula rutas sobre calles verdaderas
   • La IA aprende patrones de rutas 

VISUALIZACIÓN COMPLETA
   • Mapas interactivos con Folium
   • Muestra red vial + nodos + rutas
   • Zoom, capas, mediciones

""")
    
    controlador = ControladorSistema()
    controlador.menu_interactivo()