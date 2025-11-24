import networkx as nx
import folium
from folium import plugins
import numpy as np
from typing import Dict, List, Tuple
import time
import matplotlib.pyplot as plt
import matplotlib

class ComparadorAlgoritmos:
    
    def __init__(self):
        self.resultados = {}
    
    def calcular_con_dijkstra(
        self,
        G_vial: nx.MultiDiGraph,
        origen_vial: int,
        destino_vial: int,
        peso: str = "travel_time"
    ) -> Tuple[List[int], float, Dict]:
        
        inicio = time.time()
        
        try:
            G_simple = nx.Graph()
            
            for node, data in G_vial.nodes(data=True):
                G_simple.add_node(node, **data)
            
            for u, v, key, data in G_vial.edges(keys=True, data=True):
                peso_actual = data.get(peso, float('inf'))
                
                if G_simple.has_edge(u, v):
                    peso_existente = G_simple[u][v].get(peso, float('inf'))
                    if peso_actual < peso_existente:
                        G_simple[u][v][peso] = peso_actual
                        G_simple[u][v]['length'] = data.get('length', 0)
                else:
                    G_simple.add_edge(u, v, **{peso: peso_actual, 'length': data.get('length', 0)})
            
            ruta = nx.dijkstra_path(
                G_simple,
                origen_vial,
                destino_vial,
                weight=peso
            )
            
            peso_total = nx.dijkstra_path_length(
                G_simple,
                origen_vial,
                destino_vial,
                weight=peso
            )
            
            tiempo_ejecucion = time.time() - inicio
            
            info = self._extraer_info_ruta(G_simple, ruta, peso)
            info['tiempo_ejecucion_ms'] = tiempo_ejecucion * 1000
            info['algoritmo'] = 'Dijkstra'
            
            return ruta, peso_total, info
            
        except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
            tiempo_ejecucion = time.time() - inicio
            print(f" No se encontró ruta con Dijkstra: {e}")
            return [], float('inf'), {'tiempo_ejecucion_ms': tiempo_ejecucion * 1000}
        except Exception as e:
            tiempo_ejecucion = time.time() - inicio
            print(f" Error en Dijkstra: {e}")
            return [], float('inf'), {'tiempo_ejecucion_ms': tiempo_ejecucion * 1000}
    
    def calcular_con_bellman_ford(
        self,
        G_vial: nx.MultiDiGraph,
        origen_vial: int,
        destino_vial: int,
        peso: str = "travel_time"
    ) -> Tuple[List[int], float, Dict]:
        
        inicio = time.time()
        
        try:
            G_simple = nx.Graph()
            
            for node, data in G_vial.nodes(data=True):
                G_simple.add_node(node, **data)
            
            for u, v, key, data in G_vial.edges(keys=True, data=True):
                peso_actual = data.get(peso, float('inf'))
                
                if G_simple.has_edge(u, v):
                    peso_existente = G_simple[u][v].get(peso, float('inf'))
                    if peso_actual < peso_existente:
                        G_simple[u][v][peso] = peso_actual
                        G_simple[u][v]['length'] = data.get('length', 0)
                else:
                    G_simple.add_edge(u, v, **{peso: peso_actual, 'length': data.get('length', 0)})
            
            length, path = nx.single_source_bellman_ford(
                G_simple,
                origen_vial,
                target=destino_vial,
                weight=peso
            )
            
            ruta = path
            peso_total = length
            
            tiempo_ejecucion = time.time() - inicio
            
            info = self._extraer_info_ruta(G_simple, ruta, peso)
            info['tiempo_ejecucion_ms'] = tiempo_ejecucion * 1000
            info['algoritmo'] = 'Bellman-Ford'
            
            return ruta, peso_total, info
            
        except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
            tiempo_ejecucion = time.time() - inicio
            print(f"   No se encontró ruta con Bellman-Ford: {e}")
            return [], float('inf'), {'tiempo_ejecucion_ms': tiempo_ejecucion * 1000}
        except Exception as e:
            tiempo_ejecucion = time.time() - inicio
            print(f"   Error en Bellman-Ford: {e}")
            return [], float('inf'), {'tiempo_ejecucion_ms': tiempo_ejecucion * 1000}
    
    def calcular_con_astar(
        self,
        G_vial: nx.MultiDiGraph,
        origen_vial: int,
        destino_vial: int,
        peso: str = "travel_time"
    ) -> Tuple[List[int], float, Dict]:
        
        inicio = time.time()
        
        def heuristica(u, v):
            try:
                lat_u = G_vial.nodes[u]['y']
                lon_u = G_vial.nodes[u]['x']
                lat_v = G_vial.nodes[v]['y']
                lon_v = G_vial.nodes[v]['x']
                
                return np.sqrt((lat_u - lat_v)**2 + (lon_u - lon_v)**2) * 111000 
            except:
                return 0
        
        try:
            G_simple = nx.Graph()
            
            for node, data in G_vial.nodes(data=True):
                G_simple.add_node(node, **data)
            
            for u, v, key, data in G_vial.edges(keys=True, data=True):
                peso_actual = data.get(peso, float('inf'))
                
                if G_simple.has_edge(u, v):
                    peso_existente = G_simple[u][v].get(peso, float('inf'))
                    if peso_actual < peso_existente:
                        G_simple[u][v][peso] = peso_actual
                        G_simple[u][v]['length'] = data.get('length', 0)
                else:
                    G_simple.add_edge(u, v, **{peso: peso_actual, 'length': data.get('length', 0)})
            
            ruta = nx.astar_path(
                G_simple,
                origen_vial,
                destino_vial,
                heuristic=heuristica,
                weight=peso
            )
            
            peso_total = nx.astar_path_length(
                G_simple,
                origen_vial,
                destino_vial,
                heuristic=heuristica,
                weight=peso
            )
            
            tiempo_ejecucion = time.time() - inicio
            
            info = self._extraer_info_ruta(G_simple, ruta, peso)
            info['tiempo_ejecucion_ms'] = tiempo_ejecucion * 1000
            info['algoritmo'] = 'A*'
            
            return ruta, peso_total, info
            
        except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
            tiempo_ejecucion = time.time() - inicio
            print(f"   No se encontró ruta con A*: {e}")
            return [], float('inf'), {'tiempo_ejecucion_ms': tiempo_ejecucion * 1000}
        except Exception as e:
            tiempo_ejecucion = time.time() - inicio
            print(f"   Error en A*: {e}")
            return [], float('inf'), {'tiempo_ejecucion_ms': tiempo_ejecucion * 1000}
    
    def _extraer_info_ruta(self, G_simple, ruta, peso):
        
        if not ruta or len(ruta) < 2:
            return {}
        
        distancia_total = 0
        tiempo_total = 0
        
        for i in range(len(ruta) - 1):
            u = ruta[i]
            v = ruta[i + 1]
            
            if G_simple.has_edge(u, v):
                distancia_total += G_simple[u][v].get('length', 0)
                tiempo_total += G_simple[u][v].get(peso, 0)
        
        return {
            'num_nodos': len(ruta),
            'num_calles': len(ruta) - 1,
            'distancia_m': distancia_total,
            'distancia_km': distancia_total / 1000,
            'tiempo_s': tiempo_total,
            'tiempo_min': tiempo_total / 60
        }
    
    def visualizar_comparacion_en_mapa(
        self,
        G_vial: nx.MultiDiGraph,
        nodos_washington: Dict,
        origen_id: str,
        destino_id: str,
        archivo: str = "comparacion_algoritmos_mapa.html"
    ):
        
        if not self.resultados:
            print("  No hay resultados para visualizar")
            return
        
        print(f"\n  Generando mapa comparativo...")
        
        nodo_o = nodos_washington[origen_id]
        nodo_d = nodos_washington[destino_id]
        centro = [(nodo_o.latitud + nodo_d.latitud)/2, (nodo_o.longitud + nodo_d.longitud)/2]
        
        mapa = folium.Map(
            location=centro,
            zoom_start=13,
            tiles='OpenStreetMap',
            control_scale=True
        )
        
        colores_alg = {
            'Dijkstra': '#3498db',     
            'Bellman-Ford': '#9b59b6', 
            'A*': '#2ecc71',             
            'IA': '#e74c3c'             
        }
        
        estilos_alg = {
            'Dijkstra': {'weight': 6, 'opacity': 0.9, 'dash_array': None},
            'Bellman-Ford': {'weight': 5, 'opacity': 0.8, 'dash_array': '10, 5'},
            'A*': {'weight': 5, 'opacity': 0.8, 'dash_array': '5, 5'},
            'IA': {'weight': 4, 'opacity': 0.7, 'dash_array': '2, 8'}
        }
        
        titulo_html = f'''
        <div style="position: fixed; top: 10px; left: 50px; width: auto; max-width: 650px;
                    background-color: white; border: 3px solid #2c3e50;
                    z-index: 9999; padding: 15px; border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
            <h3 style="margin: 0 0 10px 0; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">
                🔬 Comparación de Algoritmos de Rutas
            </h3>
            <p style="margin: 5px 0; font-size: 13px; color: #34495e;">
                <b>Origen:</b> {nodo_o.nombre}<br>
                <b>Destino:</b> {nodo_d.nombre}
            </p>
            <table style="width: 100%; font-size: 11px; margin-top: 10px; border-collapse: collapse;">
                <tr style="background-color: #2c3e50; color: white; font-weight: bold;">
                    <td style="padding: 5px;">Algoritmo</td>
                    <td style="padding: 5px;">Distancia</td>
                    <td style="padding: 5px;">Tiempo</td>
                    <td style="padding: 5px;">Velocidad</td>
                    <td style="padding: 5px;">Cómputo</td>
                </tr>
        '''
        
        for alg, datos in self.resultados.items():
            info = datos['info']
            dist = info.get('distancia_km', 0)
            tiempo = info.get('tiempo_min', 0)
            ejec = info.get('tiempo_ejecucion_ms', 0)
            color = colores_alg.get(alg, 'gray')
            
            velocidad = (dist / (tiempo / 60)) if tiempo > 0 else 0
            
            titulo_html += f'''
                <tr style="background-color: {'#ecf0f1' if self.resultados.keys().index(alg) % 2 == 0 else 'white'};">
                    <td style="padding: 5px;">
                        <span style="color: {color}; font-size: 18px; font-weight: bold;">●</span> 
                        <b>{alg}</b>
                    </td>
                    <td style="padding: 5px;">{dist:.2f} km</td>
                    <td style="padding: 5px;">{tiempo:.1f} min</td>
                    <td style="padding: 5px;">{velocidad:.1f} km/h</td>
                    <td style="padding: 5px;">{ejec:.2f} ms</td>
                </tr>
            '''
        
        distancias = [datos['info'].get('distancia_km', 0) for datos in self.resultados.values() if datos['info'].get('distancia_km', 0) > 0]
        tiempos = [datos['info'].get('tiempo_ejecucion_ms', float('inf')) for datos in self.resultados.values()]
        
        if distancias:
            dist_min = min(distancias)
            dist_max = max(distancias)
            diff_pct = ((dist_max - dist_min) / dist_min * 100) if dist_min > 0 else 0
            
            tiempo_min_alg = min(self.resultados.items(), key=lambda x: x[1]['info'].get('tiempo_ejecucion_ms', float('inf')))
            
            titulo_html += f'''
                </table>
                <div style="margin-top: 10px; padding: 10px; background-color: #e8f4f8; border-radius: 5px;">
                    <p style="margin: 3px 0; font-size: 12px;">
                        <b> Análisis:</b><br>
                        Diferencia de distancias: {diff_pct:.1f}%<br>
                        Más rápido: <b>{tiempo_min_alg[0]}</b> ({tiempo_min_alg[1]['info'].get('tiempo_ejecucion_ms', 0):.2f} ms)<br>
                        Todos {'encontraron la misma ruta' if diff_pct < 1 else 'encontraron rutas diferentes'}
                    </p>
                </div>
            '''
        
        titulo_html += '</div>'
        mapa.get_root().html.add_child(folium.Element(titulo_html))
        
        grupos_rutas = {}
        for alg in self.resultados.keys():
            grupos_rutas[alg] = folium.FeatureGroup(
                name=f'{alg} - {self.resultados[alg]["info"].get("distancia_km", 0):.2f} km',
                show=True
            )
        
        rutas_dibujadas = 0
        for alg, datos in self.resultados.items():
            ruta = datos['ruta']
            info = datos['info']
            
            if not ruta or len(ruta) < 2:
                print(f"   {alg}: Sin ruta para visualizar")
                continue
            
            color = colores_alg.get(alg, 'gray')
            estilo = estilos_alg.get(alg, {'weight': 4, 'opacity': 0.7, 'dash_array': None})
            
            coords_ruta = []
            for nodo_vial in ruta:
                try:
                    lat = G_vial.nodes[nodo_vial]['y']
                    lon = G_vial.nodes[nodo_vial]['x']
                    coords_ruta.append([lat, lon])
                except:
                    continue
            
            if len(coords_ruta) < 2:
                print(f"   {alg}: No hay suficientes coordenadas")
                continue
            
            folium.PolyLine(
                coords_ruta,
                color=color,
                weight=estilo['weight'],
                opacity=estilo['opacity'],
                dash_array=estilo['dash_array'],
                popup=f"""
                    <div style='font-family: Arial; width: 200px;'>
                        <h4 style='margin: 0; color: {color};'>{alg}</h4>
                        <table style='width: 100%; font-size: 11px; margin-top: 5px;'>
                            <tr><td><b>Distancia:</b></td><td>{info.get('distancia_km', 0):.2f} km</td></tr>
                            <tr><td><b>Tiempo:</b></td><td>{info.get('tiempo_min', 0):.1f} min</td></tr>
                            <tr><td><b>Calles:</b></td><td>{info.get('num_calles', 0)}</td></tr>
                            <tr><td><b>Cómputo:</b></td><td>{info.get('tiempo_ejecucion_ms', 0):.2f} ms</td></tr>
                        </table>
                    </div>
                """,
                tooltip=f"{alg}: {len(ruta)} nodos, {info.get('distancia_km', 0):.2f} km"
            ).add_to(grupos_rutas[alg])
            
            folium.CircleMarker(
                location=coords_ruta[0],
                radius=7,
                color=color,
                fill=True,
                fillColor='white',
                fillOpacity=0.9,
                popup=f"Inicio {alg}",
                weight=3
            ).add_to(grupos_rutas[alg])
            
            folium.CircleMarker(
                location=coords_ruta[-1],
                radius=7,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.9,
                popup=f"Fin {alg}",
                weight=3
            ).add_to(grupos_rutas[alg])
            
            rutas_dibujadas += 1
            print(f"   {alg}: {len(coords_ruta)} puntos, {info.get('distancia_km', 0):.2f} km")
        
        folium.Marker(
            location=[nodo_o.latitud, nodo_o.longitud],
            popup=f"<b>ORIGEN</b><br>{nodo_o.nombre}<br>{nodo_o.tipo.title()}",
            tooltip=f"Origen: {nodo_o.nombre}",
            icon=folium.Icon(color='green', icon='play', prefix='fa', icon_color='white')
        ).add_to(mapa)
        
        folium.Marker(
            location=[nodo_d.latitud, nodo_d.longitud],
            popup=f"<b>DESTINO</b><br>{nodo_d.nombre}<br>{nodo_d.tipo.title()}",
            tooltip=f"Destino: {nodo_d.nombre}",
            icon=folium.Icon(color='red', icon='flag-checkered', prefix='fa', icon_color='white')
        ).add_to(mapa)
        
        for grupo in grupos_rutas.values():
            grupo.add_to(mapa)
        
        folium.LayerControl(collapsed=False, position='topright').add_to(mapa)
        plugins.Fullscreen(position='topleft').add_to(mapa)
        
        leyenda_html = f'''
        <div style="position: fixed; bottom: 30px; left: 50px; width: 280px;
                    background-color: white; border: 3px solid #2c3e50;
                    z-index: 9999; padding: 15px; border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
            <h4 style="margin: 0 0 10px 0; color: #2c3e50;">Leyenda de Algoritmos</h4>
            <div style="font-size: 12px;">
        '''
        
        for alg, color in colores_alg.items():
            if alg in self.resultados:
                estilo = estilos_alg.get(alg, {})
                dash = estilo.get('dash_array', None)
                dash_style = f"border-top: 3px {('dashed' if dash and '10' in dash else 'dotted' if dash else 'solid')} {color};" if dash else f"background-color: {color};"
                
                leyenda_html += f'''
                <p style="margin: 8px 0;">
                    <span style="display: inline-block; width: 30px; height: 3px; 
                          {dash_style} vertical-align: middle;"></span>
                    <b style="margin-left: 5px;">{alg}</b>
                    {' (predicción)' if alg == 'IA' else ''}
                </p>
                '''
        
        leyenda_html += f'''
                <hr style="margin: 10px 0; border: 1px solid #bdc3c7;">
                <p style="margin: 5px 0; font-size: 11px; color: #7f8c8d;">
                    <b>Tip:</b> Usa el control de capas arriba a la derecha para 
                    mostrar/ocultar rutas individuales.
                </p>
                <p style="margin: 5px 0; font-size: 11px; color: #7f8c8d;">
                    Total de rutas visualizadas: <b>{rutas_dibujadas}</b>
                </p>
            </div>
        </div>
        '''
        mapa.get_root().html.add_child(folium.Element(leyenda_html))
        
        try:
            mapa.save(archivo)
            print(f"\n✅ Mapa comparativo guardado: {archivo}")
            print(f"   📊 Rutas visualizadas: {rutas_dibujadas}/{len(self.resultados)}")
            
            try:
                import webbrowser
                import os
                webbrowser.open('file://' + os.path.abspath(archivo))
                print(f"🌐 Abriendo en navegador...")
            except:
                print(f"⚠️  Abre manualmente: {archivo}")
                
        except Exception as e:
            print(f"❌ Error guardando mapa: {e}")
        
        return archivo



    def calcular_con_ia(
        self,
        sistema_ia,
        G_vial: nx.MultiDiGraph,
        nodos_washington: Dict,
        origen_id: str,
        destino_id: str,
        gestor_factores
    ) -> Dict:
        inicio = time.time()
        
        try:
            features = self._extraer_features_basicas(
                G_vial,
                nodos_washington,
                origen_id,
                destino_id
            )
            
            prediccion = sistema_ia.predecir_ruta(features)
            tiempo_ejecucion = time.time() - inicio
            
            prediccion['tiempo_ejecucion_ms'] = tiempo_ejecucion * 1000
            prediccion['algoritmo'] = 'IA (Random Forest)'
            
            return prediccion
        except Exception as e:
            tiempo_ejecucion = time.time() - inicio
            print(f"   Error en IA: {e}")
            return {
                'tiempo_ejecucion_ms': tiempo_ejecucion * 1000,
                'distancia_km': 0,
                'tiempo_min': 0,
                'riesgo': 'DESCONOCIDO'
            }
    
    def _extraer_features_basicas(self, G_vial, nodos_washington, origen_id, destino_id):
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
        
        features.append((abs(lat_diff) + abs(lon_diff)) * 111)
        
        dist_manhattan = (abs(lat_diff) + abs(lon_diff)) * 111
        features.append(dist_euclidiana / dist_manhattan if dist_manhattan > 0 else 1)
        
        features.append(nodo_o.produccion_esperada / 1000)
        features.append(nodo_o.distancia_a_vial)
        features.append(nodo_d.distancia_a_vial)
        
        tipos = ['parcela', 'centro', 'planta']
        for tipo in tipos:
            features.append(1.0 if nodo_o.tipo == tipo else 0.0)
        for tipo in tipos:
            features.append(1.0 if nodo_d.tipo == tipo else 0.0)
        
        while len(features) < 29:
            features.append(0.0)
        
        return np.array(features[:29])
    
    def generar_grafico_comparativo_multiple(self, resultados_multiples: list, 
                                        archivo: str = "comparacion_multiple_rutas.png"):

        if not resultados_multiples:
            print("No hay resultados para graficar")
            return
        
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')
        
        print(f"\n Generando gráfico comparativo de {len(resultados_multiples)} rutas...")
        
        algoritmos = ['Dijkstra', 'Bellman-Ford', 'A*', 'IA']
        colores_alg = {
            'Dijkstra': '#3498db',
            'Bellman-Ford': '#9b59b6',
            'A*': '#2ecc71',
            'IA': '#e74c3c'
        }
        
        distancias_por_alg = {alg: [] for alg in algoritmos}
        tiempos_ejec_por_alg = {alg: [] for alg in algoritmos}
        nombres_rutas = []
        
        for i, resultado in enumerate(resultados_multiples):
            nombres_rutas.append(f"Ruta {i+1}")
            
            for alg in algoritmos:
                if alg in resultado:
                    info = resultado[alg]['info']
                    distancias_por_alg[alg].append(info.get('distancia_km', 0))
                    tiempos_ejec_por_alg[alg].append(info.get('tiempo_ejecucion_ms', 0))
                else:
                    distancias_por_alg[alg].append(0)
                    tiempos_ejec_por_alg[alg].append(0)
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'Comparación de Algoritmos en {len(resultados_multiples)} Rutas', 
                    fontsize=16, fontweight='bold')
        
        ax1 = axes[0, 0]
        x = range(len(nombres_rutas))
        
        for alg in algoritmos:
            if any(d > 0 for d in distancias_por_alg[alg]):
                ax1.plot(x, distancias_por_alg[alg], 
                        marker='o', linewidth=2, markersize=8,
                        label=alg, color=colores_alg[alg])
        
        ax1.set_xlabel('Rutas', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Distancia (km)', fontsize=11, fontweight='bold')
        ax1.set_title('Distancias Calculadas por Ruta', fontsize=12, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(nombres_rutas, rotation=45)
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3, linestyle='--')
        
        ax2 = axes[0, 1]
        tiempos_promedio = []
        colores = []
        
        for alg in algoritmos:
            tiempos = [t for t in tiempos_ejec_por_alg[alg] if t > 0]
            promedio = np.mean(tiempos) if tiempos else 0
            tiempos_promedio.append(promedio)
            colores.append(colores_alg[alg])
        
        bars = ax2.bar(algoritmos, tiempos_promedio, color=colores, alpha=0.8, edgecolor='black')
        ax2.set_ylabel('Tiempo Promedio (ms)', fontsize=11, fontweight='bold')
        ax2.set_title('Tiempo de Ejecución Promedio', fontsize=12, fontweight='bold')
        ax2.set_yscale('log')
        ax2.grid(axis='y', alpha=0.3, linestyle='--', which='both')
        
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.2f}',
                        ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax3 = axes[1, 0]
        datos_boxplot = []
        etiquetas_boxplot = []
        
        for alg in algoritmos:
            distancias = [d for d in distancias_por_alg[alg] if d > 0]
            if distancias:
                datos_boxplot.append(distancias)
                etiquetas_boxplot.append(alg)
        
        if datos_boxplot:
            bp = ax3.boxplot(datos_boxplot, labels=etiquetas_boxplot, patch_artist=True)
            
            for patch, alg in zip(bp['boxes'], etiquetas_boxplot):
                patch.set_facecolor(colores_alg[alg])
                patch.set_alpha(0.6)
            
            ax3.set_ylabel('Distancia (km)', fontsize=11, fontweight='bold')
            ax3.set_title('Distribución de Distancias', fontsize=12, fontweight='bold')
            ax3.grid(axis='y', alpha=0.3, linestyle='--')
        
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        estadisticas = []
        for alg in algoritmos:
            distancias = [d for d in distancias_por_alg[alg] if d > 0]
            tiempos = [t for t in tiempos_ejec_por_alg[alg] if t > 0]
            
            if distancias:
                dist_prom = np.mean(distancias)
                dist_std = np.std(distancias)
                tiempo_prom = np.mean(tiempos) if tiempos else 0
                
                estadisticas.append([
                    alg,
                    f"{dist_prom:.2f}",
                    f"±{dist_std:.2f}",
                    f"{tiempo_prom:.2f}",
                    f"{len(distancias)}"
                ])
        
        if estadisticas:
            tabla = ax4.table(
                cellText=estadisticas,
                colLabels=['Algoritmo', 'Dist. Prom.', 'Desv. Est.', 'Tiempo (ms)', 'Rutas'],
                cellLoc='center',
                loc='center',
                colWidths=[0.25, 0.2, 0.2, 0.2, 0.15]
            )
            
            tabla.auto_set_font_size(False)
            tabla.set_fontsize(10)
            tabla.scale(1, 2)
            
            for i in range(5):
                tabla[(0, i)].set_facecolor('#2c3e50')
                tabla[(0, i)].set_text_props(weight='bold', color='white')
            
            for i in range(1, len(estadisticas) + 1):
                color = '#ecf0f1' if i % 2 == 0 else 'white'
                for j in range(5):
                    tabla[(i, j)].set_facecolor(color)
            
            ax4.set_title('Resumen Estadístico', fontsize=12, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        try:
            plt.savefig(archivo, dpi=300, bbox_inches='tight')
            print(f"Gráfico guardado: {archivo}")
            
            try:
                import subprocess
                subprocess.run(['xdg-open', archivo], check=False)
            except:
                pass
            
        except Exception as e:
            print(f"❌ Error guardando gráfico: {e}")
        
        plt.close()
    
    
    def comparar_todos(
        self,
        G_vial: nx.MultiDiGraph,
        nodos_washington: Dict,
        origen_id: str,
        destino_id: str,
        sistema_ia,
        gestor_factores
    ) -> Dict:
        
        print(f"\n{'='*70}")
        print(f"COMPARACIÓN DE ALGORITMOS")
        print(f"{'='*70}")
        print(f"Origen: {nodos_washington[origen_id].nombre}")
        print(f"Destino: {nodos_washington[destino_id].nombre}")
        
        origen_vial = nodos_washington[origen_id].nodo_vial_cercano
        destino_vial = nodos_washington[destino_id].nodo_vial_cercano
        
        resultados = {}
        
        print(f"\n Ejecutando Dijkstra...")
        ruta_dijk, peso_dijk, info_dijk = self.calcular_con_dijkstra(
            G_vial, origen_vial, destino_vial
        )
        resultados['Dijkstra'] = {
            'ruta': ruta_dijk,
            'info': info_dijk
        }
        print(f"    Tiempo: {info_dijk.get('tiempo_ejecucion_ms', 0):.2f} ms")
        if ruta_dijk:
            print(f"    Distancia: {info_dijk.get('distancia_km', 0):.2f} km")
        
        print(f"\n Ejecutando Bellman-Ford...")
        ruta_bell, peso_bell, info_bell = self.calcular_con_bellman_ford(
            G_vial, origen_vial, destino_vial
        )
        resultados['Bellman-Ford'] = {
            'ruta': ruta_bell,
            'info': info_bell
        }
        print(f"    Tiempo: {info_bell.get('tiempo_ejecucion_ms', 0):.2f} ms")
        if ruta_bell:
            print(f"    Distancia: {info_bell.get('distancia_km', 0):.2f} km")
        
        print(f"\n Ejecutando A*...")
        ruta_astar, peso_astar, info_astar = self.calcular_con_astar(
            G_vial, origen_vial, destino_vial
        )
        resultados['A*'] = {
            'ruta': ruta_astar,
            'info': info_astar
        }
        print(f"    Tiempo: {info_astar.get('tiempo_ejecucion_ms', 0):.2f} ms")
        if ruta_astar:
            print(f"    Distancia: {info_astar.get('distancia_km', 0):.2f} km")
        
        if sistema_ia and sistema_ia.entrenado:
            print(f"\n Ejecutando IA...")
            pred_ia = self.calcular_con_ia(
                sistema_ia, G_vial, nodos_washington,
                origen_id, destino_id, gestor_factores
            )
            resultados['IA'] = {
                'ruta': None,
                'info': pred_ia
            }
            print(f"    Tiempo: {pred_ia.get('tiempo_ejecucion_ms', 0):.2f} ms")
            print(f"    Predicción: {pred_ia.get('distancia_km', 0):.2f} km")
        else:
            print(f"\n  IA no entrenada, omitiendo...")
        
        self.resultados = resultados
        return resultados
    
    def imprimir_tabla_comparativa(self):
        
        if not self.resultados:
            print("  No hay resultados para mostrar")
            return
        
        print(f"\n{'='*70}")
        print(f"TABLA COMPARATIVA DE RESULTADOS")
        
        print(f"\n{'Algoritmo':<20} {'Distancia (km)':<15} {'Tiempo (min)':<15} {'Ejecución (ms)':<15}")
        print(f"{'-'*70}")
        
        for algoritmo, datos in self.resultados.items():
            info = datos['info']
            
            distancia = info.get('distancia_km', 0)
            tiempo = info.get('tiempo_min', 0)
            tiempo_ejec = info.get('tiempo_ejecucion_ms', 0)
            
            print(f"{algoritmo:<20} {distancia:<15.2f} {tiempo:<15.2f} {tiempo_ejec:<15.2f}")
        
        print(f"\n{'='*70}")
        print(f"\n\n Resultado")
        
        tiempos = {alg: datos['info'].get('tiempo_ejecucion_ms', float('inf')) 
                   for alg, datos in self.resultados.items()}
        mas_rapido = min(tiempos, key=tiempos.get)
        
        print(f"\n Algoritmo más rápido: {mas_rapido} ({tiempos[mas_rapido]:.2f} ms)")
        
        distancias = {alg: datos['info'].get('distancia_km', 0) 
                      for alg, datos in self.resultados.items() 
                      if alg != 'IA' and datos['info'].get('distancia_km', 0) > 0}
        
        if distancias:
            distancias_unicas = set(round(d, 2) for d in distancias.values())
            if len(distancias_unicas) == 1:
                print(f" Todos los algoritmos encontraron la misma ruta óptima")
            else:
                print(f"  Los algoritmos encontraron rutas diferentes:")
                for alg, dist in distancias.items():
                    print(f" {alg}: {dist:.2f} km")
        
        if 'IA' in self.resultados and distancias:
            dist_ia = self.resultados['IA']['info'].get('distancia_km', 0)
            if dist_ia > 0:
                dist_real = list(distancias.values())[0]
                
                if dist_real > 0:
                    error = abs(dist_ia - dist_real)
                    error_pct = (error / dist_real) * 100
                    
                    print(f"\n Precisión de IA:")
                    print(f"   Error absoluto: {error:.2f} km")
                    print(f"   Error relativo: {error_pct:.2f}%")
                    
                    if error_pct < 5:
                        print(f"    Excelente precisión!")
                    elif error_pct < 10:
                        print(f"    Buena precisión")
                    elif error_pct < 20:
                        print(f"     Precisión aceptable")
                    else:
                        print(f"    Precisión mejorable")
                        
    def graficar_comparacion(self, archivo: str = "comparacion_algoritmos.png"):
        
        if not self.resultados:
            print("  No hay resultados para graficar")
            return
        
        
        matplotlib.use('Agg')
        
        print(f"\n Generando gráficos comparativos...")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Comparación de Algoritmos de Rutas', fontsize=16, fontweight='bold')
        
        algoritmos = list(self.resultados.keys())
        
        ax1 = axes[0, 0]
        distancias = []
        colores = []
        
        for alg in algoritmos:
            info = self.resultados[alg]['info']
            if alg == 'IA':
                dist = info.get('distancia_km', 0)
                colores.append('#e74c3c')
            else:
                dist = info.get('distancia_km', 0)
                colores.append('#3498db')
            distancias.append(dist)
        
        bars1 = ax1.bar(algoritmos, distancias, color=colores, alpha=0.8, edgecolor='black')
        ax1.set_ylabel('Distancia (km)', fontsize=11, fontweight='bold')
        ax1.set_title('Distancia Total de la Ruta', fontsize=12, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3, linestyle='--')
        
        for bar in bars1:
            height = bar.get_height()
            if height > 0:
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.2f}',
                        ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax2 = axes[0, 1]
        tiempos = []
        
        for alg in algoritmos:
            info = self.resultados[alg]['info']
            if alg == 'IA':
                tiempo = info.get('tiempo_min', 0)
            else:
                tiempo = info.get('tiempo_min', 0)
            tiempos.append(tiempo)
        
        bars2 = ax2.bar(algoritmos, tiempos, color=colores, alpha=0.8, edgecolor='black')
        ax2.set_ylabel('Tiempo (minutos)', fontsize=11, fontweight='bold')
        ax2.set_title('Tiempo Estimado de Viaje', fontsize=12, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3, linestyle='--')
        
        for bar in bars2:
            height = bar.get_height()
            if height > 0:
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}',
                        ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax3 = axes[1, 0]
        tiempos_ejec = []
        
        for alg in algoritmos:
            info = self.resultados[alg]['info']
            tiempo_ejec = info.get('tiempo_ejecucion_ms', 0.001)
            tiempos_ejec.append(tiempo_ejec)
        
        bars3 = ax3.bar(algoritmos, tiempos_ejec, color=colores, alpha=0.8, edgecolor='black')
        ax3.set_ylabel('Tiempo de Ejecución (ms)', fontsize=11, fontweight='bold')
        ax3.set_title('Velocidad de Cómputo (escala log)', fontsize=12, fontweight='bold')
        ax3.set_yscale('log')
        ax3.grid(axis='y', alpha=0.3, linestyle='--', which='both')
        
        for bar in bars3:
            height = bar.get_height()
            if height > 0:
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.2f}',
                        ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax4 = axes[1, 1]
        eficiencias = []
        
        for alg in algoritmos:
            info = self.resultados[alg]['info']
            tiempo_ejec = info.get('tiempo_ejecucion_ms', 0.001)
            
            if alg == 'IA':
                dist = info.get('distancia_km', 0)
            else:
                dist = info.get('distancia_km', 0)
            
            eficiencia = dist / tiempo_ejec if tiempo_ejec > 0 else 0
            eficiencias.append(eficiencia)
        
        bars4 = ax4.bar(algoritmos, eficiencias, color=colores, alpha=0.8, edgecolor='black')
        ax4.set_ylabel('Eficiencia (km/ms)', fontsize=11, fontweight='bold')
        ax4.set_title('Eficiencia Computacional', fontsize=12, fontweight='bold')
        ax4.grid(axis='y', alpha=0.3, linestyle='--')
        
        for bar in bars4:
            height = bar.get_height()
            if height > 0:
                ax4.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.3f}',
                        ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        plt.tight_layout()
        
        try:
            plt.savefig(archivo, dpi=300, bbox_inches='tight')
            print(f"Gráfico guardado: {archivo}")
            
            try:
                import subprocess
                subprocess.run(['xdg-open', archivo], check=False)
            except:
                pass
            
        except Exception as e:
            print(f"❌ Error guardando gráfico: {e}")
        
        plt.close()
