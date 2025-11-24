from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from typing import Dict, Tuple
import networkx as nx
import numpy as np
import joblib

from calculador_rutas import CalculadorRutas
from clases import Nodo
from extractor_caracteristicas import ExtractorCaracteristicas

class EntrenadorIA:
    
    def __init__(self):        
        self.modelo = RandomForestRegressor(
            n_estimators=200,
            max_depth=20,
            min_samples_split=5,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.entrenado = False
        self.metricas = {}
    
    def generar_dataset_real(
        self,
        G_vial: nx.MultiDiGraph,
        nodos_washington: Dict[str, Nodo]
    ) -> Tuple[np.ndarray, np.ndarray]:

        print(f"\n\n GENERANDO DATASET CON RUTAS ")
        
        X = []
        y = []
        
        nodos_ids = list(nodos_washington.keys())
        total_pares = len(nodos_ids) * (len(nodos_ids) - 1)
        
        print(f"Calculando {total_pares} rutas ...")        
        contador = 0
        rutas_exitosas = 0
        
        for origen_id in nodos_ids:
            for destino_id in nodos_ids:
                if origen_id != destino_id:
                    contador += 1
                    
                    if contador % 20 == 0:
                        print(f"   Progreso: {contador}/{total_pares} ({contador*100//total_pares}%) - Exitosas: {rutas_exitosas}")
                    
                    ruta, info = CalculadorRutas.calcular_ruta_washington(
                        G_vial,
                        nodos_washington,
                        origen_id,
                        destino_id
                    )
                    
                    if ruta and 'distancia_total_km' in info:
                        features = ExtractorCaracteristicas.extraer_features(
                            G_vial,
                            nodos_washington,
                            origen_id,
                            destino_id
                        )
                        
                        X.append(features)
                        y.append(info['distancia_total_km'])
                        rutas_exitosas += 1
        
        print(f"\nDataset generado:")
        print(f"   Total de rutas calculadas: {contador}")
        print(f"   Rutas exitosas: {rutas_exitosas}")
        print(f"   Ejemplos para IA: {len(X)}")
        
        return np.array(X), np.array(y)
    
    def entrenar(self, X: np.ndarray, y: np.ndarray):
        
        print(f"ENTRENANDO IA CON RUTAS")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print(f" Train: {len(X_train)} | Test: {len(X_test)}")
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        print(f"\n⏳ Entrenando Random Forest...")
        self.modelo.fit(X_train_scaled, y_train)
        
        y_pred_train = self.modelo.predict(X_train_scaled)
        y_pred_test = self.modelo.predict(X_test_scaled)
        
        mae_train = mean_absolute_error(y_train, y_pred_train)
        mae_test = mean_absolute_error(y_test, y_pred_test)
        r2_train = r2_score(y_train, y_pred_train)
        r2_test = r2_score(y_test, y_pred_test)
        
        self.metricas = {
            'mae_train': mae_train,
            'mae_test': mae_test,
            'r2_train': r2_train,
            'r2_test': r2_test,
            'num_ejemplos': len(X)
        }
        
        self.entrenado = True
        
        print(f"\n\n ENTRENAMIENTO COMPLETADO")
        print(f"{'='*70}")
        print(f"\n Train: MAE={mae_train:.2f} km | R²={r2_train:.4f}")
        print(f" Test:  MAE={mae_test:.2f} km | R²={r2_test:.4f}")
        print(f"\n La IA aprendió de {len(X)} rutas  ")
    
    def predecir(self, features: np.ndarray) -> float:
        if not self.entrenado:
            raise Exception("Modelo no entrenado")
        
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        return self.modelo.predict(features_scaled)[0]
    
    def guardar(self, archivo: str = "modelo_ia_washington_real.pkl"):
        import joblib
        joblib.dump({
            'modelo': self.modelo,
            'scaler': self.scaler,
            'metricas': self.metricas,
            'entrenado': self.entrenado
        }, archivo)
        print(f" Modelo guardado: {archivo}")
    
    def cargar(self, archivo: str = "modelo_ia_washington_real.pkl"):
        datos = joblib.load(archivo)
        self.modelo = datos['modelo']
        self.scaler = datos['scaler']
        self.metricas = datos['metricas']
        self.entrenado = datos['entrenado']
        print(f"Modelo cargado: {archivo}")
