from typing import Optional
import networkx as nx
import osmnx as ox


class DescargadorRedVial:
    
    @staticmethod
    def descargar_red_washington_oregon(
        tipo_red: str = "drive",
        guardar: bool = True,
        zona: str = "completa"
    ) -> nx.MultiDiGraph:
        
        
        print(f"🗺️  Tipo de red: {tipo_red}")
        print(f"📍 Zona seleccionada: {zona}")
        print(f"\n📡 Descargando desde OpenStreetMap...")
        
        try:
            # Definir bounding boxes según la zona
            if zona == 'yakima':
                # Solo Yakima Valley (zona más productiva #1)
                north = 47.0
                south = 46.3
                east = -119.8
                west = -121.0
                descripcion = "Yakima Valley"
                
            elif zona == 'wenatchee':
                # Solo Wenatchee Valley (zona más productiva #2)
                north = 47.7
                south = 47.2
                east = -120.0
                west = -120.8
                descripcion = "Wenatchee Valley"
                
            elif zona == 'yakima-wenatchee':
                # Yakima + Wenatchee (zonas principales conectadas)
                north = 47.7
                south = 46.3
                east = -119.8
                west = -121.0
                descripcion = "Yakima y Wenatchee Valleys"
                
            else:  # 'completa'
                # Todo Washington (⚠️ MUY PESADO)
                north = 49.0
                south = 45.5
                east = -116.9
                west = -124.8
                descripcion = "Estado de Washington completo"
                print(f"\n⚠️  ADVERTENCIA: Descarga completa requiere 16+ GB RAM")
                print(f"    Esto puede tardar 10-30 minutos y trabar tu PC")
                print(f"    Recomendación: usa 'yakima-wenatchee' en su lugar")
            
            # bbox = (west, south, east, north) = (left, bottom, right, top)
            bbox = (west, south, east, north)
            
            print(f"\n    📍 Bbox: Norte={north}, Sur={south}")
            print(f"             Este={east}, Oeste={west}")
            print(f"    🌲 Cobertura: {descripcion}")
            
            # Descargar red vial
            G = ox.graph_from_bbox(
                bbox,
                network_type=tipo_red
            )
            
            # Agregar velocidades y tiempos de viaje
            G = ox.add_edge_speeds(G)
            G = ox.add_edge_travel_times(G)
            
            print(f"\n✅ RED VIAL DESCARGADA EXITOSAMENTE")
            print(f"{'='*70}")
            print(f"    🔵 Nodos (intersecciones): {len(G.nodes):,}")
            print(f"    🔗 Aristas (calles): {len(G.edges):,}")
            
            total_km = sum(data.get('length', 0) for u, v, data in G.edges(data=True)) / 1000
            print(f"    📏 Longitud total: {total_km:,.1f} km")
            
            if guardar:
                archivo = f"washington_{zona}_red_vial.graphml"
                ox.save_graphml(G, archivo)
                print(f"\n💾 Red guardada en: {archivo}")
            
            return G
            
        except Exception as e:
            print(f"\n❌ ERROR descargando red vial: {e}")
            print(f"   ⚠️  Si se quedó sin memoria, prueba con una zona más pequeña")
            print(f"   💡 Ejemplo: zona='yakima' en lugar de 'completa'")
            return None
    
    @staticmethod
    def cargar_red_guardada(
        archivo: str = "washington_completa_red_vial.graphml"
    ) -> Optional[nx.MultiDiGraph]:

        try:
            print(f"📂 Cargando red vial guardada...")
            print(f"   📄 Archivo: {archivo}")
            
            G = ox.load_graphml(archivo)
            
            print(f"\n✅ Red vial cargada exitosamente")
            print(f"    🔵 Nodos: {len(G.nodes):,}")
            print(f"    🔗 Aristas: {len(G.edges):,}")
            
            return G
            
        except FileNotFoundError:
            print(f"\n❌ Archivo no encontrado: {archivo}")
            print(f"   💡 Debes descargar la red primero con:")
            print(f"      descargar_red_washington(zona='yakima-wenatchee')")
            return None
            
        except Exception as e:
            print(f"\n❌ Error cargando red: {e}")
            return None
    
    @staticmethod
    def obtener_estadisticas_red(G: nx.MultiDiGraph):

        if G is None:
            print("❌ No hay red vial cargada")
            return
        
        print(f"\n📊 ESTADÍSTICAS DE LA RED VIAL")
        print(f"{'='*70}")
        
        print(f"\n🏗️  Estructura:")
        print(f"   🔵 Intersecciones (nodos): {len(G.nodes):,}")
        print(f"   🔗 Calles (aristas): {len(G.edges):,}")
        
        total_km = sum(data.get('length', 0) for u, v, data in G.edges(data=True)) / 1000
        print(f"\n📏 Dimensiones:")
        print(f"   🛣️  Longitud total de calles: {total_km:,.1f} km")
        
        tipos_via = {}
        for u, v, data in G.edges(data=True):
            tipo = data.get('highway', 'unknown')
            if isinstance(tipo, list):
                tipo = tipo[0]
            tipos_via[tipo] = tipos_via.get(tipo, 0) + 1
        
        print(f"\n🛤️  Tipos de vía:")
        for tipo, count in sorted(tipos_via.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   • {tipo}: {count:,} segmentos")
        
        velocidades = [data.get('speed_kph', 0) for u, v, data in G.edges(data=True)]
        if velocidades:
            print(f"\n🚗 Velocidades:")
            print(f"   📊 Promedio: {sum(velocidades)/len(velocidades):.1f} km/h")
            print(f"   🐌 Mínima: {min(velocidades):.1f} km/h")
            print(f"   🏎️  Máxima: {max(velocidades):.1f} km/h")

