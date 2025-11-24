import os
from typing import Dict, List
import folium
import networkx as nx
import numpy as np
from folium import plugins
from clases import Nodo

class VisualizadorRed:
    
    @staticmethod
    def crear_mapa_completo(
        G_vial: nx.MultiDiGraph,
        nodos_washington: Dict[str, Nodo],
        ruta_vial: List[int] = None,
        origen_id: str = None,
        destino_id: str = None,
        info_ruta: Dict = None,
        archivo: str = "mapa_red_real_washington.html"
    ):

        
        if ruta_vial and len(ruta_vial) > 0:
            lats_ruta = [G_vial.nodes[n]['y'] for n in ruta_vial]
            lons_ruta = [G_vial.nodes[n]['x'] for n in ruta_vial]
            centro = [sum(lats_ruta)/len(lats_ruta), sum(lons_ruta)/len(lons_ruta)]
        else:
            lats = [n.latitud for n in nodos_washington.values()]
            lons = [n.longitud for n in nodos_washington.values()]
            centro = [sum(lats)/len(lats), sum(lons)/len(lons)]
        
        mapa = folium.Map(
            location=centro,
            zoom_start=13,
            tiles='OpenStreetMap',
            control_scale=True
        )
        
        folium.TileLayer('CartoDB positron', name='Mapa Claro').add_to(mapa)
        folium.TileLayer('CartoDB dark_matter', name='Mapa Oscuro').add_to(mapa)
        
        titulo = "Red Vial washington"
        if origen_id and destino_id:
            titulo = f"Ruta Real: {nodos_washington[origen_id].nombre} → {nodos_washington[destino_id].nombre}"
        
        titulo_html = f'''
        <div style="position: fixed; top: 10px; left: 50px; width: auto; max-width: 500px;
                    background-color: white; border: 3px solid #2c3e50;
                    z-index: 9999; padding: 15px; border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
            <h3 style="margin: 0 0 10px 0; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">
                {titulo}
            </h3>
            <p style="margin: 5px 0; font-size: 13px; color: #34495e;">
                <b>Red vial:</b> {len(G_vial.nodes):,} intersecciones, {len(G_vial.edges):,} calles<br>
                <b>Nodos washington:</b> {len(nodos_washington)}<br>
                <b>Sistema:</b> Rutas sobre calles reales de washington
            </p>
        '''
        
        if info_ruta:
            titulo_html += f'''
            <hr style="margin: 10px 0; border: 1px solid #bdc3c7;">
            <div style="background-color: #ecf0f1; padding: 10px; border-radius: 5px; margin-top: 10px;">
                <h4 style="margin: 0 0 8px 0; color: #e74c3c;">Información de Ruta</h4>
                <table style="width: 100%; font-size: 12px;">
                    <tr><td><b> Distancia:</b></td><td><b>{info_ruta.get('distancia_total_km', 0):.2f} km</b></td></tr>
                    <tr><td><b> Tiempo:</b></td><td><b>{info_ruta.get('tiempo_total_min', 0):.1f} min</b></td></tr>
                    <tr><td><b> Calles:</b></td><td>{info_ruta.get('num_calles', 0)}</td></tr>
                    <tr><td><b> Acceso:</b></td><td>{info_ruta.get('distancia_acceso_km', 0)*1000:.0f} m</td></tr>
                </table>
            </div>
            '''
        
        titulo_html += '</div>'
        mapa.get_root().html.add_child(folium.Element(titulo_html))
        
        grupo_red_vial = folium.FeatureGroup(name=' Red Vial  (simplificada)', show=False)
        grupo_parcelas = folium.FeatureGroup(name=' Parcelas Agrícolas', show=True)
        grupo_centros = folium.FeatureGroup(name=' Centros de Acopio', show=True)
        grupo_plantas = folium.FeatureGroup(name=' Plantas Procesadoras', show=True)
        grupo_acceso = folium.FeatureGroup(name=' Accesos a Red Vial', show=True)
        grupo_ruta = folium.FeatureGroup(name=' RUTA ÓPTIMA (Calles)', show=True)
        
        if ruta_vial:
            ruta_coords = set()
            for nodo in ruta_vial[:500]:
                ruta_coords.add(nodo)
            
            contador_calles = 0
            for u, v, data in G_vial.edges(data=True):
                if contador_calles > 3000:
                    break
                if u in ruta_coords or v in ruta_coords:
                    coords = [
                        [G_vial.nodes[u]['y'], G_vial.nodes[u]['x']],
                        [G_vial.nodes[v]['y'], G_vial.nodes[v]['x']]
                    ]
                    folium.PolyLine(
                        coords,
                        color='lightgray',
                        weight=1.5,
                        opacity=0.4
                    ).add_to(grupo_red_vial)
                    contador_calles += 1
            print(f"   ✓ {contador_calles} calles cercanas agregadas")
        else:
            for u, v, data in list(G_vial.edges(data=True))[:2000]:
                coords = [
                    [G_vial.nodes[u]['y'], G_vial.nodes[u]['x']],
                    [G_vial.nodes[v]['y'], G_vial.nodes[v]['x']]
                ]
                folium.PolyLine(
                    coords,
                    color='lightgray',
                    weight=1,
                    opacity=0.3
                ).add_to(grupo_red_vial)
        
        print(f" Agregando nodos de washington...")
        colores = {'parcela': 'green', 'centro': 'blue', 'planta': 'red'}
        iconos = {'parcela': 'leaf', 'centro': 'home', 'planta': 'industry'}
        
        for nodo_id, nodo in nodos_washington.items():
            color = colores.get(nodo.tipo, 'gray')
            icono = iconos.get(nodo.tipo, 'info')
            
            es_origen = (nodo_id == origen_id)
            es_destino = (nodo_id == destino_id)
            
            popup_html = f"""
            <div style="font-family: Arial; width: 280px;">
                <h4 style="color: {color}; margin: 0; padding-bottom: 5px; border-bottom: 2px solid {color};">
                    {nodo.nombre}
                </h4>
                <table style="width: 100%; font-size: 12px; margin-top: 10px;">
                    <tr><td><b>ID:</b></td><td>{nodo.id}</td></tr>
                    <tr><td><b>Tipo:</b></td><td>{nodo.tipo.title()}</td></tr>
                    <tr><td><b>Coordenadas:</b></td><td>{nodo.latitud:.4f}, {nodo.longitud:.4f}</td></tr>
                    <tr><td><b>Nodo vial:</b></td><td>#{nodo.nodo_vial_cercano}</td></tr>
                    <tr><td><b>Acceso:</b></td><td>{nodo.distancia_a_vial*1000:.0f} m</td></tr>
            """
            
            if nodo.tipo == 'parcela':
                popup_html += f"<tr><td><b>Producción:</b></td><td>{nodo.produccion_esperada:.0f} ton/año</td></tr>"
            
            if es_origen:
                popup_html += '<tr><td colspan="2" style="background-color: #2ecc71; color: white; text-align: center; padding: 5px; margin-top: 5px;"><b>🚀 ORIGEN</b></td></tr>'
            if es_destino:
                popup_html += '<tr><td colspan="2" style="background-color: #e74c3c; color: white; text-align: center; padding: 5px; margin-top: 5px;"><b>🏁 DESTINO</b></td></tr>'
            
            popup_html += "</table></div>"
            
            if es_origen:
                icon_actual = folium.Icon(color='green', icon='play', prefix='fa', icon_color='white')
            elif es_destino:
                icon_actual = folium.Icon(color='red', icon='flag-checkered', prefix='fa', icon_color='white')
            else:
                icon_actual = folium.Icon(color=color, icon=icono, prefix='fa')
            
            marcador = folium.Marker(
                location=[nodo.latitud, nodo.longitud],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=nodo.nombre,
                icon=icon_actual,
                z_index_offset=1000 if (es_origen or es_destino) else 100
            )
            
            if nodo.tipo == 'parcela':
                marcador.add_to(grupo_parcelas)
            elif nodo.tipo == 'centro':
                marcador.add_to(grupo_centros)
            else:
                marcador.add_to(grupo_plantas)
            
            if nodo.nodo_vial_cercano:
                lat_vial = G_vial.nodes[nodo.nodo_vial_cercano]['y']
                lon_vial = G_vial.nodes[nodo.nodo_vial_cercano]['x']
                
                mostrar_acceso = (es_origen or es_destino or not ruta_vial)
                
                linea_acceso = folium.PolyLine(
                    [[nodo.latitud, nodo.longitud], [lat_vial, lon_vial]],
                    color=color,
                    weight=3 if (es_origen or es_destino) else 2,
                    opacity=0.7 if (es_origen or es_destino) else 0.5,
                    dash_array='5, 5',
                    popup=f"Acceso: {nodo.distancia_a_vial*1000:.0f} m",
                    tooltip=f"Acceso a red vial: {nodo.distancia_a_vial*1000:.0f}m"
                )
                
                if mostrar_acceso:
                    linea_acceso.add_to(grupo_acceso)
                
                if es_origen or es_destino:
                    folium.CircleMarker(
                        location=[lat_vial, lon_vial],
                        radius=5,
                        color=color,
                        fill=True,
                        fillColor=color,
                        fillOpacity=0.7,
                        popup=f"Punto de acceso a red vial",
                        tooltip="Conexión vial"
                    ).add_to(grupo_acceso)
        
        if ruta_vial and len(ruta_vial) > 1:
            print(f"Dibujando ruta óptima ({len(ruta_vial)} intersecciones)...")
            
            coords_ruta = []
            for nodo_vial in ruta_vial:
                lat = G_vial.nodes[nodo_vial]['y']
                lon = G_vial.nodes[nodo_vial]['x']
                coords_ruta.append([lat, lon])
            
            folium.PolyLine(
                coords_ruta,
                color='#e74c3c',
                weight=6,
                opacity=0.9,
                popup=f"<b>Ruta Óptima</b><br>{len(ruta_vial)} intersecciones<br>Sobre calles reales",
                tooltip=f"Ruta calculada: {len(ruta_vial)} puntos"
            ).add_to(grupo_ruta)
            
            folium.PolyLine(
                coords_ruta,
                color='#c0392b',
                weight=8,
                opacity=0.5
            ).add_to(grupo_ruta)
            
            if len(coords_ruta) > 5:
                num_flechas = min(15, len(coords_ruta) // 20)
                if num_flechas > 0:
                    paso = len(coords_ruta) // num_flechas
                    
                    for i in range(0, len(coords_ruta) - paso, paso):
                        try:
                            punto_inicio = coords_ruta[i]
                            punto_fin = coords_ruta[i + paso]
                            
                            lat_diff = punto_fin[0] - punto_inicio[0]
                            lon_diff = punto_fin[1] - punto_inicio[1]
                            angulo = np.arctan2(lat_diff, lon_diff) * 180 / np.pi
                            
                            lat_medio = (punto_inicio[0] + punto_fin[0]) / 2
                            lon_medio = (punto_inicio[1] + punto_fin[1]) / 2
                            
                            folium.RegularPolygonMarker(
                                location=[lat_medio, lon_medio],
                                fill=True,
                                fill_color='red',
                                fill_opacity=0.8,
                                color='darkred',
                                number_of_sides=3,
                                radius=8,
                                rotation=angulo + 90,
                                popup="Dirección de ruta",
                                weight=2
                            ).add_to(grupo_ruta)
                        except:
                            pass
            
            segmentos_marcados = len(ruta_vial) // 10 
            if segmentos_marcados > 0:
                for i in range(0, len(ruta_vial), max(1, len(ruta_vial) // segmentos_marcados)):
                    if i < len(coords_ruta):
                        folium.CircleMarker(
                            location=coords_ruta[i],
                            radius=4,
                            color='darkred',
                            fill=True,
                            fillColor='red',
                            fillOpacity=0.9,
                            popup=f"Intersección #{i} (Nodo vial: {ruta_vial[i]})",
                            tooltip=f"Punto {i+1}/{len(ruta_vial)}",
                            weight=2
                        ).add_to(grupo_ruta)
            
            folium.CircleMarker(
                location=coords_ruta[0],
                radius=8,
                color='green',
                fill=True,
                fillColor='lightgreen',
                fillOpacity=0.9,
                popup="<b> Inicio en red vial</b>",
                tooltip="Punto de inicio en calles",
                weight=3
            ).add_to(grupo_ruta)
            
            folium.CircleMarker(
                location=coords_ruta[-1],
                radius=8,
                color='red',
                fill=True,
                fillColor='orange',
                fillOpacity=0.9,
                popup="<b>🏁 Fin en red vial</b>",
                tooltip="Punto final en calles",
                weight=3
            ).add_to(grupo_ruta)
            
            print(f"    Ruta dibujada con {len(coords_ruta)} puntos")
            print(f"    Segmentos visualizados: {len(ruta_vial)-1}")
            
            try:
                mapa.fit_bounds([[min(c[0] for c in coords_ruta), min(c[1] for c in coords_ruta)],
                                [max(c[0] for c in coords_ruta), max(c[1] for c in coords_ruta)]])
            except:
                pass
        
        grupo_red_vial.add_to(mapa)
        grupo_parcelas.add_to(mapa)
        grupo_centros.add_to(mapa)
        grupo_plantas.add_to(mapa)
        grupo_acceso.add_to(mapa)
        grupo_ruta.add_to(mapa)
        
        folium.LayerControl(collapsed=False, position='topright').add_to(mapa)
        plugins.Fullscreen(position='topleft', title='Pantalla completa', title_cancel='Salir').add_to(mapa)
        plugins.MeasureControl(
            position='bottomleft',
            primary_length_unit='kilometers',
            secondary_length_unit='meters'
        ).add_to(mapa)
        
        try:
            minimap = plugins.MiniMap(
                toggle_display=True,
                position='bottomright',
                width=150,
                height=150
            )
            mapa.add_child(minimap)
        except:
            pass
        
        leyenda_html = f'''
        <div style="position: fixed; bottom: 50px; left: 50px; width: 280px;
                    background-color: white; border: 3px solid #2c3e50;
                    z-index: 9999; padding: 15px; border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
            <h4 style="margin: 0 0 10px 0; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">
                 Leyenda
            </h4>
            <div style="font-size: 12px;">
                <p style="margin: 5px 0;"><b>Tipos de nodo:</b></p>
                <p style="margin: 3px 0;">
                    <span style="color: green; font-size: 16px;">●</span> <b>Parcelas agrícolas</b> ( Producción)<br>
                    <span style="color: blue; font-size: 16px;">●</span> <b>Centros de acopio</b> ( Recolección)<br>
                    <span style="color: red; font-size: 16px;">●</span> <b>Plantas procesadoras</b> ( Procesamiento)
                </p>
                <hr style="margin: 10px 0;">
                <p style="margin: 5px 0;"><b>Elementos del mapa:</b></p>
                <p style="margin: 3px 0;">
                    <span style="display: inline-block; width: 30px; height: 3px; background-color: lightgray; vertical-align: middle;"></span> Red vial <br>
                    <span style="display: inline-block; width: 30px; height: 4px; background-color: red; vertical-align: middle;"></span> <b>Ruta óptima</b><br>
                    <span style="display: inline-block; width: 30px; border-top: 2px dashed green; vertical-align: middle;"></span> Acceso a calles<br>
        '''
        
        if ruta_vial:
            leyenda_html += f'''
                </p>
                <hr style="margin: 10px 0;">
                <p style="margin: 5px 0;"><b>Controles:</b></p>
                <p style="margin: 3px 0; font-size: 11px;">
                    • Click en marcadores para ver detalles<br>
                    • Usa las capas para mostrar/ocultar elementos<br>
                    • Herramienta de medición abajo izquierda<br>
                    • Pantalla completa arriba izquierda
                </p>
            '''
        
        leyenda_html += '''
            </div>
        </div>
        '''
        mapa.get_root().html.add_child(folium.Element(leyenda_html))
        
        try:
            mapa.save(archivo)
            print(f"\n✅ Mapa guardado exitosamente: {archivo}")
            file_size = os.path.getsize(archivo) / 1024
            print(f"   📁 Tamaño: {file_size:.1f} KB")
        except Exception as e:
            print(f"\n❌ Error guardando mapa: {e}")
            return None
        
        return archivo
