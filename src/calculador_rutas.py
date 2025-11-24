from typing import Dict, List, Tuple
import networkx as nx

from clases import Nodo
from factores_viales import GestorFactoresViales


class CalculadorRutas:
    
    @staticmethod
    def calcular_ruta_real(
        G_vial: nx.MultiDiGraph,
        nodo_origen_vial: int,
        nodo_destino_vial: int,
        peso: str = "travel_time",
        gestor_factores: GestorFactoresViales = None
    ) -> Tuple[List[int], float, Dict]:

        try:
            ruta = nx.shortest_path(
                G_vial,
                nodo_origen_vial,
                nodo_destino_vial,
                weight=peso
            )
            
            peso_total = nx.shortest_path_length(
                G_vial,
                nodo_origen_vial,
                nodo_destino_vial,
                weight=peso
            )
            
            distancia_total = 0
            tiempo_base_total = 0
            tiempo_real_total = 0
            eventos_en_ruta = {
                'trafico_alto': 0,
                'clima_adverso': 0,
                'retenes': 0,
                'accidentes': 0,
                'obras': 0
            }
            
            for i in range(len(ruta) - 1):
                u = ruta[i]
                v = ruta[i + 1]
                
                mejor_edge = min(
                    G_vial[u][v].values(),
                    key=lambda x: x.get(peso, float('inf'))
                )
                
                distancia_total += mejor_edge.get('length', 0)
                tiempo_real_total += mejor_edge.get('travel_time', 0)
                tiempo_base_total += mejor_edge.get('travel_time_base', mejor_edge.get('travel_time', 0))
                
                if gestor_factores:
                    for key in G_vial[u][v]:
                        if (u, v, key) in gestor_factores.aristas_viales:
                            arista = gestor_factores.aristas_viales[(u, v, key)]
                            if arista.factores.trafico > 1.5:
                                eventos_en_ruta['trafico_alto'] += 1
                            if arista.factores.clima != 'despejado':
                                eventos_en_ruta['clima_adverso'] += 1
                            if arista.factores.retenes:
                                eventos_en_ruta['retenes'] += 1
                            if arista.factores.accidente:
                                eventos_en_ruta['accidentes'] += 1
                            if arista.factores.obras:
                                eventos_en_ruta['obras'] += 1
                            break
            
            info = {
                'num_nodos': len(ruta),
                'num_calles': len(ruta) - 1,
                'distancia_m': distancia_total,
                'distancia_km': distancia_total / 1000,
                'tiempo_base_s': tiempo_base_total,
                'tiempo_base_min': tiempo_base_total / 60,
                'tiempo_real_s': tiempo_real_total,
                'tiempo_real_min': tiempo_real_total / 60,
                'tiempo_adicional_min': (tiempo_real_total - tiempo_base_total) / 60,
                'penalizacion_promedio': tiempo_real_total / tiempo_base_total if tiempo_base_total > 0 else 1.0,
                'eventos': eventos_en_ruta
            }
            
            return ruta, peso_total, info
            
        except nx.NetworkXNoPath:
            print(f"No existe ruta entre {nodo_origen_vial} y {nodo_destino_vial}")
            return [], float('inf'), {}
        except Exception as e:
            print(f"Error calculando ruta: {e}")
            return [], float('inf'), {}
    
    @staticmethod
    def calcular_ruta_washington(
        G_vial: nx.MultiDiGraph,
        nodos_washington: Dict[str, Nodo],
        origen_id: str,
        destino_id: str,
        gestor_factores: GestorFactoresViales = None
    ) -> Tuple[List[int], Dict]:

        if origen_id not in nodos_washington or destino_id not in nodos_washington:
            print(f" Nodos no válidos: {origen_id}, {destino_id}")
            return [], {}
        
        nodo_origen = nodos_washington[origen_id]
        nodo_destino = nodos_washington[destino_id]
        
        if nodo_origen.nodo_vial_cercano is None or nodo_destino.nodo_vial_cercano is None:
            print(f" Nodos no conectados a red vial")
            return [], {}
        
        print(f"\n Calculando ruta REAL con factores externos:")
        print(f"   Origen: {nodo_origen.nombre}")
        print(f"   Destino: {nodo_destino.nombre}")
        
        ruta, peso, info = CalculadorRutas.calcular_ruta_real(
            G_vial,
            nodo_origen.nodo_vial_cercano,
            nodo_destino.nodo_vial_cercano,
            gestor_factores=gestor_factores
        )
        
        if ruta:
            distancia_total = (info['distancia_km'] + 
                             nodo_origen.distancia_a_vial + 
                             nodo_destino.distancia_a_vial)
            
            tiempo_acceso = ((nodo_origen.distancia_a_vial + nodo_destino.distancia_a_vial) / 30) * 60
            tiempo_total = info['tiempo_real_min'] + tiempo_acceso
            tiempo_base_total = info['tiempo_base_min'] + tiempo_acceso
            
            info_completa = {
                **info,
                'distancia_total_km': distancia_total,
                'tiempo_total_min': tiempo_total,
                'tiempo_base_total_min': tiempo_base_total,
                'tiempo_adicional_total_min': tiempo_total - tiempo_base_total,
                'distancia_acceso_km': nodo_origen.distancia_a_vial + nodo_destino.distancia_a_vial
            }
            
            print(f"\nRuta calculada:")
            print(f"   Distancia: {distancia_total:.2f} km")
            print(f"   Tiempo base: {tiempo_base_total:.1f} min")
            print(f"   Tiempo real: {tiempo_total:.1f} min")
            
            if info['tiempo_adicional_min'] > 0:
                print(f"   Retraso por factores: +{info['tiempo_adicional_min']:.1f} min")
                print(f"   Penalización: {info['penalizacion_promedio']:.2f}x")
            
            if info.get('eventos'):
                print(f"\n   Eventos en ruta:")
                eventos = info['eventos']
                if eventos['trafico_alto'] > 0:
                    print(f"      Tráfico alto: {eventos['trafico_alto']} segmentos")
                if eventos['clima_adverso'] > 0:
                    print(f"      Clima adverso: {eventos['clima_adverso']} segmentos")
                if eventos['retenes'] > 0:
                    print(f"      Retenes: {eventos['retenes']}")
                if eventos['accidentes'] > 0:
                    print(f"      Accidentes: {eventos['accidentes']}")
                if eventos['obras'] > 0:
                    print(f"      Obras: {eventos['obras']}")
            
            return ruta, info_completa
        
        return [], {}
