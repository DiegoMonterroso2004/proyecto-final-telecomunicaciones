"""Simulador académico de enlaces. Python 3.9+; solo biblioteca estándar."""
from typing import Optional
from dataclasses import dataclass, asdict, replace
import argparse
import csv
import html
import json
import math
from pathlib import Path
import unittest

@dataclass(frozen=True)
class Enlace:
    distancia_km: float = 10
    frecuencia_ghz: float = 6
    ancho_mhz: float = 40
    potencia_dbm: float = 23
    diametro_tx_m: float = .6
    diametro_rx_m: float = .6
    eficiencia: float = .6
    perdida_tx_db: float = 1
    perdida_rx_db: float = 1
    otras_perdidas_db: float = 2
    atenuacion_extra_db: float = 0
    figura_ruido_db: float = 6
    snr_objetivo_db: float = 25
    sensibilidad_dbm: Optional[float] = None
    orden_qam: int = 16
    rolloff: float = 0
    factor_tierra: float = 4/3

def calcular(e):
    for k,v in asdict(e).items():
        if v is None and k == 'sensibilidad_dbm':
            continue
        if not isinstance(v,(float,int)) or not math.isfinite(v):
            raise ValueError(f'{k}: se requiere un número finito')
    for k in ['distancia_km','frecuencia_ghz','ancho_mhz','diametro_tx_m','diametro_rx_m','factor_tierra']:
        if getattr(e,k)<=0: raise ValueError(f'{k}: debe ser mayor que cero')
    if not 0<e.eficiencia<=1: raise ValueError('Eficiencia fuera del intervalo (0, 1]')
    for k in ['perdida_tx_db','perdida_rx_db','otras_perdidas_db','atenuacion_extra_db','figura_ruido_db']:
        if getattr(e,k)<0: raise ValueError(f'{k}: no puede ser negativo')
    if not 0<=e.rolloff<=1: raise ValueError('Exceso de banda fuera del intervalo [0, 1]')
    m=e.orden_qam
    if not float(m).is_integer() or int(m)<4 or int(m)&(int(m)-1) or int(math.isqrt(int(m)))**2!=int(m):
        raise ValueError('Usar QAM cuadrada de orden potencia de dos: 4, 16, 64, 256...')
    lm=.3/e.frecuencia_ghz
    gt=10*math.log10(e.eficiencia*(math.pi*e.diametro_tx_m/lm)**2)
    gr=10*math.log10(e.eficiencia*(math.pi*e.diametro_rx_m/lm)**2)
    fs=92.45+20*math.log10(e.frecuencia_ghz)+20*math.log10(e.distancia_km)
    rx=e.potencia_dbm+gt+gr-fs-e.perdida_tx_db-e.perdida_rx_db-e.otras_perdidas_db-e.atenuacion_extra_db
    ruido=-174+10*math.log10(e.ancho_mhz*1e6)+e.figura_ruido_db
    snr=rx-ruido
    # log(1 + exp(x)) estable para relaciones señal/ruido extremas.
    xx=snr*math.log(10)/10
    sh=e.ancho_mhz*(max(xx,0)+math.log1p(math.exp(-abs(xx))))/math.log(2)
    ideal=e.ancho_mhz*math.log2(m)/(1+e.rolloff)
    fresnel=17.32*math.sqrt(e.distancia_km/(4*e.frecuencia_ghz))
    bulge=1000*(e.distancia_km/2)**2/(2*e.factor_tierra*6371)
    return dict(ganancia_tx_dbi=gt,ganancia_rx_dbi=gr,fspl_db=fs,potencia_rx_dbm=rx,
                ruido_dbm=ruido,cn_db=snr,umbral_snr_dbm=ruido+e.snr_objetivo_db,
                reserva_snr_db=snr-e.snr_objetivo_db,
                fm_db=None if e.sensibilidad_dbm is None else rx-e.sensibilidad_dbm,
                pire_dbm=e.potencia_dbm-e.perdida_tx_db+gt,shannon_mbps=sh,
                tasa_qam_ideal_mbps=ideal,fresnel_m=fresnel,despeje_60_m=.6*fresnel,
                abultamiento_m=bulge,referencia_geometrica_m=.6*fresnel+bulge)

def casos():
    a=Enlace(); b=replace(a,distancia_km=35,diametro_tx_m=1.2,diametro_rx_m=1.2)
    return [('Base 10 km',a),('Base 35 km',b),('10 km con 10 dB extra',replace(a,atenuacion_extra_db=10)),
            ('35 km con 20 dB extra',replace(b,atenuacion_extra_db=20)),
            ('35 km con antenas de 0.60 m',replace(b,diametro_tx_m=.6,diametro_rx_m=.6)),
            ('10 km con NF de 9 dB',replace(a,figura_ruido_db=9)),
            ('10 km con canal de 20 MHz',replace(a,ancho_mhz=20)),
            ('10 km con sensibilidad supuesta -70 dBm',replace(a,sensibilidad_dbm=-70))]

