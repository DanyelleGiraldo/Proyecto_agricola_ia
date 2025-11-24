from typing import Dict
import numpy as np

class ExtractorCaracteristicas:
    
    @staticmethod
    def extraer_features(
        G_vial,
        nodos_washington: Dict,
        origen_id: str,
        destino_id: str,
        gestor_factores=None,
        hora_del_dia: int = 12
    ) -> np.ndarray:
        
        nodo_o = nodos_washington[origen_id]
        nodo_d = nodos_washington[destino_id]
        
        features = []
        
        lat_diff = nodo_o.latitud - nodo_d.latitud
        lon_diff = nodo_o.longitud - nodo_d.longitud
        
        dist_euclidiana = np.sqrt(lat_diff**2 + lon_diff**2) * 111
        features.append(dist_euclidiana)
        
        features.append(abs(lat_diff) * 111)
        features.append(abs(lon_diff) * 111)
        
        azimuth = np.arctan2(lon_diff, lat_diff) * 180 / np.pi
        if azimuth < 0:
            azimuth += 360
        features.append(azimuth / 360)
        
        dist_manhattan = (abs(lat_diff) + abs(lon_diff)) * 111
        features.append(dist_manhattan)
        
        excentricidad = dist_euclidiana / dist_manhattan if dist_manhattan > 0 else 1
        features.append(excentricidad)
        
        features.append(nodo_o.produccion_esperada / 1000)
        features.append(nodo_o.distancia_a_vial)
        features.append(nodo_d.distancia_a_vial)
        
        tipos = ['parcela', 'centro', 'planta']
        for tipo in tipos:
            features.append(1.0 if nodo_o.tipo == tipo else 0.0)
        for tipo in tipos:
            features.append(1.0 if nodo_d.tipo == tipo else 0.0)
        

        radio_analisis = 2.0
        
        nodos_cercanos_o = sum(1 for n in G_vial.nodes()
                              if abs(G_vial.nodes[n]['y'] - nodo_o.latitud) < 0.02 and
                                 abs(G_vial.nodes[n]['x'] - nodo_o.longitud) < 0.02)
        nodos_cercanos_d = sum(1 for n in G_vial.nodes()
                              if abs(G_vial.nodes[n]['y'] - nodo_d.latitud) < 0.02 and
                                 abs(G_vial.nodes[n]['x'] - nodo_d.longitud) < 0.02)
        
        features.append(np.log1p(nodos_cercanos_o))
        features.append(np.log1p(nodos_cercanos_d))
        
        velocidades = []
        for u, v, data in G_vial.edges(data=True):
            if (abs(G_vial.nodes[u]['y'] - nodo_o.latitud) < 0.02 and
                abs(G_vial.nodes[u]['x'] - nodo_o.longitud) < 0.02):
                velocidades.append(data.get('speed_kph', 40))
        
        vel_promedio = np.mean(velocidades) if velocidades else 40
        features.append(vel_promedio / 100)
        
        grados = [G_vial.degree(n) for n in list(G_vial.nodes())[:100]]
        features.append(np.mean(grados) / 10 if grados else 0.3)
        
        features.append(hora_del_dia / 24)
        
        es_hora_pico = 1.0 if (7 <= hora_del_dia <= 9) or (17 <= hora_del_dia <= 19) else 0.0
        features.append(es_hora_pico)
        
        es_finde = 0.0
        features.append(es_finde)
        
        if gestor_factores:
            penalizaciones = []
            riesgos = []
            eventos = 0
            
            for (u, v, key), arista in list(gestor_factores.aristas_viales.items())[:500]:
                lat_u = G_vial.nodes[u]['y']
                lon_u = G_vial.nodes[u]['x']
                
                if (abs(lat_u - nodo_o.latitud) < 0.02 or 
                    abs(lat_u - nodo_d.latitud) < 0.02):
                    
                    penalizaciones.append(arista.factores.calcular_penalizacion_tiempo())
                    
                    riesgo = arista.factores.obtener_riesgo()
                    riesgo_num = {'BAJO': 1, 'MEDIO': 2, 'ALTO': 3, 'MUY ALTO': 4}.get(riesgo, 1)
                    riesgos.append(riesgo_num)
                    
                    if (arista.factores.accidente or arista.factores.obras or 
                        arista.factores.retenes):
                        eventos += 1
            
            features.append(np.mean(penalizaciones) if penalizaciones else 1.0)
            features.append(np.mean(riesgos) if riesgos else 1.0)
            features.append(np.log1p(eventos))
        else:
            features.extend([1.0, 1.0, 0.0])

        features.extend([1.0, 0.0, 0.0, 0.0])
        
        return np.array(features)
