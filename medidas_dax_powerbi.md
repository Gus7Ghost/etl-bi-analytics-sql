# Fórmulas y Medidas DAX para Power BI

Este archivo contiene las medidas en lenguaje **DAX (Data Analysis Expressions)** creadas para el modelo de datos tabular con esquema en estrella (`fact_ventas`, `dim_clientes`, `dim_productos`, `dim_tiempo`).

---

### 1. Métricas Base de Facturación y Margen
```dax
Ventas Totales = SUM(fact_ventas[monto_neto])
```

```dax
Costo Total = SUM(fact_ventas[costo_total])
```

```dax
Margen Bruto = [Ventas Totales] - [Costo Total]
```

```dax
% Margen Bruto = DIVIDE([Margen Bruto], [Ventas Totales], 0)
```

```dax
Ticket Promedio = DIVIDE([Ventas Totales], DISTINCTCOUNT(fact_ventas[transaccion_id]), 0)
```

---

### 2. Inteligencia de Tiempo (Time Intelligence)
```dax
-- Ventas del Mismo Periodo Año Anterior (SPLY)
Ventas SPLY = 
CALCULATE(
    [Ventas Totales],
    SAMEPERIODLASTYEAR(dim_tiempo[fecha])
)
```

```dax
-- Crecimiento Interanual (YoY %)
Crecimiento YoY % = 
DIVIDE([Ventas Totales] - [Ventas SPLY], [Ventas SPLY], 0)
```

```dax
-- Media Móvil a 3 Meses (Rolling 3 Months)
Media Movil 3 Meses = 
AVERAGEX(
    DATESINPERIOD(dim_tiempo[fecha], LASTDATE(dim_tiempo[fecha]), -3, MONTH),
    [Ventas Totales]
)
```

---

### 3. Métricas de Clientes y Retención
```dax
Clientes Activos = DISTINCTCOUNT(fact_ventas[cliente_id])
```

```dax
-- Venta Promedio por Cliente
Gasto Promedio por Cliente = DIVIDE([Ventas Totales], [Clientes Activos], 0)
```
