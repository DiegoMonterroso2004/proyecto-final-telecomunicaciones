"""Casos de cierre del informe; conserva el simulador original sin cambios."""
from pathlib import Path
from dataclasses import replace
from simulador import Enlace, exportar

if __name__=='__main__':
    base=Enlace(sensibilidad_dbm=-79.5)
    registros=[('10 km - referencia',base),
               ('35 km - linea base',replace(base,distancia_km=35,diametro_tx_m=1.2,diametro_rx_m=1.2)),
               ('35 km - refuerzo propuesto',replace(base,distancia_km=35,diametro_tx_m=1.8,diametro_rx_m=1.8,potencia_dbm=28))]
    print(exportar(Path(__file__).parent/'resultados_finales',registros))
