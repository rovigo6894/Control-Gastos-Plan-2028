import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import psycopg2
import os

st.set_page_config(page_title="Control Financiero PRO", layout="centered")

PASSWORD = "1234"

PRESUPUESTOS_POR_DEFECTO = {
    "Alimentación": 7900,
    "Servicios": 1550,
    "Vivienda": 1400,
    "Transporte": 750,
    "Ahorro": 1500
}

SUBCATEGORIAS = {
    "Alimentación": ["Despensa", "Comida fuera", "Antojos", "Bebidas", "Café"],
    "Servicios": ["Luz", "Agua", "Gas", "Internet", "Teléfono", "Netflix/Spotify"],
    "Vivienda": ["Renta", "Mantenimiento", "Artículos hogar", "Limpiadores", "Muebles"],
    "Transporte": ["Gasolina", "Mantenimiento auto", "Pasajes", "Estacionamiento", "Taxi/Uber"],
    "Ahorro": ["Ahorro mensual", "Fondo emergencia", "Inversiones", "Meta específica"]
}

def get_connection():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        database_url = "postgresql://postgres:postgres@localhost:5432/gastos"
    return psycopg2.connect(database_url)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Verificar si la columna subcategoria existe
    c.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='gastos' AND column_name='subcategoria'
    """)
    columna_existe = c.fetchone()
    
    if not columna_existe:
        # Si no existe, recrear la tabla correctamente
        c.execute("DROP TABLE IF EXISTS gastos CASCADE")
        c.execute("DROP TABLE IF EXISTS presupuestos CASCADE")
        c.execute('''
            CREATE TABLE gastos (
                id SERIAL PRIMARY KEY,
                fecha DATE,
                rubro TEXT,
                subcategoria TEXT,
                monto REAL
            )
        ''')
        c.execute('''
            CREATE TABLE presupuestos (
                rubro TEXT PRIMARY KEY,
                monto REAL
            )
        ''')
        # Insertar presupuestos por defecto
        for rubro, monto in PRESUPUESTOS_POR_DEFECTO.items():
            c.execute("INSERT INTO presupuestos (rubro, monto) VALUES (%s, %s)", (rubro, monto))
    
    conn.commit()
    conn.close()

def cargar_gastos():
    init_db()
    conn = get_connection()
    df = pd.read_sql_query("SELECT fecha, rubro, subcategoria, monto FROM gastos ORDER BY fecha DESC", conn)
    conn.close()
    if not df.empty:
        df["fecha"] = pd.to_datetime(df["fecha"])
    return df

def cargar_presupuestos():
    conn = get_connection()
    df = pd.read_sql_query("SELECT rubro, monto FROM presupuestos", conn)
    conn.close()
    if df.empty:
        return PRESUPUESTOS_POR_DEFECTO
    else:
        return dict(zip(df["rubro"], df["monto"]))

def guardar_presupuesto(rubro, monto):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO presupuestos (rubro, monto) VALUES (%s, %s) ON CONFLICT (rubro) DO UPDATE SET monto = EXCLUDED.monto", 
              (rubro, monto))
    conn.commit()
    conn.close()

def guardar_gasto(fecha, rubro, subcategoria, monto):
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

df = cargar_gastos()
presupuestos = cargar_presupuestos()
total_presupuesto = sum(presupuestos.values())

st.title("💰 Control Financiero PRO")
st.caption("Subcategorías | Presupuestos editables | Alertas inteligentes")

if not df.empty:
    total = df["monto"].sum()
    dias = datetime.now().day
    proyeccion = (total / dias) * 30 if dias > 0 else 0
    restante = total_presupuesto - total

    col1, col2, col3 = st.columns(3)
    col1.metric("💸 Gastado", f"${total:,.0f}")
    col2.metric("📈 Proyección", f"${proyeccion:,.0f}")
    col3.metric("💰 Presupuesto restante", f"${restante:,.0f}")

st.divider()

with st.expander("✏️ Editar presupuestos mensuales", expanded=False):
    st.subheader("Ajusta tus presupuestos por categoría")
    nuevos_presupuestos = {}
    cols = st.columns(2)
    for i, (rubro, monto_actual) in enumerate(presupuestos.items()):
        with cols[i % 2]:
            nuevo = st.number_input(f"{rubro}", value=float(monto_actual), step=100.0, key=f"pres_{rubro}")
            nuevos_presupuestos[rubro] = nuevo
    if st.button("💾 Guardar presupuestos", use_container_width=True):
        for rubro, monto in nuevos_presupuestos.items():
            guardar_presupuesto(rubro, monto)
        st.success("✅ Presupuestos actualizados")
        st.rerun()

st.divider()

st.subheader("➕ Registrar gasto")

fecha = st.date_input("Fecha", datetime.now())
rubro = st.selectbox("Categoría", list(presupuestos.keys()))

subcategoria_opciones = SUBCATEGORIAS[rubro]
subcategoria = st.selectbox("Subcategoría", subcategoria_opciones)

monto = st.number_input("Monto ($)", step=10.0, min_value=0.0)

col1, col2 = st.columns(2)
with col1:
    if st.button("💾 Guardar", use_container_width=True):
        if monto > 0:
            guardar_gasto(fecha.strftime("%Y-%m-%d"), rubro, subcategoria, monto)
            st.success(f"✅ Guardado: {rubro} → {subcategoria} | ${monto:,.0f}")
            st.rerun()
        else:
            st.warning("⚠️ Ingresa un monto válido")

with col2:
    if st.button("🗑️ Eliminar último", use_container_width=True):
        eliminar_ultimo()
        st.warning("Último gasto eliminado")
        st.rerun()

st.divider()

if not df.empty:
    resumen = df.groupby("rubro")["monto"].sum().reset_index()
    resumen["presupuesto"] = resumen["rubro"].map(presupuestos)
    resumen["uso %"] = (resumen["monto"] / resumen["presupuesto"] * 100).fillna(0)

    st.subheader("🚨 Alertas y diagnóstico")
    
    top = resumen.sort_values(by="uso %", ascending=False).iloc[0]
    
    if top["uso %"] > 100:
        st.error(f"⚠️ EXCESO en {top['rubro']} - Has superado el presupuesto en {top['uso %']:.0f}%")
    elif top["uso %"] > 80:
        st.warning(f"📌 ALERTA en {top['rubro']} - Has usado {top['uso %']:.0f}% de tu presupuesto")
    else:
        st.success("✅ Todo en orden. Buen control de gastos")
    
    st.subheader("📊 Estado por categoría")
    for _, row in resumen.iterrows():
        porcentaje = row["uso %"]
        if porcentaje > 100:
            st.error(f"**{row['rubro']}**: ${row['monto']:,.0f} / ${row['presupuesto']:,.0f} ({porcentaje:.0f}%) 🔴 EXCEDIDO")
        elif porcentaje > 80:
            st.warning(f"**{row['rubro']}**: ${row['monto']:,.0f} / ${row['presupuesto']:,.0f} ({porcentaje:.0f}%) 🟡 CUIDADO")
        else:
            st.success(f"**{row['rubro']}**: ${row['monto']:,.0f} / ${row['presupuesto']:,.0f} ({porcentaje:.0f}%) 🟢 OK")

    fig = px.pie(resumen, names="rubro", values="monto", title="Distribución de gastos por categoría")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📋 Detalle por subcategoría")
    detalle_sub = df.groupby(["rubro", "subcategoria"])["monto"].sum().reset_index()
    detalle_sub = detalle_sub.sort_values("monto", ascending=False)
    st.dataframe(detalle_sub, use_container_width=True)

    st.subheader("📋 Historial de movimientos")
    st.dataframe(df.sort_values(by="fecha", ascending=False), use_container_width=True)

    if st.button("📁 Descargar respaldo (CSV)"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="✅ Haz clic para descargar",
            data=csv,
            file_name=f"gastos_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
else:
    st.info("📝 No hay gastos registrados aún. Agrega tu primer gasto arriba.")

st.divider()
st.caption("💰 Control Financiero PRO | Subcategorías | Presupuestos editables | Alertas en tiempo real")
