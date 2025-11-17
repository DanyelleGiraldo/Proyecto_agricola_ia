from typing import Optional
import networkx as nx
import osmnx as ox


class DescargadorRedVial:
    
    @staticmethod
    def descargar_red_bucaramanga(
        lugar: str = "Santander, Colombia",
        tipo_red: str = "drive",
        guardar: bool = True,
        incluir_floridablanca: bool = True
    ) -> nx.MultiDiGraph:

        print(f" Tipo de red: {tipo_red}")
        print(f"\n Descargando desde OpenStreetMap...")
        
        try:
            if not incluir_floridablanca:
                G = ox.graph_from_place(lugar, network_type=tipo_red)
            
            else:

                bbox = (7.20, 7.00, -73.04, -73.18)
                
                print(f"    Usando bbox: Norte={bbox[0]}, Sur={bbox[1]}")
                print(f"                   Este={bbox[2]}, Oeste={bbox[3]}")
                print(f"     Cobertura: Bucaramanga + Floridablanca + zonas rurales")
                
                G = ox.graph_from_bbox(
                    north=bbox[0],
                    south=bbox[1],
                    east=bbox[2],
                    west=bbox[3],
                    network_type=tipo_red
                )
            
            G = ox.add_edge_speeds(G)
            G = ox.add_edge_travel_times(G)
            
            print(f"\nRED VIAL DESCARGADA EXITOSAMENTE")
            print(f"{'='*70}")
            print(f"    Nodos (intersecciones): {len(G.nodes):,}")
            print(f"    Aristas (calles): {len(G.edges):,}")
            
            total_km = sum(data.get('length', 0) for u, v, data in G.edges(data=True)) / 1000
            print(f"    Longitud total de calles: {total_km:,.1f} km")
            
            if guardar:
                archivo = "bucaramanga_floridablanca_red_vial_manzanas.graphml"
                ox.save_graphml(G, archivo)
                print(f"\nRed guardada en: {archivo}")
            
            return G
            
        except Exception as e:
            print(f"\n ERROR descargando red vial: {e}")
            print(f"   Intenta verificar tu conexión a internet")
            print(f"   o usar una red guardada previamente.")
            return None
    
    @staticmethod
    def cargar_red_guardada(
        archivo: str = "bucaramanga_floridablanca_red_vial_manzanas.graphml"
    ) -> Optional[nx.MultiDiGraph]:

        try:

            print(f"   Archivo: {archivo}")
            
            G = ox.load_graphml(archivo)
            
            print(f"\n Red vial cargada exitosamente")
            print(f"    Nodos: {len(G.nodes):,}")
            print(f"    Aristas: {len(G.edges):,}")
            
            return G
            
        except FileNotFoundError:
            print(f"\n Archivo no encontrado: {archivo}")
            print(f"   Debes descargar la red primero con descargar_red_bucaramanga()")
            return None
            
        except Exception as e:
            print(f"\n Error cargando red: {e}")
            return None
    
    @staticmethod
    def obtener_estadisticas_red(G: nx.MultiDiGraph):

        if G is None:
            print(" No hay red vial cargada")
            return
        
        
        print(f"\n Estructura:")
        print(f"   Intersecciones (nodos): {len(G.nodes):,}")
        print(f"   Calles (aristas): {len(G.edges):,}")
        
        total_km = sum(data.get('length', 0) for u, v, data in G.edges(data=True)) / 1000
        print(f"\n Dimensiones:")
        print(f"   Longitud total de calles: {total_km:,.1f} km")
        
        tipos_via = {}
        for u, v, data in G.edges(data=True):
            tipo = data.get('highway', 'unknown')
            if isinstance(tipo, list):
                tipo = tipo[0]
            tipos_via[tipo] = tipos_via.get(tipo, 0) + 1
        
        print(f"\n Tipos de vía:")
        for tipo, count in sorted(tipos_via.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {tipo}: {count:,} segmentos")
        
        velocidades = [data.get('speed_kph', 0) for u, v, data in G.edges(data=True)]
        if velocidades:
            print(f"\n Velocidades:")
            print(f"   Promedio: {sum(velocidades)/len(velocidades):.1f} km/h")
            print(f"   Mínima: {min(velocidades):.1f} km/h")
            print(f"   Máxima: {max(velocidades):.1f} km/h")