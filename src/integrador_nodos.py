from typing import Dict, List
import networkx as nx
import osmnx as ox

from clases import Nodo

class IntegradorNodos:
    
    @staticmethod
    def obtener_nodos_washington() -> List[Nodo]:
        
        zonas = {
            'parcelas': [
                # YAKIMA VALLEY (Principal zona de producción)
                {'id': 'P001', 'nombre': 'Yakima Valley Orchards - Yakima', 'lat': 46.6021, 'lon': -120.5059, 'prod': 5000, 'mun': 'Yakima'},
                {'id': 'P002', 'nombre': 'Selah Creek Farms - Selah', 'lat': 46.6543, 'lon': -120.5301, 'prod': 4200, 'mun': 'Selah'},
                {'id': 'P003', 'nombre': 'Naches Heights Apple Ranch', 'lat': 46.7315, 'lon': -120.6951, 'prod': 3800, 'mun': 'Naches'},
                {'id': 'P004', 'nombre': 'Tieton Orchards Complex', 'lat': 46.7007, 'lon': -120.7551, 'prod': 4500, 'mun': 'Tieton'},
                {'id': 'P005', 'nombre': 'Zillah Apple Farms', 'lat': 46.4018, 'lon': -120.2621, 'prod': 3500, 'mun': 'Zillah'},
                
                # WENATCHEE VALLEY (Valle más productivo)
                {'id': 'P006', 'nombre': 'Stemilt Orchards - Wenatchee', 'lat': 47.4235, 'lon': -120.3103, 'prod': 6000, 'mun': 'Wenatchee'},
                {'id': 'P007', 'nombre': 'Chelan Fresh - East Wenatchee', 'lat': 47.4156, 'lon': -120.2826, 'prod': 5500, 'mun': 'East Wenatchee'},
                {'id': 'P008', 'nombre': 'Columbia Valley Orchards', 'lat': 47.4857, 'lon': -120.2651, 'prod': 4800, 'mun': 'Wenatchee'},
                {'id': 'P009', 'nombre': 'Cashmere Apple Farms', 'lat': 47.5223, 'lon': -120.4704, 'prod': 4000, 'mun': 'Cashmere'},
                {'id': 'P010', 'nombre': 'Leavenworth Orchard District', 'lat': 47.5962, 'lon': -120.6615, 'prod': 3200, 'mun': 'Leavenworth'},
                
                # COLUMBIA BASIN (Zona en expansión)
                {'id': 'P011', 'nombre': 'Royal Slope Orchards - Mattawa', 'lat': 46.7374, 'lon': -119.9034, 'prod': 3500, 'mun': 'Mattawa'},
                {'id': 'P012', 'nombre': 'Quincy Valley Fruits', 'lat': 47.2340, 'lon': -119.8528, 'prod': 3200, 'mun': 'Quincy'},
                {'id': 'P013', 'nombre': 'Moses Lake Apple Growers', 'lat': 47.1301, 'lon': -119.2781, 'prod': 2800, 'mun': 'Moses Lake'},
                
                # SPOKANE AREA (Zona este)
                {'id': 'P014', 'nombre': 'Spokane Valley Fruits', 'lat': 47.6588, 'lon': -117.2394, 'prod': 1500, 'mun': 'Spokane Valley'},
                {'id': 'P015', 'nombre': 'Green Bluff Orchards', 'lat': 47.7712, 'lon': -117.2371, 'prod': 1200, 'mun': 'Green Bluff'},
                
                # TRI-CITIES AREA
                {'id': 'P016', 'nombre': 'Pasco Basin Orchards', 'lat': 46.2396, 'lon': -119.1006, 'prod': 2500, 'mun': 'Pasco'},
                
                # NORTH CENTRAL WASHINGTON
                {'id': 'P017', 'nombre': 'Okanogan Valley Apples', 'lat': 48.3651, 'lon': -119.5831, 'prod': 2000, 'mun': 'Okanogan'},
                {'id': 'P018', 'nombre': 'Omak Fruit Company', 'lat': 48.4112, 'lon': -119.5275, 'prod': 1800, 'mun': 'Omak'},
            ],
            
            'centros': [
                # Centros de Acopio y Distribución Principales
                {'id': 'C001', 'nombre': 'Yakima Fruit Distribution Hub', 'lat': 46.6021, 'lon': -120.5059, 'mun': 'Yakima'},
                {'id': 'C002', 'nombre': 'Wenatchee Valley Warehouse', 'lat': 47.4235, 'lon': -120.3103, 'mun': 'Wenatchee'},
                {'id': 'C003', 'nombre': 'Columbia Basin Cold Storage', 'lat': 46.7374, 'lon': -119.9034, 'mun': 'Mattawa'},
                {'id': 'C004', 'nombre': 'Seattle Distribution Center', 'lat': 47.6062, 'lon': -122.3321, 'mun': 'Seattle'},
                {'id': 'C005', 'nombre': 'Spokane Regional Storage', 'lat': 47.6588, 'lon': -117.2394, 'mun': 'Spokane'},
                {'id': 'C006', 'nombre': 'Tri-Cities Distribution Hub', 'lat': 46.2396, 'lon': -119.1006, 'mun': 'Pasco'},
                {'id': 'C007', 'nombre': 'Tacoma Port Distribution', 'lat': 47.2529, 'lon': -122.4443, 'mun': 'Tacoma'},
            ],
            
            'plantas': [
                {'id': 'PL001', 'nombre': 'Tree Top Inc. - Selah', 'lat': 46.6543, 'lon': -120.5301, 'mun': 'Selah'},
                {'id': 'PL002', 'nombre': 'Washington Fruit Processing - Yakima', 'lat': 46.6021, 'lon': -120.5059, 'mun': 'Yakima'},
                {'id': 'PL003', 'nombre': 'Wenatchee Packing Plant', 'lat': 47.4235, 'lon': -120.3103, 'mun': 'Wenatchee'},
                {'id': 'PL004', 'nombre': 'Columbia River Processing', 'lat': 46.2396, 'lon': -119.1006, 'mun': 'Pasco'},
                {'id': 'PL005', 'nombre': 'Seattle Processing Facility', 'lat': 47.6062, 'lon': -122.3321, 'mun': 'Seattle'},
            ],
            
            'mercados': [
                {'id': 'M001', 'nombre': 'Seattle Pike Place Market', 'lat': 47.6097, 'lon': -122.3422, 'mun': 'Seattle'},
                {'id': 'M002', 'nombre': 'Spokane Public Market', 'lat': 47.6588, 'lon': -117.4260, 'mun': 'Spokane'},
                {'id': 'M003', 'nombre': 'Yakima Farmers Market', 'lat': 46.6021, 'lon': -120.5059, 'mun': 'Yakima'},
                {'id': 'M004', 'nombre': 'Tacoma Farmers Market', 'lat': 47.2529, 'lon': -122.4443, 'mun': 'Tacoma'},
                {'id': 'M005', 'nombre': 'Bellingham Public Market', 'lat': 48.7519, 'lon': -122.4787, 'mun': 'Bellingham'},
                {'id': 'M006', 'nombre': 'Tri-Cities Farmers Market', 'lat': 46.2396, 'lon': -119.1006, 'mun': 'Pasco'},
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
        
        for mercado in zonas['mercados']:
            nodos.append(Nodo(
                id=mercado['id'],
                nombre=mercado['nombre'],
                tipo='mercado',
                latitud=mercado['lat'],
                longitud=mercado['lon']
            ))
        
        return nodos
    
    @staticmethod
    def conectar_nodos_a_red_vial(
        nodos_washington: List[Nodo],
        G_vial: nx.MultiDiGraph
    ) -> Dict[str, int]:
        
        conexiones = {}
        
        print(f"\n🔗 Conectando nodos a la red vial de Washington...")
        print(f"{'='*70}")
        
        for nodo in nodos_washington:
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
            
            emoji = {
                'parcela': '🍎',
                'centro': '🏪',
                'planta': '🏭',
                'mercado': '🛒'
            }[nodo.tipo]
            
            tipo_texto = {
                'parcela': 'Huerto',
                'centro': 'Acopio',
                'planta': 'Planta',
                'mercado': 'Mercado'
            }[nodo.tipo]
            
            print(f"{emoji} {nodo.id:5} ({tipo_texto:7}) → Nodo vial {nodo_vial_cercano} ({distancia:.0f}m)")
        
        print(f"\n{'='*70}")
        print(f"✅ {len(conexiones)} nodos conectados a la red vial de Washington")
        print(f"    🍎 {sum(1 for n in nodos_washington if n.tipo == 'parcela')} huertos de manzanas")
        print(f"    🏪 {sum(1 for n in nodos_washington if n.tipo == 'centro')} centros de acopio")
        print(f"    🏭 {sum(1 for n in nodos_washington if n.tipo == 'planta')} plantas procesadoras")
        print(f"    🛒 {sum(1 for n in nodos_washington if n.tipo == 'mercado')} mercados")
        
        return conexiones