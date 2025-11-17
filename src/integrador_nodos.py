from typing import Dict, List
import networkx as nx
import osmnx as ox

from clases import Nodo

class IntegradorNodos:

    
    @staticmethod
    def obtener_nodos_santander() -> List[Nodo]:

        zonas = {
            'parcelas': [
                {'id': 'P001', 'nombre': 'Finca Los Manzanos - Bosconia', 'lat': 7.1500, 'lon': -73.0800, 'prod': 180},
                {'id': 'P002', 'nombre': 'Huerto El Cacique - Suratá', 'lat': 7.1700, 'lon': -73.0650, 'prod': 220},
                {'id': 'P003', 'nombre': 'Finca La Esperanza - Pantano', 'lat': 7.1800, 'lon': -73.1100, 'prod': 150},
                
                {'id': 'P004', 'nombre': 'Finca Villa Rosario - Altos de Floridablanca', 'lat': 7.0800, 'lon': -73.0500, 'prod': 280},
                {'id': 'P005', 'nombre': 'Huerto San José - Vereda Ruitoque', 'lat': 7.0950, 'lon': -73.0700, 'prod': 240},
                {'id': 'P006', 'nombre': 'Finca El Vergel - Cañaveral', 'lat': 7.0650, 'lon': -73.0600, 'prod': 200},
                
                {'id': 'P007', 'nombre': 'Finca Las Delicias - La Cumbre', 'lat': 7.0100, 'lon': -73.0450, 'prod': 190},
                {'id': 'P008', 'nombre': 'Huerto San Rafael - El Rasgón', 'lat': 6.9950, 'lon': -73.0500, 'prod': 210},
                
                {'id': 'P009', 'nombre': 'Finca El Pomar - Lagos del Cacique', 'lat': 7.1100, 'lon': -73.0900, 'prod': 160},
                {'id': 'P010', 'nombre': 'Huerto Santa Rita - Morrorico', 'lat': 7.0900, 'lon': -73.0850, 'prod': 175},
                
                {'id': 'P011', 'nombre': 'Finca Los Arrayanes - Café Madrid', 'lat': 7.1350, 'lon': -73.1050, 'prod': 165},
                {'id': 'P012', 'nombre': 'Huerto El Poblado - Zona Norte', 'lat': 7.1450, 'lon': -73.1150, 'prod': 185},
            ],
            
            'centros': [
                {'id': 'C001', 'nombre': 'Centroabastos Bucaramanga', 'lat': 7.1250, 'lon': -73.1100},
                {'id': 'C002', 'nombre': 'Plaza Guarín - Centro Histórico', 'lat': 7.1300, 'lon': -73.1250},
                {'id': 'C003', 'nombre': 'Centro de Acopio Cabecera', 'lat': 7.1100, 'lon': -73.1200},
                
                {'id': 'C004', 'nombre': 'Acopio Cañaveral', 'lat': 7.0700, 'lon': -73.0650},
                {'id': 'C005', 'nombre': 'Centro de Distribución Lagos 2', 'lat': 7.0850, 'lon': -73.0900},
            ],
            
            'plantas': [
                {'id': 'PL001', 'nombre': 'Procesadora de Frutas Santander - Zona Industrial', 'lat': 7.1350, 'lon': -73.1300},
                {'id': 'PL002', 'nombre': 'Planta de Jugos Naturales - Girardot', 'lat': 7.1200, 'lon': -73.1150},
                
                {'id': 'PL003', 'nombre': 'Agroindustrial El Bosque', 'lat': 7.0650, 'lon': -73.0750},
                {'id': 'PL004', 'nombre': 'Procesadora de Manzanas Floridablanca', 'lat': 7.0800, 'lon': -73.0800},
            ]
        }
        
        nodos = []
        
        for parcela in zonas['parcelas']:
            nodos.append(Nodo(
                id=parcela['id'],
                nombre=parcela['nombre'],
                tipo='parcela',
                latitud=parcela['lat'],
                longitud=parcela['lon'],
                produccion_esperada=parcela['prod'] 
            ))
        
        for centro in zonas['centros']:
            nodos.append(Nodo(
                id=centro['id'],
                nombre=centro['nombre'],
                tipo='centro',
                latitud=centro['lat'],
                longitud=centro['lon']
            ))
        
        for planta in zonas['plantas']:
            nodos.append(Nodo(
                id=planta['id'],
                nombre=planta['nombre'],
                tipo='planta',
                latitud=planta['lat'],
                longitud=planta['lon']
            ))
        
        return nodos
    
    @staticmethod
    def conectar_nodos_a_red_vial(
        nodos_santander: List[Nodo],
        G_vial: nx.MultiDiGraph
    ) -> Dict[str, int]:

        
        conexiones = {}
        
        for nodo in nodos_santander:
            nodo_vial_cercano = ox.distance.nearest_nodes(
                G_vial,
                nodo.longitud,
                nodo.latitud
            )
            
            lat_vial = G_vial.nodes[nodo_vial_cercano]['y']
            lon_vial = G_vial.nodes[nodo_vial_cercano]['x']
            
            distancia = ox.distance.great_circle(
                nodo.latitud, nodo.longitud,
                lat_vial, lon_vial
            )
            
            nodo.nodo_vial_cercano = nodo_vial_cercano
            nodo.distancia_a_vial = distancia / 1000 
            
            conexiones[nodo.id] = nodo_vial_cercano
            
            emoji = {'parcela': '🌳', 'centro': '🏪', 'planta': '🏭'}[nodo.tipo]
            tipo_texto = {
                'parcela': 'Finca', 
                'centro': 'Acopio', 
                'planta': 'Planta'
            }[nodo.tipo]
            
            print(f"{emoji} {nodo.id:5} ({tipo_texto:6}) → Nodo vial {nodo_vial_cercano} ({distancia:.0f}m)")
        
        print(f"\n {len(conexiones)} nodos de producción conectados a la red vial")
        print(f"    {sum(1 for n in nodos_santander if n.tipo == 'parcela')} fincas productoras")
        print(f"    {sum(1 for n in nodos_santander if n.tipo == 'centro')} centros de acopio")
        print(f"    {sum(1 for n in nodos_santander if n.tipo == 'planta')} plantas procesadoras")
        
        return conexiones