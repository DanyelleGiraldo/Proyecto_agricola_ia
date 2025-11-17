

import os
from typing import Dict, List
import webbrowser
from calculador_rutas import CalculadorRutas
from comparador_algoritmos import ComparadorAlgoritmos
from extractor_caracteristicas import ExtractorCaracteristicas
from factores_viales import GestorFactoresViales
from ia_multiobjetivo import IAMultiObjetivo
from integrador_nodos import IntegradorNodos
from redvial import DescargadorRedVial
from visualizador_red import VisualizadorRed
import numpy as np

class ControladorSistema:
    
    def __init__(self):
        self.G_vial = None
        self.nodos_santander = {}
        self.gestor_factores = None
        self.sistema_ia = None
        self.comparador = ComparadorAlgoritmos()
        self.inicializado = False
    
    def inicializar_sistema(self):
        """Inicializa el sistema completo"""
        print(f"\n{'='*70}")
        print(f"INICIALIZANDO SISTEMA")
        print(f"{'='*70}")
        
        print(f"\n[1/4] Red vial de Bucaramanga...")
        archivo_red = "bucaramanga_red_vial.graphml"
        
        if os.path.exists(archivo_red):
            print(f"    Archivo encontrado, cargando...")
            self.G_vial = DescargadorRedVial.cargar_red_guardada(archivo_red)
        else:
            print(f"     No se encontró archivo guardado, descargando...")
            self.G_vial = DescargadorRedVial.descargar_red_bucaramanga(
    incluir_floridablanca=False,
    guardar=True
)
        
        if self.G_vial is None:
            print(f"\n Error: No se pudo obtener la red vial")
            return False
        
        print(f"\n[2/4] Nodos de Santander...")
        nodos_lista = IntegradorNodos.obtener_nodos_santander()
        self.nodos_santander = {n.id: n for n in nodos_lista}
        print(f"    {len(self.nodos_santander)} nodos cargados")
        
        print(f"\n[3/4] Conectando nodos a red vial...")
        conexiones = IntegradorNodos.conectar_nodos_a_red_vial(
            nodos_lista,
            self.G_vial
        )
        
        print(f"\n[4/4] Inicializando gestor de factores externos...")
        self.gestor_factores = GestorFactoresViales(self.G_vial)
        
        self.sistema_ia = IAMultiObjetivo()
        
        self.inicializado = True
        
        print(f"\n{'='*70}")
        print(f" SISTEMA INICIALIZADO CORRECTAMENTE")
        print(f"\n Resumen:")
        print(f"   Red vial: {len(self.G_vial.nodes):,} intersecciones")
        print(f"   Calles: {len(self.G_vial.edges):,}")
        print(f"   Nodos Santander: {len(self.nodos_santander)}")
        print(f"   Conexiones exitosas: {len(conexiones)}")
        
        return True
    
    def entrenar_ia(self, num_escenarios: int = 3):
        
        if not self.inicializado:
            print(f"  Sistema no inicializado. Ejecuta primero la opción 1.")
            return
        
        print(f"\n{'='*70}")
        print(f"\n\n ENTRENANDO SISTEMA DE IA")
        
        X, targets = self.sistema_ia.generar_dataset_multiobjetivo(
            self.G_vial,
            self.nodos_santander,
            self.gestor_factores,
            num_escenarios=num_escenarios
        )
        
        if len(X) == 0:
            print(f" No se generó dataset válido")
            return
        
        self.sistema_ia.entrenar(X, targets)
        
        self.sistema_ia.guardar()
        
        print(f"\n Sistema de IA entrenado y guardado")
    
    def calcular_ruta_real(self, origen_id: str, destino_id: str):
        
        if not self.inicializado:
            print(f"  Sistema no inicializado")
            return None, None
        
        ruta, info = CalculadorRutas.calcular_ruta_santander(
            self.G_vial,
            self.nodos_santander,
            origen_id,
            destino_id,
            self.gestor_factores
        )
        
        return ruta, info
    
    def visualizar_ruta(self, origen_id: str, destino_id: str, ruta_vial: List[int], info: Dict):
        
        if not self.inicializado:
            print(f"  Sistema no inicializado")
            return
        
        archivo = VisualizadorRed.crear_mapa_completo(
            self.G_vial,
            self.nodos_santander,
            ruta_vial,
            origen_id,
            destino_id,
            info
        )
        
        if archivo:
            try:
                webbrowser.open('file://' + os.path.abspath(archivo))
                print(f"Abriendo mapa en navegador...")
            except:
                print(f"  No se pudo abrir automáticamente. Abre manualmente: {archivo}")
    
    def menu_interactivo(self):
        
        while True:
            print(f"\n{'='*70}")
            print(f" MENÚ PRINCIPAL - SISTEMA IA BUCARAMANGA")
            print(f"{'='*70}")
            print(f"\n OPCIONES DISPONIBLES:\n")
            print(f"  1. Inicializar sistema (descargar red vial)")
            print(f"  2. Entrenar IA con rutas ")
            print(f"  3.  Calcular y visualizar ruta específica")
            print(f"  4. Simular factores externos")
            print(f"  5. Comparar IA vs Rutas Reales")
            print(f"  6. Ver estadísticas del sistema")
            print(f"  7. Recargar modelo de IA guardado")
            print(f"  8.  Visualizar mapa completo sin ruta")
            print(f"  9. Comparar todos los algoritmos (1 ruta)")
            print(f"  10. Comparar algoritmos en múltiples rutas")
            print(f"  11. Ver tabla comparativa de últimos resultados")
            print(f"  0. Salir")
            
            print(f"\n{'='*70}")
            opcion = input("Selecciona una opción: ").strip()
            
            if opcion == "1":
                self.inicializar_sistema()
            
            elif opcion == "2":
                if not self.inicializado:
                    print(f"  Primero debes inicializar el sistema (opción 1)")
                    continue
                
                print(f"\n¿Cuántos escenarios deseas simular por ruta?")
                print(f"  1 = Rápido (solo condiciones normales)")
                print(f"  3 = Balanceado (normal, hora pico, clima)")
                print(f"  5 = Completo (muchos escenarios)")
                
                try:
                    num_esc = int(input("Número de escenarios [3]: ").strip() or "3")
                    self.entrenar_ia(num_esc)
                except:
                    print(f" Entrada inválida")
            
            elif opcion == "3":
                if not self.inicializado:
                    print(f"  Primero debes inicializar el sistema (opción 1)")
                    continue
                
                print(f"\n Nodos disponibles:")
                for nodo in self.nodos_santander.values():
                    print(nodo.id, nodo.nombre)
                    
                
                origen = input("\nID nodo origen (ej: P001): ").strip().upper()
                destino = input("ID nodo destino (ej: C001): ").strip().upper()
                
                if origen not in self.nodos_santander or destino not in self.nodos_santander:
                    print(f" Nodos inválidos")
                    continue
                
                ruta, info = self.calcular_ruta_real(origen, destino)
                
                if ruta:
                    print(f"\n¿Visualizar en mapa? (s/n): ", end="")
                    if input().strip().lower() == 's':
                        self.visualizar_ruta(origen, destino, ruta, info)
            
            elif opcion == "4":
                if not self.inicializado:
                    print(f"  Primero debes inicializar el sistema (opción 1)")
                    continue
                
                print(f"\n SIMULACIONES DE FACTORES EXTERNOS:")
                print(f"  1. Hora pico")
                print(f"  2. Clima adverso (lluvia)")
                print(f"  3. Condiciones aleatorias")
                print(f"  4. Limpiar factores (volver a normal)")
                
                sim = input("\nSelecciona simulación: ").strip()
                
                if sim == "1":
                    self.gestor_factores.simular_hora_pico(True)
                elif sim == "2":
                    self.gestor_factores.simular_clima_adverso("lluvia")
                elif sim == "3":
                    self.gestor_factores.simular_condiciones_aleatorias(0.3)
                elif sim == "4":
                    self.gestor_factores.limpiar_factores()
                
                stats = self.gestor_factores.obtener_estadisticas()
                print(f"\n Estadísticas actuales:")
                print(f"   Tráfico alto: {stats['trafico_alto']}")
                print(f"   Clima adverso: {stats['clima_adverso']}")
                print(f"   Retenes: {stats['retenes']}")
                print(f"   Accidentes: {stats['accidentes']}")
                print(f"   Obras: {stats['obras']}")
                print(f"   Penalización promedio: {stats['penalizacion_promedio']:.2f}x")
            
            elif opcion == "5":
                if not self.inicializado:
                    print(f"  Sistema no inicializado")
                    continue
                
                if not self.sistema_ia.entrenado:
                    print(f" IA no entrenada. Ejecuta primero la opción 2.")
                    continue
                
                print(f"\n COMPARACIÓN IA VS RUTAS REALES")
                print(f"\nCalculando ruta real...")
                
                origen = "P001"
                destino = "C001"
                
                ruta_real, info_real = self.calcular_ruta_real(origen, destino)
                
                if ruta_real:
                    print(f"\n Predicción de IA:")
                    features = ExtractorCaracteristicas.extraer_features(
                        self.G_vial,
                        self.nodos_santander,
                        origen,
                        destino,
                        self.gestor_factores
                    )
                    
                    pred = self.sistema_ia.predecir_ruta(features)
                    
                    print(f"\n COMPARACIÓN:")
                    print(f"{'Métrica':<20} {'IA':<15} {'Real':<15} {'Diff':<15}")
                    print(f"{'-'*65}")
                    
                    dist_diff = abs(pred['distancia_km'] - info_real['distancia_total_km'])
                    tiempo_diff = abs(pred['tiempo_min'] - info_real['tiempo_total_min'])
                    
                    print(f"{'Distancia (km)':<20} {pred['distancia_km']:<15.2f} {info_real['distancia_total_km']:<15.2f} {dist_diff:<15.2f}")
                    print(f"{'Tiempo (min)':<20} {pred['tiempo_min']:<15.1f} {info_real['tiempo_total_min']:<15.1f} {tiempo_diff:<15.1f}")
                    print(f"{'Riesgo':<20} {pred['riesgo']:<15} {'N/A':<15} {'N/A':<15}")
                    print(f"{'Calidad':<20} {pred['score_calidad']:<15.1f} {'N/A':<15} {'N/A':<15}")
                    
                    print(f"\n Precisión:")
                    print(f"   Error distancia: {dist_diff/info_real['distancia_total_km']*100:.1f}%")
                    print(f"   Error tiempo: {tiempo_diff/info_real['tiempo_total_min']*100:.1f}%")
            
            elif opcion == "6":
                if not self.inicializado:
                    print(f"  Sistema no inicializado")
                    continue
                
                print(f"\n ESTADÍSTICAS DEL SISTEMA")
                print(f"{'='*70}")
                
                print(f"\n  Red Vial:")
                print(f"   Intersecciones: {len(self.G_vial.nodes):,}")
                print(f"   Calles: {len(self.G_vial.edges):,}")
                
                print(f"\n Nodos Santander:")
                tipos = {}
                for nodo in self.nodos_santander.values():
                    tipos[nodo.tipo] = tipos.get(nodo.tipo, 0) + 1
                
                for tipo, cantidad in tipos.items():
                    print(f"   {tipo.title()}: {cantidad}")
                
                if self.sistema_ia.entrenado:
                    print(f"\n Modelos de IA:")
                    print(f"   Estado: ENTRENADOS ")
                    print(f"   Métricas:")
                    for modelo, metricas in self.sistema_ia.metricas.items():
                        print(f"     {modelo.title()}:")
                        for metrica, valor in metricas.items():
                            print(f"       {metrica}: {valor:.4f}")
                
                stats_factores = self.gestor_factores.obtener_estadisticas()
                print(f"\n Factores Externos Actuales:")
                print(f"   Tráfico alto: {stats_factores['trafico_alto']} calles")
                print(f"   Clima adverso: {stats_factores['clima_adverso']} calles")
                print(f"   Retenes: {stats_factores['retenes']}")
                print(f"   Accidentes: {stats_factores['accidentes']}")
                print(f"   Obras: {stats_factores['obras']}")
                print(f"   Penalización promedio: {stats_factores['penalizacion_promedio']:.2f}x")
            
            elif opcion == "7":
                archivo = "modelo_ia_multiobjetivo.pkl"
                if os.path.exists(archivo):
                    self.sistema_ia = IAMultiObjetivo()
                    self.sistema_ia.cargar(archivo)
                else:
                    print(f" No se encontró modelo guardado")
            
            elif opcion == "8":
                if not self.inicializado:
                    print(f"  Sistema no inicializado")
                    continue
                
                archivo = VisualizadorRed.crear_mapa_completo(
                    self.G_vial,
                    self.nodos_santander
                )
                
                if archivo:
                    try:
                        webbrowser.open('file://' + os.path.abspath(archivo))
                    except:
                        print(f"  Abre manualmente: {archivo}")
            
            elif opcion == "9":
                if not self.inicializado:
                    print(f"  Sistema no inicializado")
                    continue
                
                print(f"\n Nodos disponibles:")
                print(f"   Parcelas: P001-P015")
                print(f"   Centros: C001-C004")
                print(f"   Plantas: PL001-PL003")
                
                origen = input("\nID nodo origen (ej: P001): ").strip().upper()
                destino = input("ID nodo destino (ej: C001): ").strip().upper()
                
                if origen not in self.nodos_santander or destino not in self.nodos_santander:
                    print(f" Nodos inválidos")
                    continue
                
                resultados = self.comparador.comparar_todos(
                    self.G_vial,
                    self.nodos_santander,
                    origen,
                    destino,
                    self.sistema_ia,
                    self.gestor_factores
                )
                
                self.comparador.imprimir_tabla_comparativa()
                
                print(f"\n¿Generar gráficos? (s/n): ", end="")
                if input().strip().lower() == 's':
                    self.comparador.graficar_comparacion()
            
            elif opcion == "10":
                if not self.inicializado:
                    print(f"  Sistema no inicializado")
                    continue
                
                print(f"\n COMPARACIÓN EN MÚLTIPLES RUTAS")
                
                try:
                    num_rutas = int(input("¿Cuántas rutas comparar? [5]: ").strip() or "5")
                except:
                    num_rutas = 5
                
                import random
                nodos_ids = list(self.nodos_santander.keys())
                pares = []
                
                for _ in range(num_rutas):
                    origen = random.choice(nodos_ids)
                    destino = random.choice([n for n in nodos_ids if n != origen])
                    pares.append((origen, destino))
                
                print(f"\n🔬 Comparando {len(pares)} rutas...")
                
                resultados_multiples = []
                
                for i, (origen, destino) in enumerate(pares, 1):
                    print(f"\n[{i}/{len(pares)}] {origen} → {destino}")
                    
                    resultados = self.comparador.comparar_todos(
                        self.G_vial,
                        self.nodos_santander,
                        origen,
                        destino,
                        self.sistema_ia,
                        self.gestor_factores
                    )
                    
                    resultados_multiples.append(resultados)
                
                print(f"\n📊 Generando gráfico comparativo...")
                self.comparador.generar_grafico_comparativo_multiple(resultados_multiples)
                
                print(f"\n{'='*70}")
                print(f" RESUMEN ESTADÍSTICO")
                print(f"{'='*70}")
                
                algoritmos = list(resultados_multiples[0].keys())
                
                for alg in algoritmos:
                    tiempos = []
                    distancias = []
                    
                    for resultado in resultados_multiples:
                        info = resultado[alg]['info']
                        tiempos.append(info.get('tiempo_ejecucion_ms', 0))
                        
                        if alg == 'IA':
                            distancias.append(info.get('distancia_km', 0))
                        else:
                            distancias.append(info.get('distancia_km', 0))
                    
                    print(f"\n{alg}:")
                    print(f"   Tiempo ejecución promedio: {np.mean(tiempos):.2f} ms")
                    print(f"   Tiempo ejecución mín/máx: {min(tiempos):.2f} / {max(tiempos):.2f} ms")
                    print(f"   Distancia promedio: {np.mean(distancias):.2f} km")
            
            elif opcion == "11":
                self.comparador.imprimir_tabla_comparativa()
            
            elif opcion == "0":
                print(f"\n ¡Hasta luego!")
                break
            
            else:
                print(f" Opción inválida")
            
            input(f"\nPresiona Enter para continuar...")
