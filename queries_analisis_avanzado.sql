-- ==============================================================================
-- Consultas SQL Avanzadas para Análisis de Negocios e Inteligencia Comercial
-- Demuestra: Funciones de Ventana, CTEs recursivas/múltiples, RFM y Cohortes
-- Autor: Gustavo Bryan López Cosme | UNI - FIIS
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. TOP 3 PRODUCTOS CON MAYOR RENTABILIDAD POR CATEGORÍA (DENSE_RANK & PARTITION)
-- ------------------------------------------------------------------------------
WITH RentabilidadProductos AS (
    SELECT 
        p.categoria,
        p.nombre AS producto,
        COUNT(f.transaccion_id) AS total_ordenes,
        ROUND(SUM(f.monto_neto), 2) AS facturacion_total,
        ROUND(SUM(f.margen_bruto), 2) AS ganancia_total,
        DENSE_RANK() OVER (
            PARTITION BY p.categoria 
            ORDER BY SUM(f.margen_bruto) DESC
        ) AS ranking_rentabilidad
    FROM fact_ventas f
    JOIN dim_productos p ON f.producto_id = p.producto_id
    GROUP BY p.categoria, p.nombre
)
SELECT 
    categoria,
    ranking_rentabilidad,
    producto,
    facturacion_total,
    ganancia_total
FROM RentabilidadProductos
WHERE ranking_rentabilidad <= 3
ORDER BY categoria, ranking_rentabilidad;


-- ------------------------------------------------------------------------------
-- 2. EVOLUCIÓN MENSUAL, CRECIMIENTO INTERMENSUAL (MoM %) Y TOTAL ACUMULADO (RUNNING TOTAL)
-- ------------------------------------------------------------------------------
WITH VentasMensuales AS (
    SELECT 
        t.anio,
        t.mes,
        t.nombre_mes,
        ROUND(SUM(f.monto_neto), 2) AS venta_mes
    FROM fact_ventas f
    JOIN dim_tiempo t ON f.fecha_id = t.fecha_id
    GROUP BY t.anio, t.mes, t.nombre_mes
),
VentasConLag AS (
    SELECT 
        anio,
        mes,
        nombre_mes,
        venta_mes,
        -- Venta del mes anterior utilizando LAG()
        LAG(venta_mes, 1) OVER (ORDER BY anio, mes) AS venta_mes_anterior,
        -- Venta acumulada a lo largo del año (Running Total)
        SUM(venta_mes) OVER (
            PARTITION BY anio 
            ORDER BY mes 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS venta_acumulada_anual
    FROM VentasMensuales
)
SELECT 
    anio,
    mes,
    nombre_mes,
    venta_mes,
    venta_mes_anterior,
    ROUND(
        ((venta_mes - venta_mes_anterior) * 100.0 / NULLIF(venta_mes_anterior, 0)), 
        2
    ) AS crecimiento_mom_pct,
    venta_acumulada_anual
FROM VentasConLag
ORDER BY anio, mes;


-- ------------------------------------------------------------------------------
-- 3. SEGMENTACIÓN DE CLIENTES RFM (RECENCY, FREQUENCY, MONETARY)
-- ------------------------------------------------------------------------------
WITH MetricasCliente AS (
    SELECT 
        c.cliente_id,
        c.nombre AS cliente,
        c.region,
        -- Recency: Días transcurridos desde su última compra (tomando fecha máx como ref)
        (SELECT MAX(fecha_id) FROM fact_ventas) - MAX(f.fecha_id) AS dias_inactividad,
        -- Frequency: Conteo total de transacciones
        COUNT(DISTINCT f.transaccion_id) AS frecuencia,
        -- Monetary: Gasto total acumulado
        SUM(f.monto_neto) AS valor_monetario
    FROM fact_ventas f
    JOIN dim_clientes c ON f.cliente_id = c.cliente_id
    GROUP BY c.cliente_id, c.nombre, c.region
),
ScoresRFM AS (
    SELECT 
        cliente_id,
        cliente,
        region,
        dias_inactividad,
        frecuencia,
        valor_monetario,
        -- Asignación de cuartiles (1 al 4)
        NTILE(4) OVER (ORDER BY dias_inactividad DESC) AS r_score, -- Más reciente = mayor puntaje
        NTILE(4) OVER (ORDER BY frecuencia ASC) AS f_score,
        NTILE(4) OVER (ORDER BY valor_monetario ASC) AS m_score
    FROM MetricasCliente
)
SELECT 
    cliente_id,
    cliente,
    region,
    frecuencia,
    ROUND(valor_monetario, 2) AS valor_monetario,
    (r_score + f_score + m_score) AS score_rfm_total,
    CASE 
        WHEN (r_score + f_score + m_score) >= 10 THEN 'Cliente VIP / Campeón'
        WHEN (r_score + f_score + m_score) >= 7 THEN 'Cliente Leal / Potencial'
        WHEN r_score <= 2 THEN 'En Riesgo de Abandono'
        ELSE 'Cliente Ocasional'
    END AS segmento_cliente
FROM ScoresRFM
ORDER BY score_rfm_total DESC, valor_monetario DESC;
