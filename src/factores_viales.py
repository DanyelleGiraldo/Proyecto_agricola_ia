from typing import Dict, List, Tuple
import networkx as nx
import osmnx as ox
import numpy as np
from clases import AristaVial, FactoresExternos

class GestorFactoresViales:
    
    def __init__(self, G_vial: nx.MultiDiGraph):
        self.G_vial = G_vial
        self.aristas_viales: Dict[Tuple[int, int], AristaVial] = {}
        self._inicializar_aristas()
    
    def _inicializar_aristas(self):
        print(f"\n Aplicando factores a las vias:D.")
        
        for u, v, key, data in self.G_vial.edges(keys=True, data=True):
            distancia = data.get('length', 0)
            tiempo_base = data.get('travel_time', distancia / 10)
            velocidad = data.get('speed_kph', 40)
            
            highway = data.get('highway', 'unclassified')
            if highway in ['motorway', 'trunk', 'primary']:
                tipo_via = 'primaria'
            elif highway in ['secondary', 'tertiary']:
                tipo_via = 'secundaria'
            elif highway in ['residential', 'living_street']:
                tipo_via = 'residencial'
            else:
                tipo_via = 'terciaria'
            
            arista = AristaVial(
                nodo_origen=u,
                nodo_destino=v,
                distancia_m=distancia,
                tiempo_base_s=tiempo_base,
                velocidad_maxima=velocidad,
                tipo_via=tipo_via,
                factores=FactoresExternos()
            )
            
            self.aristas_viales[(u, v, key)] = arista
        
        print(f"{len(self.aristas_viales)} aristas inicializadas")
    
    def aplicar_factores_zona(
        self,
        lat_centro: float,
        lon_centro: float,
        radio_km: float,
        factores: FactoresExternos
    ):

        print(f"\nAplicando factores en zona:")
        print(f"   Centro: ({lat_centro:.4f}, {lon_centro:.4f})")
        print(f"   Radio: {radio_km} km")
        print(f"   Factores: {factores.to_dict()}")
        
        afectadas = 0
        
        for (u, v, key), arista in self.aristas_viales.items():
            lat_u = self.G_vial.nodes[u]['y']
            lon_u = self.G_vial.nodes[u]['x']
            lat_v = self.G_vial.nodes[v]['y']
            lon_v = self.G_vial.nodes[v]['x']
            
            lat_medio = (lat_u + lat_v) / 2
            lon_medio = (lon_u + lon_v) / 2
            
            distancia = ox.distance.great_circle(lat_centro, lon_centro, lat_medio, lon_medio) / 1000
            
            if distancia <= radio_km:
                arista.actualizar_factores(factores)
                afectadas += 1
        
        print(f"✅ {afectadas} aristas afectadas")
        self._actualizar_pesos_grafo()
    
    def aplicar_factores_ruta(
        self,
        ruta_nodos: List[int],
        factores: FactoresExternos
    ):
        
        afectadas = 0
        for i in range(len(ruta_nodos) - 1):
            u = ruta_nodos[i]
            v = ruta_nodos[i + 1]
            
            for key in self.G_vial[u][v]:
                if (u, v, key) in self.aristas_viales:
                    self.aristas_viales[(u, v, key)].actualizar_factores(factores)
                    afectadas += 1
        
        print(f"{afectadas} segmentos de ruta afectados")
        self._actualizar_pesos_grafo()
    
    def simular_hora_pico(self, vias_principales: bool = True):
        print(f"\n aplicando el palo de trancon D:")
        
        afectadas = 0
        for (u, v, key), arista in self.aristas_viales.items():
            if vias_principales and arista.tipo_via in ['primaria', 'secundaria']:
                factores = FactoresExternos(
                    trafico=np.random.uniform(1.5, 2.5),
                    hora_pico=True
                )
                arista.actualizar_factores(factores)
                afectadas += 1
            elif not vias_principales:
                factores = FactoresExternos(
                    trafico=np.random.uniform(1.2, 1.8),
                    hora_pico=True
                )
                arista.actualizar_factores(factores)
                afectadas += 1
        
        print(f"{afectadas} vías afectadas por hora pico")
        self._actualizar_pesos_grafo()
    
    def simular_clima_adverso(self, tipo_clima: str = "lluvia"):
        print(f"\n Simulando clima: {tipo_clima.upper()}")
        
        afectadas = 0
        for arista in self.aristas_viales.values():
            factores = FactoresExternos(
                clima=tipo_clima,
                trafico=np.random.uniform(1.1, 1.3)
            )
            arista.actualizar_factores(factores)
            afectadas += 1
        
        print(f" {afectadas} aristas afectadas")
        self._actualizar_pesos_grafo()
    
    def simular_condiciones_aleatorias(self, probabilidad: float = 0.2):
        print(f"\nSimulando condiciones aleatorias Juntando clima, trancon, reten, accidente y obras (p={probabilidad})...")
        
        import random
        
        stats = {
            'trafico_alto': 0,
            'lluvia': 0,
            'retenes': 0,
            'accidentes': 0,
            'obras': 0
        }
        
        for arista in self.aristas_viales.values():
            factores = FactoresExternos()
            
            factores.trafico = random.uniform(0.8, 2.0)
            if factores.trafico > 1.5:
                stats['trafico_alto'] += 1
            
            if random.random() < probabilidad * 0.5:
                factores.clima = random.choice(['lluvia', 'niebla'])
                stats['lluvia'] += 1
            
            if random.random() < probabilidad * 0.3:
                factores.retenes = True
                stats['retenes'] += 1
            
            if random.random() < probabilidad * 0.1:
                factores.accidente = True
                stats['accidentes'] += 1
            
            if random.random() < probabilidad * 0.4:
                factores.obras = True
                stats['obras'] += 1
            
            factores.hora_pico = random.random() < 0.3
            
            arista.actualizar_factores(factores)
        
        print(f"\n📊 Estadísticas de simulación:")
        print(f"   Tráfico alto: {stats['trafico_alto']}")
        print(f"   Clima adverso: {stats['lluvia']}")
        print(f"   Retenes: {stats['retenes']}")
        print(f"   Accidentes: {stats['accidentes']}")
        print(f"   Obras: {stats['obras']}")
        
        self._actualizar_pesos_grafo()
    
    def limpiar_factores(self):
        print(f"\nLimpiando factores externos...")
        
        for arista in self.aristas_viales.values():
            arista.actualizar_factores(FactoresExternos())
        
        self._actualizar_pesos_grafo()
        print(f"Red restaurada a condiciones normales")
    
    def _actualizar_pesos_grafo(self):
        for (u, v, key), arista in self.aristas_viales.items():
            self.G_vial[u][v][key]['travel_time'] = arista.tiempo_real_s
            self.G_vial[u][v][key]['travel_time_base'] = arista.tiempo_base_s
            self.G_vial[u][v][key]['penalizacion'] = arista.factores.calcular_penalizacion_tiempo()
    
    def obtener_estadisticas(self) -> Dict:
        stats = {
            'total_aristas': len(self.aristas_viales),
            'trafico_alto': 0,
            'clima_adverso': 0,
            'retenes': 0,
            'accidentes': 0,
            'obras': 0,
            'hora_pico': 0,
            'riesgo_alto': 0,
            'riesgo_medio': 0,
            'riesgo_bajo': 0,
            'penalizacion_promedio': 0,
            'tiempo_adicional_total_min': 0
        }
        
        total_penalizacion = 0
        tiempo_adicional_total = 0
        
        for arista in self.aristas_viales.values():
            pen = arista.factores.calcular_penalizacion_tiempo()
            total_penalizacion += pen
            
            if arista.factores.trafico > 1.5:
                stats['trafico_alto'] += 1
            if arista.factores.clima in ['lluvia', 'tormenta', 'niebla']:
                stats['clima_adverso'] += 1
            if arista.factores.retenes:
                stats['retenes'] += 1
            if arista.factores.accidente:
                stats['accidentes'] += 1
            if arista.factores.obras:
                stats['obras'] += 1
            if arista.factores.hora_pico:
                stats['hora_pico'] += 1
            
            riesgo = arista.factores.obtener_riesgo()
            if riesgo in ['ALTO', 'MUY ALTO']:
                stats['riesgo_alto'] += 1
            elif riesgo == 'MEDIO':
                stats['riesgo_medio'] += 1
            else:
                stats['riesgo_bajo'] += 1
            
            tiempo_adicional_total += (arista.tiempo_real_s - arista.tiempo_base_s)
        
        stats['penalizacion_promedio'] = total_penalizacion / len(self.aristas_viales)
        stats['tiempo_adicional_total_min'] = tiempo_adicional_total / 60
        
        return stats
    
    def obtener_aristas_por_riesgo(self, nivel: str = "ALTO") -> List[AristaVial]:
        return [
            arista for arista in self.aristas_viales.values()
            if arista.factores.obtener_riesgo() == nivel
        ]
