from dataclasses import dataclass
from typing import Optional


@dataclass
class Nodo:
    id: str
    nombre: str
    tipo: str
    latitud: float
    longitud: float
    produccion_esperada: float = 0.0
    nodo_vial_cercano: Optional[int] = None 
    distancia_a_vial: float = 0.0


@dataclass
class FactoresExternos:
    trafico: float = 1.0
    clima: str = "despejado"
    retenes: bool = False
    accidente: bool = False
    obras: bool = False
    hora_pico: bool = False
    
    def calcular_penalizacion_tiempo(self) -> float:
        multiplicador = self.trafico
        if self.clima == "lluvia": multiplicador *= 1.3
        elif self.clima == "tormenta": multiplicador *= 1.8
        elif self.clima == "niebla": multiplicador *= 1.5
        if self.retenes: multiplicador *= 1.2
        if self.accidente: multiplicador *= 2.5
        if self.obras: multiplicador *= 1.4
        if self.hora_pico: multiplicador *= 1.6
        return multiplicador
    
    def calcular_penalizacion_costo(self) -> float:
        multiplicador = 1.0
        if self.clima in ["lluvia", "tormenta"]:
            multiplicador *= 1.2
        if self.hora_pico:
            multiplicador *= 1.15
        return multiplicador
    
    def obtener_riesgo(self) -> str:
        p = self.calcular_penalizacion_tiempo()
        if p >= 2.5: return "MUY ALTO"
        elif p >= 1.8: return "ALTO"
        elif p >= 1.3: return "MEDIO"
        else: return "BAJO"
    
    def to_dict(self):
        return {
            'trafico': self.trafico,
            'clima': self.clima,
            'retenes': self.retenes,
            'accidente': self.accidente,
            'obras': self.obras,
            'hora_pico': self.hora_pico,
            'penalizacion_tiempo': self.calcular_penalizacion_tiempo(),
            'penalizacion_costo': self.calcular_penalizacion_costo(),
            'riesgo': self.obtener_riesgo()
        }


@dataclass
class AristaVial:
    nodo_origen: int
    nodo_destino: int
    distancia_m: float
    tiempo_base_s: float
    velocidad_maxima: float
    tipo_via: str = "primaria"
    factores: FactoresExternos = None
    
    def __post_init__(self):
        if self.factores is None:
            self.factores = FactoresExternos()
    
    @property
    def tiempo_real_s(self) -> float:
        return self.tiempo_base_s * self.factores.calcular_penalizacion_tiempo()
    
    @property
    def tiempo_real_min(self) -> float:
        return self.tiempo_real_s / 60
    
    @property
    def velocidad_real(self) -> float:
        if self.tiempo_real_s > 0:
            return (self.distancia_m / 1000) / (self.tiempo_real_s / 3600)
        return 0
    
    def actualizar_factores(self, factores: FactoresExternos):
        self.factores = factores
    
    def to_dict(self):
        return {
            'origen': self.nodo_origen,
            'destino': self.nodo_destino,
            'distancia_m': self.distancia_m,
            'distancia_km': self.distancia_m / 1000,
            'tiempo_base_min': self.tiempo_base_s / 60,
            'tiempo_real_min': self.tiempo_real_min,
            'velocidad_maxima': self.velocidad_maxima,
            'velocidad_real': self.velocidad_real,
            'tipo_via': self.tipo_via,
            'factores': self.factores.to_dict()
        }

