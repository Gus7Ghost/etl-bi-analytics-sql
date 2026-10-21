# ==============================================================================
# Pipeline ETL de Datos de Operaciones y Modelado Dimensional (Star Schema)
# Autor: Gustavo Bryan López Cosme | UNI - FIIS
# Compatible con Python Standard Library (sqlite3) y Pandas
# ==============================================================================

import sqlite3
import random
from datetime import datetime, timedelta

def run_etl():
    print("[ETL] 1. Inicializando base de datos SQLite...")
    conn = sqlite3.connect("ventas_analytics.db")
    cursor = conn.cursor()

    # Creación de tablas del esquema en estrella (Star Schema)
    cursor.execute("DROP TABLE IF EXISTS fact_ventas;")
    cursor.execute("DROP TABLE IF EXISTS dim_clientes;")
    cursor.execute("DROP TABLE IF EXISTS dim_productos;")
    cursor.execute("DROP TABLE IF EXISTS dim_tiempo;")

    cursor.execute("""
    CREATE TABLE dim_clientes (
        cliente_id INTEGER PRIMARY KEY,
        nombre TEXT,
        region TEXT,
        tipo_cliente TEXT,
        fecha_registro TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE dim_productos (
        producto_id INTEGER PRIMARY KEY,
        nombre TEXT,
        categoria TEXT,
        precio_unitario REAL,
        costo_unitario REAL
    );
    """)

    cursor.execute("""
    CREATE TABLE dim_tiempo (
        fecha_id INTEGER PRIMARY KEY,
        fecha TEXT,
        anio INTEGER,
        trimestre INTEGER,
        mes INTEGER,
        nombre_mes TEXT,
        dia INTEGER,
        dia_semana TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE fact_ventas (
        transaccion_id INTEGER PRIMARY KEY,
        fecha_id INTEGER,
        cliente_id INTEGER,
        producto_id INTEGER,
        cantidad INTEGER,
        descuento REAL,
        monto_bruto REAL,
        monto_neto REAL,
        costo_total REAL,
        margen_bruto REAL,
        FOREIGN KEY (fecha_id) REFERENCES dim_tiempo(fecha_id),
        FOREIGN KEY (cliente_id) REFERENCES dim_clientes(cliente_id),
        FOREIGN KEY (producto_id) REFERENCES dim_productos(producto_id)
    );
    """)

    print("[ETL] 2. Poblando Dimensión Productos...")
    products = [
        (101, "Cámara Industrial OpenCV", "Sistemas IA", 280.0, 160.0),
        (102, "Módulo UAV Telemetría MAVLink", "Sistemas IA", 450.0, 270.0),
        (103, "Servidor Edge Inferencia", "Servicios Cloud", 1200.0, 750.0),
        (104, "Licencia Power BI Pro Empresarial", "Software", 120.0, 80.0),
        (105, "Sensor Biométrico IR", "Sistemas IA", 190.0, 95.0),
        (106, "Router Industrial 5G", "Electrónica", 340.0, 210.0),
        (107, "Suscripción Base de Datos Cloud", "Servicios Cloud", 600.0, 350.0)
    ]
    cursor.executemany("INSERT INTO dim_productos VALUES (?, ?, ?, ?, ?);", products)

    print("[ETL] 3. Poblando Dimensión Clientes...")
    regions = ['Lima Metropolitana', 'Arequipa', 'Trujillo', 'Cusco', 'Piura']
    customer_types = ['Corporativo', 'Pyme', 'Sector Público', 'Educación']
    random.seed(42)

    customers = []
    for c_id in range(1, 51):
        reg_date = (datetime(2025, 1, 1) + timedelta(days=random.randint(0, 300))).strftime('%Y-%m-%d')
        customers.append((
            c_id,
            f"Empresa / Cliente {c_id:03d}",
            random.choice(regions),
            random.choice(customer_types),
            reg_date
        ))
    cursor.executemany("INSERT INTO dim_clientes VALUES (?, ?, ?, ?, ?);", customers)

    print("[ETL] 4. Poblando Dimensión Tiempo (Calendario 2025-2026)...")
    curr_date = datetime(2025, 1, 1)
    end_date = datetime(2026, 6, 30)
    time_rows = []
    meses_es = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    dias_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    while curr_date <= end_date:
        fecha_id = int(curr_date.strftime('%Y%m%d'))
        trimestre = (curr_date.month - 1) // 3 + 1
        time_rows.append((
            fecha_id,
            curr_date.strftime('%Y-%m-%d'),
            curr_date.year,
            trimestre,
            curr_date.month,
            meses_es[curr_date.month],
            curr_date.day,
            dias_es[curr_date.weekday()]
        ))
        curr_date += timedelta(days=1)
    cursor.executemany("INSERT INTO dim_tiempo VALUES (?, ?, ?, ?, ?, ?, ?, ?);", time_rows)

    print("[ETL] 5. Generando Hechos de Ventas (1000 transacciones)...")
    transactions = []
    base_date = datetime(2025, 2, 1)
    for t_id in range(1001, 2001):
        t_date = base_date + timedelta(days=random.randint(0, 380))
        t_fecha_id = int(t_date.strftime('%Y%m%d'))
        c_id = random.randint(1, 50)
        prod = random.choice(products)
        p_id = prod[0]
        p_price = prod[3]
        p_cost = prod[4]
        
        qty = random.randint(1, 10)
        discount = random.choice([0.0, 0.05, 0.10, 0.15])
        monto_bruto = round(qty * p_price, 2)
        monto_neto = round(monto_bruto * (1.0 - discount), 2)
        costo_total = round(qty * p_cost, 2)
        margen = round(monto_neto - costo_total, 2)

        transactions.append((
            t_id, t_fecha_id, c_id, p_id, qty, discount,
            monto_bruto, monto_neto, costo_total, margen
        ))

    cursor.executemany("INSERT INTO fact_ventas VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", transactions)

    conn.commit()
    conn.close()
    print("[ETL] [OK] Proceso finalizado. Base de datos 'ventas_analytics.db' generada con exito.")

if __name__ == "__main__":
    run_etl()
