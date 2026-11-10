# Simulador de enlaces de telecomunicaciones

Herramienta académica para los enlaces de 10 y 35 km del proyecto multisede. Incluye el simulador original de Richard y los complementos del cierre del informe.

## Autoría

Proyecto académico de Diego Monterroso y Richard Anthony De León. El simulador original de Richard se conserva con ajustes de compatibilidad y complementos del informe. Repositorio de origen: https://github.com/RichardAnthonyDeLeon/simulador-de-enlaces

## Ejecutar la interfaz

Se necesita Python 3.9 o superior y un navegador. No se requieren paquetes externos.

1. Descargar [Proyecto_Final_Repositorio.zip](Proyecto_Final_Repositorio.zip) y extraerlo completo. Este paquete incluye las carpetas de resultados y complementos.
2. En Windows, ejecutar `ABRIR_SIMULADOR.bat`.
3. En otros sistemas, ejecutar `python3 simulador.py`.
4. Elegir el caso, modificar parámetros y pulsar **Calcular**. Para calcular Fm, introducir la sensibilidad del receptor.

Los ocho casos originales se conservan en `resultados/informe.html` (incluido en el ZIP completo). Descargar el repositorio y abrir ese archivo localmente permite consultar la tabla y el gráfico sin ejecutar Python. GitHub muestra el código HTML y no ejecuta la aplicación.

## Instrucciones para la docente

Descargar [Proyecto_Final_Repositorio.zip](Proyecto_Final_Repositorio.zip) desde este repositorio: abrir el archivo y pulsar **Download raw** (descargar archivo original). Extraer la carpeta completa. GitHub permite consultar el código; la interfaz se ejecuta en la computadora.

- **Windows:** con Python 3.9 o superior instalado, abrir `ABRIR_SIMULADOR.bat`. Si Windows pregunta por el origen del archivo, revisar el código antes de permitir su ejecución.
- **macOS o Linux:** abrir Terminal en la carpeta descargada y ejecutar `python3 simulador.py`.
- Mantener la ventana de Terminal abierta mientras se usa la interfaz. Para cerrar el servidor, pulsar **Ctrl+C**.
- Si el navegador no se abre, copiar la dirección local que muestra Terminal.
- Para revisar resultados sin instalar Python, abrir `resultados_finales/informe.html` desde la carpeta extraída. Esto muestra los resultados guardados; no permite recalcular.
- No se requieren paquetes externos, cuenta de GitHub ni conexión a Internet durante los cálculos.

## Casos del cierre del informe

Ejecutar:

```sh
python casos_finales.py
```

Se generan tres casos con sensibilidad de referencia de −79.5 dBm en `resultados_finales/`: 10 km, línea base de 35 km y variante reforzada de 35 km. También se incluyen resultados ya generados.

La variante reforzada usa 6 GHz, 40 MHz, 16-QAM, antenas de 1.80 m y potencia de 28 dBm. Para reproducirla en la interfaz, cargar 35 km e introducir esos diámetros, potencia y sensibilidad. Su Fm calculado es 42.31 dB, frente a 38.49 dB exigidos por el escenario climático del complemento. Los cálculos originales de 1.20 m y 23 dBm permanecen como referencia, no como el caso reforzado.

## Complementos

- `complemento/disponibilidad_academica.py` (incluido en el ZIP completo): escenario de lluvia y multitrayecto, margen requerido y comparación con el margen disponible.
- `complemento/disponibilidad_resultados.json` (incluido en el ZIP completo): entradas y resultados del escenario académico.
- `complemento/verificacion_complementaria.py` (incluido en el ZIP completo): verificaciones numéricas y de reglas lógicas.
- `complemento/topologia.svg` (incluido en el ZIP completo): topología lógica propuesta.
- [`Complemento_Telecomunicaciones.zip`](Complemento_Telecomunicaciones.zip): copia descargable del paquete de pruebas, registros y topología. Desde GitHub, abrir el archivo y usar la descarga del archivo original.

El complemento incluye una copia identificada del motor original (`simulador_revisado.py`) para reproducir sus pruebas. El informe Word/PDF y la coevaluación se entregan por separado en el paquete final para Canvas.

## Reproducir las verificaciones

```sh
python simulador.py --test
python complemento/verificacion_complementaria.py
python complemento/disponibilidad_academica.py --test
python complemento/disponibilidad_academica.py
```

Con `python3` en lugar de `python` cuando lo requiera el sistema. Las suites contienen 10, 12 y 5 pruebas, respectivamente: **27 verificaciones aprobadas** en la revisión de entrega. Los registros se encuentran en `complemento/pruebas_originales.txt`, `complemento/pruebas_complementarias.txt` y `complemento/pruebas_disponibilidad.txt`.

## Alcance de los resultados

La disponibilidad usa datos climáticos y geométricos supuestos, claramente declarados en el programa y el informe. No constituye una validación del terreno ni una garantía de servicio. La variante de 35 km se justifica dentro de ese escenario; la selección final de equipos y emplazamientos requiere datos reales.

Las pruebas de rutas y permisos son modelos locales; no comprueban un firewall, IPS, failover ni tráfico de paquetes en equipos. El modelo distingue la reserva respecto a SNR = 25 dB del margen frente a la sensibilidad del receptor. Nyquist/QAM y Shannon son referencias teóricas y no velocidades útiles garantizadas.

## Fuentes técnicas

- [UIT-R P.530-19](https://www.itu.int/rec/R-REC-P.530/en): propagación de enlaces terrestres.
- [UIT-R P.838-3](https://www.itu.int/rec/R-REC-P.838/en): atenuación específica por lluvia.
- [UIT-R P.841-7](https://www.itu.int/rec/R-REC-P.841/en): conversión de estadísticas anuales y de peor mes.

Las condiciones, hipótesis y selección del receptor de referencia se desarrollan en el informe técnico.
