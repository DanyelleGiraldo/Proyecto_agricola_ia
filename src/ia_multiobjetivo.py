from sklearn.discriminant_analysis import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
import joblib

import numpy as np
from typing import Dict, List, Tuple

from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

from calculador_rutas import CalculadorRutas
from extractor_caracteristicas import ExtractorCaracteristicas

class IAMultiObjetivo:
    
    def __init__(self):
        self.modelo_distancia = GradientBoostingRegressor(
            n_estimators=300,
            max_depth=8,
            learning_rate=0.05,
            subsample=0.8,
            random_state=42
        )
        
        self.modelo_tiempo = GradientBoostingRegressor(
            n_estimators=300,
            max_depth=8,
            learning_rate=0.05,
            subsample=0.8,
            random_state=42
        )
        
        self.modelo_riesgo = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            random_state=42
        )
        
        self.modelo_calidad = GradientBoostingRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        
        self.scaler = StandardScaler()
        self.entrenado = False
        self.metricas = {}
    
    def generar_dataset_multiobjetivo(
        self,
        G_vial,
        nodos_washington: Dict,
        gestor_factores,
        num_escenarios: int = 3
    ) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:

        print(f"\n{'='*70}")
        print(f"\nGENERANDO DATASET MULTI-OBJETIVO")
        print(f"\n\nEscenarios por ruta: {num_escenarios}")
        
        X = []
        y_distancia = []
        y_tiempo = []
        y_riesgo = []
        y_calidad = []
        
        nodos_ids = list(nodos_washington.keys())
        total_pares = len(nodos_ids) * (len(nodos_ids) - 1)
        total_calculos = total_pares * num_escenarios
        
        print(f" Total rutas a calcular: {total_calculos:,}")
        
        contador = 0
        rutas_exitosas = 0
        
        escenarios = [
            ("Normal", lambda: gestor_factores.limpiar_factores()),
            ("Hora Pico", lambda: gestor_factores.simular_hora_pico(True)),
            ("Clima Adverso", lambda: gestor_factores.simular_clima_adverso("lluvia")),
        ]
        
        for escenario_nombre, escenario_func in escenarios[:num_escenarios]:
            print(f"\n Escenario: {escenario_nombre}")
            escenario_func()
            
            for origen_id in nodos_ids:
                for destino_id in nodos_ids:
                    if origen_id == destino_id:
                        continue
                    
                    contador += 1
                    
                    if contador % 50 == 0:
                        print(f"   Progreso: {contador}/{total_calculos} "
                              f"({contador*100//total_calculos}%) - "
                              f"Exitosas: {rutas_exitosas}")
                    
                    ruta, info = CalculadorRutas.calcular_ruta_washington(
                        G_vial,
                        nodos_washington,
                        origen_id,
                        destino_id,
                        gestor_factores
                    )
                    
                    if not ruta or 'distancia_total_km' not in info:
                        continue
                    
                    features = ExtractorCaracteristicas.extraer_features(
                        G_vial,
                        nodos_washington,
                        origen_id,
                        destino_id,
                        gestor_factores
                    )
                    
                    distancia = info['distancia_total_km']
                    tiempo = info['tiempo_total_min']
                    penalizacion = info.get('penalizacion_promedio', 1.0)
                    
                    if penalizacion >= 2.0:
                        riesgo = 3  
                    elif penalizacion >= 1.5:
                        riesgo = 2 
                    else:
                        riesgo = 1 
                    
                    score_distancia = max(0, 100 - distancia * 2)
                    score_tiempo = max(0, 100 - tiempo * 1.5)
                    score_riesgo = max(0, 100 - (penalizacion - 1) * 50)
                    
                    calidad = (score_distancia + score_tiempo + score_riesgo) / 3
                    
                    X.append(features)
                    y_distancia.append(distancia)
                    y_tiempo.append(tiempo)
                    y_riesgo.append(riesgo)
                    y_calidad.append(calidad)
                    rutas_exitosas += 1
        
        gestor_factores.limpiar_factores()
        
        print(f"\n Dataset generado:")
        print(f"   Total calculados: {contador:,}")
        print(f"   Exitosos: {rutas_exitosas:,}")
        print(f"   Ejemplos finales: {len(X):,}")
        
        targets = {
            'distancia': np.array(y_distancia),
            'tiempo': np.array(y_tiempo),
            'riesgo': np.array(y_riesgo),
            'calidad': np.array(y_calidad)
        }
        
        return np.array(X), targets
    
    def entrenar(self, X: np.ndarray, targets: Dict[str, np.ndarray]):
        
        indices = np.arange(len(X))
        train_idx, test_idx = train_test_split(
            indices, test_size=0.2, random_state=42
        )
        
        X_train = X[train_idx]
        X_test = X[test_idx]
        
        print(f" Train: {len(X_train)} | Test: {len(X_test)}")
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        self.metricas = {}
        
        print(f"\n Entrenando modelo de DISTANCIA...")
        y_dist_train = targets['distancia'][train_idx]
        y_dist_test = targets['distancia'][test_idx]
        
        self.modelo_distancia.fit(X_train_scaled, y_dist_train)
        pred_dist = self.modelo_distancia.predict(X_test_scaled)
        
        mae_dist = mean_absolute_error(y_dist_test, pred_dist)
        r2_dist = r2_score(y_dist_test, pred_dist)
        
        self.metricas['distancia'] = {'mae': mae_dist, 'r2': r2_dist}
        print(f"   MAE: {mae_dist:.2f} km | R²: {r2_dist:.4f}")
        
        print(f"\n Entrenando modelo de TIEMPO...")
        y_tiempo_train = targets['tiempo'][train_idx]
        y_tiempo_test = targets['tiempo'][test_idx]
        
        self.modelo_tiempo.fit(X_train_scaled, y_tiempo_train)
        pred_tiempo = self.modelo_tiempo.predict(X_test_scaled)
        
        mae_tiempo = mean_absolute_error(y_tiempo_test, pred_tiempo)
        r2_tiempo = r2_score(y_tiempo_test, pred_tiempo)
        
        self.metricas['tiempo'] = {'mae': mae_tiempo, 'r2': r2_tiempo}
        print(f"   MAE: {mae_tiempo:.2f} min | R²: {r2_tiempo:.4f}")
        
        print(f"\n Entrenando modelo de RIESGO...")
        y_riesgo_train = targets['riesgo'][train_idx]
        y_riesgo_test = targets['riesgo'][test_idx]
        
        self.modelo_riesgo.fit(X_train_scaled, y_riesgo_train)
        pred_riesgo = self.modelo_riesgo.predict(X_test_scaled)
        
        from sklearn.metrics import accuracy_score
        acc_riesgo = accuracy_score(y_riesgo_test, pred_riesgo)
        
        self.metricas['riesgo'] = {'accuracy': acc_riesgo}
        print(f"   Accuracy: {acc_riesgo:.2%}")
        
        print(f"\n Entrenando modelo de CALIDAD...")
        y_calidad_train = targets['calidad'][train_idx]
        y_calidad_test = targets['calidad'][test_idx]
        
        self.modelo_calidad.fit(X_train_scaled, y_calidad_train)
        pred_calidad = self.modelo_calidad.predict(X_test_scaled)
        
        mae_calidad = mean_absolute_error(y_calidad_test, pred_calidad)
        r2_calidad = r2_score(y_calidad_test, pred_calidad)
        
        self.metricas['calidad'] = {'mae': mae_calidad, 'r2': r2_calidad}
        print(f"   MAE: {mae_calidad:.2f} pts | R²: {r2_calidad:.4f}")
        
        self.entrenado = True
        
        print(f"\n{'='*70}")
        print(f"ENTRENAMIENTO COMPLETADO")
        print(f"{'='*70}")
        print(f"\n La IA ahora puede:")
        print(f"    Predecir distancia con ±{mae_dist:.2f} km de error")
        print(f"    Predecir tiempo con ±{mae_tiempo:.2f} min de error")
        print(f"    Clasificar riesgo con {acc_riesgo:.1%} precisión")
        print(f"    Evaluar calidad general de rutas")
    
    def predecir_ruta(
        self,
        features: np.ndarray
    ) -> Dict[str, any]:
        if not self.entrenado:
            raise Exception("Modelos no entrenados")
        
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        
        distancia = self.modelo_distancia.predict(features_scaled)[0]
        tiempo = self.modelo_tiempo.predict(features_scaled)[0]
        riesgo = self.modelo_riesgo.predict(features_scaled)[0]
        calidad = self.modelo_calidad.predict(features_scaled)[0]
        
        prob_riesgo = self.modelo_riesgo.predict_proba(features_scaled)[0]
        
        riesgo_nombres = {1: 'BAJO', 2: 'MEDIO', 3: 'ALTO'}
        
        return {
            'distancia_km': distancia,
            'tiempo_min': tiempo,
            'riesgo': riesgo_nombres.get(riesgo, 'DESCONOCIDO'),
            'prob_bajo': prob_riesgo[0] if len(prob_riesgo) > 0 else 0,
            'prob_medio': prob_riesgo[1] if len(prob_riesgo) > 1 else 0,
            'prob_alto': prob_riesgo[2] if len(prob_riesgo) > 2 else 0,
            'score_calidad': calidad
        }
    
    def recomendar_mejor_ruta(
        self,
        rutas_candidatas: List[Tuple[str, str]],
        G_vial,
        nodos_washington: Dict,
        gestor_factores,
        prioridad: str = 'balanceado'
    ) -> Tuple[str, str, Dict]:

        print(f"\n Evaluando {len(rutas_candidatas)} rutas candidatas...")
        print(f"   Prioridad: {prioridad.upper()}")
        
        evaluaciones = []
        
        for origen_id, destino_id in rutas_candidatas:
            features = ExtractorCaracteristicas.extraer_features(
                G_vial,
                nodos_washington,
                origen_id,
                destino_id,
                gestor_factores
            )
            
            pred = self.predecir_ruta(features)
            
            if prioridad == 'distancia':
                score = -pred['distancia_km']
            elif prioridad == 'tiempo':
                score = -pred['tiempo_min']
            elif prioridad == 'seguridad':
                score = pred['prob_bajo'] * 100 - pred['prob_alto'] * 50
            else:
                score = pred['score_calidad']
            
            evaluaciones.append({
                'origen': origen_id,
                'destino': destino_id,
                'score': score,
                'prediccion': pred
            })
        
        evaluaciones.sort(key=lambda x: x['score'], reverse=True)
        
        mejor = evaluaciones[0]
        
        print(f"\n MEJOR RUTA ENCONTRADA:")
        print(f"   {mejor['origen']} → {mejor['destino']}")
        print(f"   Score: {mejor['score']:.2f}")
        print(f"   Distancia: {mejor['prediccion']['distancia_km']:.2f} km")
        print(f"   Tiempo: {mejor['prediccion']['tiempo_min']:.1f} min")
        print(f"   Riesgo: {mejor['prediccion']['riesgo']}")
        print(f"   Calidad: {mejor['prediccion']['score_calidad']:.1f}/100")
        
        return mejor['origen'], mejor['destino'], mejor['prediccion']
    
    def guardar(self, archivo: str = "modelo_ia_multiobjetivo.pkl"):
        joblib.dump({
            'modelo_distancia': self.modelo_distancia,
            'modelo_tiempo': self.modelo_tiempo,
            'modelo_riesgo': self.modelo_riesgo,
            'modelo_calidad': self.modelo_calidad,
            'scaler': self.scaler,
            'metricas': self.metricas,
            'entrenado': self.entrenado
        }, archivo)
        print(f" Modelos guardados: {archivo}")
    
    def cargar(self, archivo: str = "modelo_ia_multiobjetivo.pkl"):
        datos = joblib.load(archivo)
        self.modelo_distancia = datos['modelo_distancia']
        self.modelo_tiempo = datos['modelo_tiempo']
        self.modelo_riesgo = datos['modelo_riesgo']
        self.modelo_calidad = datos['modelo_calidad']
        self.scaler = datos['scaler']
        self.metricas = datos['metricas']
        self.entrenado = datos['entrenado']
        print(f" Modelos cargados: {archivo}")