AVISO=('Modelo determinista académico. No simula tráfico de paquetes, terreno real, IPS, '
       'conmutación ni probabilidades de lluvia. No demuestra disponibilidad del 99.97 %. '
       'C/N equivale aquí a SNR en el mismo ancho de banda, sin interferencia. '
       'Fm se calcula solo cuando se proporciona sensibilidad; no se confunde con la reserva de SNR. '
       'Nyquist/QAM y Shannon son límites teóricos, no velocidades útiles garantizadas.')

def exportar(destino, registros):
    out=Path(destino); out.mkdir(parents=True,exist_ok=True)
    records=[{'caso':n,**asdict(e),**calcular(e)} for n,e in registros]
    with (out/'resultados.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0])); w.writeheader(); w.writerows(records)
    (out/'resultados.json').write_text(json.dumps({'advertencia':AVISO,'escenarios':records},ensure_ascii=False,indent=2),encoding='utf-8')
    cols=['caso','potencia_rx_dbm','cn_db','reserva_snr_db','fm_db','shannon_mbps','tasa_qam_ideal_mbps']
    labels=['Escenario','P recibida dBm','C/N dB','Reserva SNR dB','Fm dB','Shannon Mbit/s','QAM ideal Mbit/s']
    rows=''
    for r in records:
        rows+='<tr>'+''.join('<td>'+html.escape('Pendiente' if r[c] is None else f'{r[c]:.2f}' if isinstance(r[c],(float,int)) else str(r[c]))+'</td>' for c in cols)+'</tr>'
    bars=''
    for i,r in enumerate(records):
        y=35+52*i; v=r['reserva_snr_db']; width=min(abs(v)*12,380)
        x=390 if v>=0 else 390-width
        bars+=f'<text x="8" y="{y+16}" font-size="12">{html.escape(r["caso"])}</text><rect x="{x}" y="{y}" width="{width}" height="24" fill="{"#147d64" if v>=0 else "#b64135"}"/><text x="{max(395,x+width+5)}" y="{y+17}" font-size="12">{v:.2f} dB</text>'
    h=70+52*len(records)
    page=f'''<!doctype html><html lang="es"><meta charset="utf-8"><title>Resultados del simulador de enlaces</title>
    <style>body{{font:16px Arial;max-width:1150px;margin:40px auto;padding:0 20px;color:#17252a}} table{{border-collapse:collapse;width:100%;font-size:14px}} td,th{{padding:10px;border:1px solid #ccd4d6;text-align:left}} th{{background:#e9eff0}} p{{line-height:1.55}} svg{{max-width:100%;height:auto}}</style>
    <h1>Resultados del simulador de enlaces</h1><p>{html.escape(AVISO)}</p>
    <table><thead><tr>{''.join('<th>'+x+'</th>' for x in labels)}</tr></thead><tbody>{rows}</tbody></table>
    <h2>Reserva respecto a la SNR objetivo</h2><p>Verde: reserva positiva. Rojo: no alcanza el objetivo de 25 dB. El eje central corresponde a cero.</p>
    <svg role="img" aria-label="Comparación de reservas de SNR" viewBox="0 0 850 {h}"><line x1="390" y1="20" x2="390" y2="{h-15}" stroke="#83949a"/>{bars}</svg>
    <h2>Interpretación</h2><p>La atenuación extra reduce C/N y reserva en la misma cantidad de dB. El escenario de 35 km con 20 dB extra no sostiene la SNR objetivo. Reducir el ancho de banda disminuye ruido integrado, pero reduce la tasa ideal QAM. Una sensibilidad introducida produce un Fm de escenario; no valida por sí sola el receptor ni la disponibilidad.</p>
    <p>Modelo: FSPL = 92.45 + 20 log10(f GHz) + 20 log10(d km); ganancia = 10 log10[η(πD/λ)²]; ruido = -174 + 10 log10(B Hz) + NF; C/N = P recibida - ruido; Fm = P recibida - sensibilidad. Se usa λ ≈ 0.3/f GHz para conservar la convención del capítulo III.</p></html>'''
    (out/'informe.html').write_text(page,encoding='utf-8')
    return out/'informe.html'

class Verificaciones(unittest.TestCase):
    def test_referencia_10(self):
        r=calcular(Enlace()); self.assertAlmostEqual(r['fspl_db'],128.013025,places=5)
        self.assertAlmostEqual(r['potencia_rx_dbm'],-50.396755,places=5)
        self.assertAlmostEqual(r['cn_db'],41.582645,places=5)
    def test_referencia_35(self):
        r=calcular(casos()[1][1]); self.assertAlmostEqual(r['potencia_rx_dbm'],-49.236916,places=5)
        self.assertAlmostEqual(r['reserva_snr_db'],17.742484,places=5)
    def test_atenuacion(self):
        a=calcular(Enlace()); b=calcular(replace(Enlace(),atenuacion_extra_db=10))
        self.assertAlmostEqual(a['cn_db']-b['cn_db'],10)
    def test_duplicar_distancia(self):
        a=calcular(Enlace()); b=calcular(replace(Enlace(),distancia_km=20))
        self.assertAlmostEqual(b['fspl_db']-a['fspl_db'],20*math.log10(2))
    def test_antena(self):
        a=calcular(Enlace()); b=calcular(replace(Enlace(),diametro_tx_m=1.2))
        self.assertAlmostEqual(b['potencia_rx_dbm']-a['potencia_rx_dbm'],20*math.log10(2))
    def test_ancho(self):
        a=calcular(Enlace()); b=calcular(replace(Enlace(),ancho_mhz=20))
        self.assertAlmostEqual(b['cn_db']-a['cn_db'],10*math.log10(2))
        self.assertEqual(b['tasa_qam_ideal_mbps'],80)
    def test_sensibilidad(self):
        self.assertIsNone(calcular(Enlace())['fm_db'])
        self.assertAlmostEqual(calcular(replace(Enlace(),sensibilidad_dbm=-70))['fm_db'],19.603245,places=5)
    def test_shannon_25(self):
        self.assertAlmostEqual(40*math.log2(1+10**2.5),332.375010,places=5)
    def test_rolloff(self):
        self.assertEqual(calcular(replace(Enlace(),rolloff=.25))['tasa_qam_ideal_mbps'],128)
    def test_invalido(self):
        for k,v in [('distancia_km',0),('ancho_mhz',-1),('eficiencia',1.5),('orden_qam',15),('rolloff',-1),('potencia_dbm',float('nan')),('atenuacion_extra_db',-2)]:
            with self.subTest(campo=k), self.assertRaises(ValueError): calcular(replace(Enlace(),**{k:v}))

def ventana(solo_servir=False, puerto=0):
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from secrets import token_urlsafe
    from datetime import datetime
    import webbrowser
    token=token_urlsafe(24)
    base=Path(__file__).parent
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args): pass
        def respuesta(self, code, data, tipo='application/json; charset=utf-8'):
            raw=data if isinstance(data,bytes) else json.dumps(data,ensure_ascii=False).encode('utf-8')
            self.send_response(code); self.send_header('Content-Type',tipo)
            self.send_header('Content-Length',str(len(raw))); self.send_header('Cache-Control','no-store')
            self.end_headers(); self.wfile.write(raw)
        def do_GET(self):
            if self.path=='/'+token+'/': self.respuesta(200,(base/'interfaz.html').read_bytes(),'text/html; charset=utf-8')
            else: self.respuesta(404,{'error':'Ruta inexistente'})
        def do_POST(self):
            if self.path not in ['/'+token+'/calcular','/'+token+'/exportar']:
                self.respuesta(404,{'error':'Ruta inexistente'}); return
            try:
                if self.headers.get_content_type()!='application/json': raise ValueError('Se requiere JSON')
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<20000: raise ValueError('Solicitud no válida')
                e=Enlace(**json.loads(self.rfile.read(length))); r=calcular(e)
                if self.path.endswith('/exportar'):
                    out=exportar(base/'resultados_personalizados'/datetime.now().strftime('%Y%m%d_%H%M%S_%f'),[('Personalizado',e)])
                    self.respuesta(200,{'archivo':str(out)})
                else: self.respuesta(200,r)
            except (ValueError,TypeError,OverflowError,OSError) as exc:
                self.respuesta(400,{'error':str(exc)})
    server=ThreadingHTTPServer(('127.0.0.1',puerto),Handler)
    url=f'http://127.0.0.1:{server.server_port}/{token}/'
    print(url,flush=True)
    print('Simulador local. Para cerrar, presione Ctrl+C en esta consola.',flush=True)
    if not solo_servir: webbrowser.open(url)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch',action='store_true',help='Genera los ocho escenarios de referencia')
    parser.add_argument('--test',action='store_true',help='Ejecuta diez verificaciones automáticas')
    parser.add_argument('--servir',action='store_true',help='Interfaz local sin abrir navegador')
    parser.add_argument('--puerto',type=int,default=0)
    parser.add_argument('--salida',default=str(Path(__file__).parent/'resultados'))
    args=parser.parse_args()
    if args.test:
        result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Verificaciones))
        raise SystemExit(0 if result.wasSuccessful() else 1)
    elif args.batch: print(exportar(args.salida,casos()))
    else: ventana(args.servir,args.puerto)
