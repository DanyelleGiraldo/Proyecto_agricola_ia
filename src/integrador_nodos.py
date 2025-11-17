from typing import Dict, List
import networkx as nx
import osmnx as ox

from clases import Nodo

class IntegradorNodos:

    
    @staticmethod
    def obtener_nodos_santander() -> List[Nodo]:

        zonas = {
            'parcelas': [
                # ZONA METROPOLITANA BUCARAMANGA
                {'id': 'P001', 'nombre': 'Finca Los Manzanos - Bosconia', 'lat': 7.1500, 'lon': -73.0800, 'prod': 180, 'mun': 'Bucaramanga'},
                {'id': 'P002', 'nombre': 'Huerto El Cacique - Suratá', 'lat': 7.1700, 'lon': -73.0650, 'prod': 220, 'mun': 'Bucaramanga'},
                {'id': 'P003', 'nombre': 'Finca La Esperanza - Pantano', 'lat': 7.1800, 'lon': -73.1100, 'prod': 150, 'mun': 'Bucaramanga'},
                {'id': 'P004', 'nombre': 'Finca Villa Rosario - Altos', 'lat': 7.0800, 'lon': -73.0500, 'prod': 280, 'mun': 'Floridablanca'},
                {'id': 'P005', 'nombre': 'Huerto San José - Ruitoque', 'lat': 7.0950, 'lon': -73.0700, 'prod': 240, 'mun': 'Floridablanca'},
                
                # PROVINCIA DE GARCÍA ROVIRA (Clima frío - alta producción)
                {'id': 'P006', 'nombre': 'Finca Las Nieves - Málaga', 'lat': 6.7000, 'lon': -72.7333, 'prod': 350, 'mun': 'Málaga'},
                {'id': 'P007', 'nombre': 'Huerto San Pablo - Concepción', 'lat': 6.7667, 'lon': -72.7000, 'prod': 320, 'mun': 'Concepción'},
                {'id': 'P008', 'nombre': 'Finca El Alto - Carcasí', 'lat': 6.6333, 'lon': -72.6333, 'prod': 280, 'mun': 'Carcasí'},
                {'id': 'P009', 'nombre': 'Huerto La Cumbre - San Andrés', 'lat': 6.8167, 'lon': -72.8500, 'prod': 300, 'mun': 'San Andrés'},
                {'id': 'P010', 'nombre': 'Finca El Bosque - Cerrito', 'lat': 6.8333, 'lon': -72.6833, 'prod': 260, 'mun': 'Cerrito'},
                
                # PROVINCIA DE SOTO (Zona cafetera - producción media)
                {'id': 'P011', 'nombre': 'Finca La Pradera - Piedecuesta', 'lat': 7.0833, 'lon': -73.0500, 'prod': 200, 'mun': 'Piedecuesta'},
                {'id': 'P012', 'nombre': 'Huerto El Roble - Girón', 'lat': 7.0667, 'lon': -73.1667, 'prod': 180, 'mun': 'Girón'},
                {'id': 'P013', 'nombre': 'Finca Las Acacias - Lebrija', 'lat': 7.1167, 'lon': -73.2167, 'prod': 220, 'mun': 'Lebrija'},
                {'id': 'P014', 'nombre': 'Huerto San Isidro - Rionegro', 'lat': 7.1500, 'lon': -73.1500, 'prod': 190, 'mun': 'Rionegro'},
                
                # PROVINCIA DE VÉLEZ (Templado - producción diversificada)
                {'id': 'P015', 'nombre': 'Finca El Paraíso - Vélez', 'lat': 6.0167, 'lon': -73.6667, 'prod': 240, 'mun': 'Vélez'},
                {'id': 'P016', 'nombre': 'Huerto La Samaria - Barbosa', 'lat': 5.9333, 'lon': -73.6167, 'prod': 210, 'mun': 'Barbosa'},
                {'id': 'P017', 'nombre': 'Finca Las Brisas - Guavatá', 'lat': 5.9500, 'lon': -73.7000, 'prod': 230, 'mun': 'Guavatá'},
                {'id': 'P018', 'nombre': 'Huerto El Mirador - Puente Nacional', 'lat': 5.8833, 'lon': -73.6833, 'prod': 195, 'mun': 'Puente Nacional'},
                
                # PROVINCIA DE GUANENTÁ (Altiplano - especializada)
                {'id': 'P019', 'nombre': 'Finca La Colina - San Gil', 'lat': 6.5500, 'lon': -73.1333, 'prod': 270, 'mun': 'San Gil'},
                {'id': 'P020', 'nombre': 'Huerto Los Pinos - Barichara', 'lat': 6.6333, 'lon': -73.2167, 'prod': 180, 'mun': 'Barichara'},
                {'id': 'P021', 'nombre': 'Finca El Descanso - Curití', 'lat': 6.6000, 'lon': -73.0667, 'prod': 220, 'mun': 'Curití'},
                {'id': 'P022', 'nombre': 'Huerto San Martín - Aratoca', 'lat': 6.7000, 'lon': -73.0167, 'prod': 200, 'mun': 'Aratoca'},
                
                # PROVINCIA DE COMUNERA (Sur - emergente)
                {'id': 'P023', 'nombre': 'Finca La Esperanza - El Guacamayo', 'lat': 6.2500, 'lon': -73.5000, 'prod': 160, 'mun': 'El Guacamayo'},
                {'id': 'P024', 'nombre': 'Huerto San Carlos - Charalá', 'lat': 6.2833, 'lon': -73.1500, 'prod': 175, 'mun': 'Charalá'},
                {'id': 'P025', 'nombre': 'Finca Los Laureles - Encino', 'lat': 6.1500, 'lon': -73.0833, 'prod': 190, 'mun': 'Encino'},
            ],
            
            'centros': [
                # Centros de Acopio Regionales
                {'id': 'C001', 'nombre': 'Centroabastos Bucaramanga', 'lat': 7.1250, 'lon': -73.1100, 'mun': 'Bucaramanga'},
                {'id': 'C002', 'nombre': 'Centro de Acopio Málaga', 'lat': 6.7000, 'lon': -72.7333, 'mun': 'Málaga'},
                {'id': 'C003', 'nombre': 'Centro de Acopio San Gil', 'lat': 6.5500, 'lon': -73.1333, 'mun': 'San Gil'},
                {'id': 'C004', 'nombre': 'Centro de Acopio Vélez', 'lat': 6.0167, 'lon': -73.6667, 'mun': 'Vélez'},
                {'id': 'C005', 'nombre': 'Centro de Acopio Barrancabermeja', 'lat': 7.0667, 'lon': -73.8500, 'mun': 'Barrancabermeja'},
                {'id': 'C006', 'nombre': 'Centro de Acopio Socorro', 'lat': 6.4667, 'lon': -73.2667, 'mun': 'Socorro'},
            ],
            
            'plantas': [
                # Plantas Procesadoras Estratégicas
                {'id': 'PL001', 'nombre': 'Procesadora Santander - B/manga', 'lat': 7.1350, 'lon': -73.1300, 'mun': 'Bucaramanga'},
                {'id': 'PL002', 'nombre': 'Planta de Jugos Málaga', 'lat': 6.7200, 'lon': -72.7500, 'mun': 'Málaga'},
                {'id': 'PL003', 'nombre': 'Procesadora San Gil', 'lat': 6.5600, 'lon': -73.1400, 'mun': 'San Gil'},
                {'id': 'PL004', 'nombre': 'Agroindustrial Vélez', 'lat': 6.0300, 'lon': -73.6700, 'mun': 'Vélez'},
            ],
            
            'mercados': [
                # Principales Mercados de Destino
                {'id': 'M001', 'nombre': 'Mercado Campesino B/manga', 'lat': 7.1300, 'lon': -73.1250, 'mun': 'Bucaramanga'},
                {'id': 'M002', 'nombre': 'Plaza de Mercado San Gil', 'lat': 6.5500, 'lon': -73.1333, 'mun': 'San Gil'},
                {'id': 'M003', 'nombre': 'Mercado Municipal Málaga', 'lat': 6.7000, 'lon': -72.7333, 'mun': 'Málaga'},
                {'id': 'M004', 'nombre': 'Mercado Vélez', 'lat': 6.0167, 'lon': -73.6667, 'mun': 'Vélez'},
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