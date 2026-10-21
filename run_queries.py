# ==============================================================================
# Ejecutor de Consultas SQL Analíticas en Terminal
# Autor: Gustavo Bryan López Cosme | UNI - FIIS
# ==============================================================================

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "ventas_analytics.db")
SQL_FILE = os.path.join(os.path.dirname(__file__), "queries_analisis_avanzado.sql")

def run():
    if not os.path.exists(DB_PATH):
        print("[ERROR] No se encontro ventas_analytics.db. Ejecuta primero 'python etl_pipeline.py'.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    with open(SQL_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Separar consultas por punto y coma
    queries = [q.strip() for q in content.split(";") if q.strip()]

    titles = [
        "1. TOP 3 PRODUCTOS MAS RENTABLES POR CATEGORIA (DENSE_RANK)",
        "2. EVOLUCION MENSUAL, CRECIMIENTO MoM % Y TOTAL ACUMULADO (LAG & RUNNING TOTAL)",
        "3. SEGMENTACION DE CLIENTES RFM (RECENCY, FREQUENCY, MONETARY - NTILE(4))"
    ]

    for i, query in enumerate(queries):
        title = titles[i] if i < len(titles) else f"CONSULTA #{i+1}"
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80)
        
        try:
            cur.execute(query)
            col_names = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

            # Mostrar encabezados
            header_line = " | ".join(f"{col:<20}" for col in col_names)
            print(header_line)
            print("-" * len(header_line))

            # Mostrar primeras filas (máximo 10 para visualización limpia)
            for row in rows[:10]:
                formatted_row = " | ".join(f"{str(val):<20}" for val in row)
                print(formatted_row)

            if len(rows) > 10:
                print(f"... y {len(rows) - 10} filas adicionales.")
        except Exception as err:
            print(f"[ERROR]: {err}")

    conn.close()
    print("\n[OK] Consultas analiticas ejecutadas con exito.")

if __name__ == "__main__":
    run()
