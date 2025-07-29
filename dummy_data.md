# Función con Intervalos de Tiempo Personalizables

Aquí tienes una función mejorada que permite especificar el intervalo de tiempo directamente (como '15m', '1h', '6h', etc.) en lugar del número de intervalos por día:

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generar_datos_historicos(dias_desde_inicio=30, intervalo='1h'):
    """
    Genera un DataFrame con datos simulados desde una fecha pasada hasta ahora.
    
    Parámetros:
    - dias_desde_inicio: número de días hacia atrás desde hoy para comenzar (default: 30)
    - intervalo: cadena que especifica el intervalo entre datos (ej: '15m', '30m', '1h', '6h', '12h')
    
    Retorna:
    - DataFrame de pandas con columnas:
      * timestamp (formato MySQL)
      * system (nombre del sistema)
      * provisioned_gb
      * recovered_gb
      * total_capacity
    """
    # Validar y convertir el intervalo a timedelta
    intervalo_timedelta = parse_intervalo(intervalo)
    
    # Nombres de los sistemas
    sistemas = ['Sistema_A', 'Sistema_B', 'Sistema_C', 'Sistema_D']
    
    # Capacidades base para cada sistema (GB)
    capacidades_base = {
        'Sistema_A': 10000,
        'Sistema_B': 15000,
        'Sistema_C': 8000,
        'Sistema_D': 12000
    }
    
    # Tendencias de crecimiento para cada sistema (por día)
    tendencias = {
        'Sistema_A': 1.002,  # 0.2% de crecimiento diario
        'Sistema_B': 1.003,
        'Sistema_C': 1.001,
        'Sistema_D': 1.0025
    }
    
    # Lista para almacenar todos los datos
    datos = []
    
    # Fecha final (ahora)
    fecha_final = datetime.now()
    
    # Fecha inicial (dias_desde_inicio atrás desde hoy a medianoche)
    fecha_inicial = (fecha_final - timedelta(days=dias_desde_inicio)).replace(
        hour=0, minute=0, second=0, microsecond=0)
    
    # Generar datos para cada intervalo
    timestamp_actual = fecha_inicial
    while timestamp_actual <= fecha_final:
        # Formatear timestamp como string MySQL
        timestamp_str = timestamp_actual.strftime('%Y-%m-%d %H:%M:%S')
        
        # Días transcurridos desde el inicio (para tendencia)
        dias_transcurridos = (timestamp_actual - fecha_inicial).total_seconds() / (24 * 3600)
        
        # Generar datos para cada sistema
        for sistema in sistemas:
            # Calcular capacidad base con tendencia de crecimiento
            base = capacidades_base[sistema] * (tendencias[sistema] ** dias_transcurridos)
            
            # Variación diurna/nocturna (simula patrones de uso)
            hora_del_dia = timestamp_actual.hour + timestamp_actual.minute/60
            factor_diurno = 0.7 + 0.5 * (np.sin((hora_del_dia/24) * 2 * np.pi - np.pi/2) + 1) / 2
            
            # Variación semanal (menos uso los fines de semana)
            dia_semana = timestamp_actual.weekday()  # 0=Lunes, 6=Domingo
            factor_semanal = 0.8 if dia_semana >= 5 else 1.0  # 20% menos los fines de semana
            
            # Generar valores con cierta variabilidad
            provisioned = base * (0.6 + 0.3 * np.random.random()) * factor_diurno * factor_semanal
            recovered = provisioned * (0.7 + 0.2 * np.random.random())
            total_capacity = base * (0.95 + 0.1 * np.random.random())
            
            # Asegurar relaciones lógicas
            recovered = min(recovered, provisioned)
            provisioned = min(provisioned, total_capacity)
            
            # Redondear valores
            provisioned = round(provisioned, 2)
            recovered = round(recovered, 2)
            total_capacity = round(total_capacity, 2)
            
            # Añadir registro
            datos.append({
                'timestamp': timestamp_str,
                'system': sistema,
                'provisioned_gb': provisioned,
                'recovered_gb': recovered,
                'total_capacity': total_capacity
            })
        
        # Avanzar al siguiente intervalo
        timestamp_actual += intervalo_timedelta
    
    # Crear DataFrame
    df = pd.DataFrame(datos)
    
    return df

def parse_intervalo(intervalo_str):
    """Convierte una cadena de intervalo (ej: '15m', '2h') a timedelta"""
    try:
        if 'm' in intervalo_str:
            minutos = int(intervalo_str.replace('m', ''))
            return timedelta(minutes=minutos)
        elif 'h' in intervalo_str:
            horas = int(intervalo_str.replace('h', ''))
            return timedelta(hours=horas)
        elif 'd' in intervalo_str:
            dias = int(intervalo_str.replace('d', ''))
            return timedelta(days=dias)
        else:
            # Por defecto asumimos horas si no se especifica unidad
            return timedelta(hours=int(intervalo_str))
    except ValueError:
        raise ValueError(f"Formato de intervalo no válido: {intervalo_str}. Use formatos como '15m', '2h', '1d'")

# Ejemplo de uso:
if __name__ == "__main__":
    # Ejemplos de diferentes intervalos
    intervalos_ejemplo = ['15m', '30m', '1h', '6h', '12h']
    
    for intervalo in intervalos_ejemplo:
        print(f"\nGenerando datos con intervalo de {intervalo}...")
        datos = generar_datos_historicos(dias_desde_inicio=7, intervalo=intervalo)
        
        print(f"Total de registros: {len(datos)}")
        print(f"Primer timestamp: {datos['timestamp'].min()}")
        print(f"Último timestamp: {datos['timestamp'].max()}")
        print(f"Muestra de datos:\n{datos.head()}")
```

## Características principales:

1. **Intervalos personalizables**:
   - Ahora puedes especificar el intervalo directamente como cadena ('15m', '1h', '6h', etc.)
   - La función soporta minutos ('m'), horas ('h') y días ('d')

2. **Generación flexible**:
   - Los datos se generan exactamente desde `dias_desde_inicio` días atrás hasta ahora
   - El intervalo entre puntos de datos es exactamente el especificado

3. **Métodos de uso**:
   ```python
   # Datos cada 15 minutos de los últimos 3 días
   datos = generar_datos_historicos(dias_desde_inicio=3, intervalo='15m')
   
   # Datos horarios de los últimos 30 días
   datos = generar_datos_historicos(dias_desde_inicio=30, intervalo='1h')
   
   # Datos cada 6 horas de los últimos 7 días
   datos = generar_datos_historicos(dias_desde_inicio=7, intervalo='6h')
   ```

4. **Validación de intervalos**:
   - La función incluye un validador que convierte cadenas como '15m' a objetos timedelta
   - Soporta múltiples formatos de intervalo

5. **Generación eficiente**:
   - Usa un bucle while para generar exactamente los intervalos necesarios
   - Mantiene todas las características de generación de datos realistas de la versión anterior

Esta implementación es más intuitiva ya que puedes especificar directamente el intervalo que necesitas en formato de cadena, similar a cómo se especifican los intervalos en muchas herramientas de bases de datos y visualización.
