import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import psycopg2
import os

st.set_page_config(page_title="Control Financiero V8 PRO", layout="centered")

# =============================
# CONFIGURACIÓN COMPLETA
# =============================
PRESUPUESTO_TOTAL = 13100

# Subcategorías por rubro
SUBCATEGORIAS = {
    "Alimentación": ["Despensa", "Comida fuera", "Antojos", "Bebidas"],
    "Servicios": ["Luz", "Agua", "Gas", "Internet", "Teléfono"],
    "Vivienda": ["Renta", "Mantenimiento", "Artículos hogar", "Limpiadores"],
    "Transporte": ["Gasolina", "Mantenimiento auto", "Pasajes", "Estacionamiento"],
    "Ahorro": ["Ahorro mensual", "Fondo emergencia", "Inversiones"]
}

PRESUPUESTO = {
    "Alimentación": 7900,
    "Servicios": 1550,
    "Vivienda": 1400,
    "Transporte": 750,
    "Ahorro": 1500
}

PASSWORD = "1234"

def get_connection():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        database_url = "postgresql://postgres:postgres@localhost:5432/gastos"
    return psycopg2.connect(database_url)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS gastos (
            id SERIAL PRIMARY KEY,
            fecha DATE,
            rubro TEXT,
            subcategoria TEXT,
            monto REAL
        )
    ''')
    conn.commit()
    conn.close()

def cargar():
    init_db()
    conn = get_connection()
    df = pd.read_sql_query("SELECT fecha, rubro, subcategoria, monto FROM gastos ORDER BY fecha DESC", conn)
    conn.close()
    if not df.empty:
        df["fecha"] = pd.to_datetime(df["fecha"])
    return df

def guardar(fecha, rubro, subcategoria, monto):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO gastos (fecha, rubro, subcategoria, monto) VALUES (%s, %s, %s, %s)", 
              (fecha, rubro, subcategoria, monto))
    conn.commit()
    conn.close()

def eliminar_ultimo():
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM gastos WHERE id = (SELECT MAX(id) FROM gastos)")
    conn.commit()
    conn.close()

# =============================
# LOGIN
# =============================
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acceso")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if pwd == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta")
    st.stop()

# =============================
# DATA
# =============================
df = cargar()

st.title("💰 Control Financiero V8 PRO")
st.caption("Datos en la nube | Subcategorías | Alertas inteligentes")

# =============================
# KPIs
# =============================
if not df.empty:
    total = df["monto"].sum()
    dias = datetime.now().day
    proyeccion = (total / dias) * 30 if dias > 0 else 0
    restante = PRESUPUESTO_TOTAL - total

    col1, col2, col3 = st.columns(3)
    col1.metric("💸 Gastado", f"${total:,.0f}")
    col2.metric("📈 Proyección", f"${proyeccion:,.0f}")
    col3.metric("💰 Disponible", f"${restante:,.0f}")

st.divider()

# =============================
# REGISTRAR GASTO CON SUBCATEGORÍAS
# =============================
st.subheader("➕ Registrar gasto")

fecha = st.date_input("Fecha", datetime.now())
rubro = st.selectbox("Categoría", list(PRESUPUESTO.keys()))

# Mostrar subcategorías según rubro seleccionado
subcategoria_opciones = SUBCATEGORIAS[rubro]
subcategoria = st.selectbox("Subcategoría", subcategoria_opciones)

monto = st.number_input("Monto ($)", step=10.0, min_value=0.0)

col1, col2 = st.columns(2)
with col1:
    if st.button("💾 Guardar", use_container_width=True):
        if monto > 0:
            guardar(fecha.strftime("%Y-%m-%d"), rubro, subcategoria, monto)
            st.success(f"✅ Gasto guardado: {rubro} → {subcategoria}")
            st.rerun()
        else:
            st.warning("⚠️ Ingresa un monto válido")

with col2:
    if st.button("🗑️ Eliminar último", use_container_width=True):
        eliminar_ultimo()
        st.warning("Último gasto eliminado")
        st.rerun()

st.divider()

# =============================
# ANÁLISIS Y ALARMAS
# =============================
if not df.empty:
    # Resumen por rubro
    resumen = df.groupby("rubro")["monto"].sum().reset_index()
    resumen["presupuesto"] = resumen["rubro"].map(PRESUPUESTO)
    resumen["uso %"] = (resumen["monto"] / resumen["presupuesto"] * 100).fillna(0)

    # ALARMAS INTELIGENTES
    st.subheader("🚨 Alertas y diagnóstico")
    
    top = resumen.sort_values(by="uso %", ascending=False).iloc[0]
    
    if top["uso %"] > 100:
        st.error(f"⚠️ EXCESO en {top['rubro']} - Has superado el presupuesto en {top['uso %']:.0f}%")
    elif top["uso %"] > 80:
        st.warning(f"📌 ALERTA en {top['rubro']} - Has usado {top['uso %']:.0f}% de tu presupuesto")
    else:
        st.success("✅ Todo en orden. Buen control de gastos")
    
    # Mostrar todas las categorías con su estado
    st.subheader("📊 Estado por categoría")
    for _, row in resumen.iterrows():
        if row["uso %"] > 100:
            st.error(f"**{row['rubro']}**: ${row['monto']:,.0f} / ${row['presupuesto']:,.0f} ({row['uso %']:.0f}%) 🔴 Excedido")
        elif row["uso %"] > 80:
            st.warning(f"**{row['rubro']}**: ${row['monto']:,.0f} / ${row['presupuesto']:,.0f} ({row['uso %']:.0f}%) 🟡 Cerca del límite")
        else:
            st.success(f"**{row['rubro']}**: ${row['monto']:,.0f} / ${row['presupuesto']:,.0f} ({row['uso %']:.0f}%) 🟢 Bien")

    # Gráfica
    fig = px.pie(resumen, names="rubro", values="monto", title="Distribución de gastos por categoría")
    st.plotly_chart(fig, use_container_width=True)
    
    # Resumen por subcategoría
    st.subheader("📋 Detalle por subcategoría")
    detalle_sub = df.groupby(["rubro", "subcategoria"])["monto"].sum().reset_index()
    st.dataframe(detalle_sub, use_container_width=True)

    # Historial completo
    st.subheader("📋 Historial de movimientos")
    st.dataframe(df.sort_values(by="fecha", ascending=False), use_container_width=True)

    # Botón de respaldo
    if st.button("📁 Descargar respaldo (CSV)"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="✅ Haz clic para descargar",
            data=csv,
            file_name=f"gastos_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
else:
    st.info("No hay gastos registrados aún. Agrega tu primer gasto arriba.")

st.divider()
st.caption("V8 PRO | Subcategorías | Alertas inteligentes | Datos en la nube")
