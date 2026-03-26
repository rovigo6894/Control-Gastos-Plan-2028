import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import psycopg2
import os

st.set_page_config(page_title="Control Financiero PRO", layout="wide", page_icon="💰")

# =============================
# CONFIGURACIÓN
# =============================
PASSWORD = "1234"

# Presupuestos por categoría
PRESUPUESTOS_POR_DEFECTO = {
    "Alimentación": 7900,
    "Servicios": 1550,
    "Vivienda": 1400,
    "Transporte": 750,
    "Ahorro": 1500,
    "Salud": 800,
    "Educación": 600,
    "Entretenimiento": 500
}

# Subcategorías ampliadas
SUBCATEGORIAS = {
    "Alimentación": ["Despensa", "Comida fuera", "Antojos", "Bebidas", "Café", "Panadería", "Carnes", "Verduras", "Fruta", "Botanas"],
    "Servicios": ["Luz", "Agua", "Gas", "Internet", "Teléfono", "Netflix", "Spotify", "Prime Video", "Mantenimiento", "Basura"],
    "Vivienda": ["Renta", "Hipoteca", "Mantenimiento", "Artículos hogar", "Limpiadores", "Muebles", "Electrodomésticos", "Decoración", "Jardinería", "Herramientas"],
    "Transporte": ["Gasolina", "Mantenimiento auto", "Pasajes", "Estacionamiento", "Taxi", "Uber", "Didi", "Renta de auto", "Lavado auto", "Tenencia"],
    "Ahorro": ["Ahorro mensual", "Fondo emergencia", "Inversiones", "Meta viajes", "Meta retiro", "Educación hijos", "Navidad", "Casa propia"],
    "Salud": ["Farmacia", "Consultas", "Dentista", "Terapias", "Medicamentos", "Seguro médico", "Gimnasio", "Nutrición", "Estudios", "Urgencias"],
    "Educación": ["Colegiaturas", "Libros", "Material escolar", "Cursos", "Talleres", "Idiomas", "Computadora", "Software", "Uniformes", "Transporte escolar"],
    "Entretenimiento": ["Cine", "Conciertos", "Restaurantes", "Bares", "Hobbies", "Deportes", "Videojuegos", "Suscripciones", "Viajes", "Parques"]
}

def get_connection():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        database_url = "postgresql://postgres:postgres@localhost:5432/gastos"
    return psycopg2.connect(database_url)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
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

# =============================
# LOGIN
# =============================
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Control Financiero PRO")
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
df = cargar_gastos()
presupuestos = cargar_presupuestos()
total_presupuesto = sum(presupuestos.values())

# =============================
# HEADER CON MÉTRICAS
# =============================
st.title("💰 Control Financiero PRO")
st.markdown("### Sistema inteligente de gestión de gastos")

if not df.empty:
    total = df["monto"].sum()
    dias = datetime.now().day
    proyeccion = (total / dias) * 30 if dias > 0 else 0
    restante = total_presupuesto - total
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💸 Gastado", f"${total:,.0f}")
    with col2:
        st.metric("📈 Proyección", f"${proyeccion:,.0f}")
    with col3:
        st.metric("💰 Restante", f"${restante:,.0f}")
    with col4:
        porcentaje_uso = (total / total_presupuesto * 100) if total_presupuesto > 0 else 0
        st.metric("📊 Uso", f"{porcentaje_uso:.1f}%")

st.divider()

# =============================
# TABS
# =============================
tab1, tab2, tab3, tab4 = st.tabs(["📝 Registrar", "✏️ Presupuestos", "📊 Análisis", "📋 Historial"])

with tab1:
    st.subheader("➕ Nuevo gasto")
    
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Fecha", datetime.now())
        rubro = st.selectbox("Categoría", list(presupuestos.keys()))
        subcategoria_opciones = SUBCATEGORIAS[rubro]
        subcategoria = st.selectbox("Subcategoría", subcategoria_opciones)
    with col2:
        monto = st.number_input("Monto ($)", step=10.0, min_value=0.0, format="%.2f")
        st.markdown("---")
        descripcion = st.text_area("Descripción (opcional)", placeholder="Ej: Supermercado", height=68)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Guardar", use_container_width=True, type="primary"):
            if monto > 0:
                guardar_gasto(fecha.strftime("%Y-%m-%d"), rubro, subcategoria, monto)
                st.success(f"✅ Guardado: {rubro} → {subcategoria} | ${monto:,.2f}")
                st.rerun()
            else:
                st.warning("Ingresa un monto válido")
    with col2:
        if st.button("🗑️ Eliminar último", use_container_width=True):
            eliminar_ultimo()
            st.warning("Último gasto eliminado")
            st.rerun()

with tab2:
    st.subheader("✏️ Ajustar presupuestos")
    nuevos_presupuestos = {}
    cols = st.columns(3)
    for i, (rubro, monto_actual) in enumerate(presupuestos.items()):
        with cols[i % 3]:
            nuevo = st.number_input(f"{rubro}", value=float(monto_actual), step=100.0, key=f"pres_{rubro}", format="%.0f")
            nuevos_presupuestos[rubro] = nuevo
    
    if st.button("💾 Guardar presupuestos", use_container_width=True, type="primary"):
        for rubro, monto in nuevos_presupuestos.items():
            guardar_presupuesto(rubro, monto)
        st.success("Presupuestos actualizados")
        st.rerun()

with tab3:
    if not df.empty:
        resumen = df.groupby("rubro")["monto"].sum().reset_index()
        resumen["presupuesto"] = resumen["rubro"].map(presupuestos)
        resumen["uso %"] = (resumen["monto"] / resumen["presupuesto"] * 100).fillna(0)
        
        st.subheader("🚨 Alertas")
        top = resumen.sort_values(by="uso %", ascending=False).iloc[0]
        if top["uso %"] > 100:
            st.error(f"⚠️ EXCESO en {top['rubro']} - {top['uso %']:.0f}%")
        elif top["uso %"] > 80:
            st.warning(f"📌 ALERTA en {top['rubro']} - {top['uso %']:.0f}%")
        else:
            st.success("✅ Buen control")
        
        col1, col2 = st.columns(2)
        with col1:
            fig_pie = px.pie(resumen, names="rubro", values="monto", title="Distribución")
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            gastos_por_dia = df.groupby(df["fecha"])["monto"].sum().reset_index()
            fig_line = px.line(gastos_por_dia, x="fecha", y="monto", title="Evolución diaria")
            st.plotly_chart(fig_line, use_container_width=True)
        
        st.subheader("Estado por categoría")
        for _, row in resumen.iterrows():
            if row["uso %"] > 100:
                st.error(f"**{row['rubro']}**: ${row['monto']:,.0f} / ${row['presupuesto']:,.0f} ({row['uso %']:.0f}%) 🔴")
            elif row["uso %"] > 80:
                st.warning(f"**{row['rubro']}**: ${row['monto']:,.0f} / ${row['presupuesto']:,.0f} ({row['uso %']:.0f}%) 🟡")
            else:
                st.success(f"**{row['rubro']}**: ${row['monto']:,.0f} / ${row['presupuesto']:,.0f} ({row['uso %']:.0f}%) 🟢")
        
        st.subheader("Detalle por subcategoría")
        detalle_sub = df.groupby(["rubro", "subcategoria"])["monto"].sum().reset_index()
        detalle_sub = detalle_sub.sort_values("monto", ascending=False)
        st.dataframe(detalle_sub, use_container_width=True)
    else:
        st.info("No hay gastos registrados")

with tab4:
    if not df.empty:
        st.subheader("Historial")
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.date_input("Desde", df["fecha"].min())
        with col2:
            fecha_fin = st.date_input("Hasta", df["fecha"].max())
        
        df_filtrado = df[(df["fecha"] >= pd.to_datetime(fecha_inicio)) & (df["fecha"] <= pd.to_datetime(fecha_fin))]
        st.dataframe(df_filtrado.sort_values(by="fecha", ascending=False), use_container_width=True)
        
        if st.button("📁 Descargar CSV"):
            csv = df.to_csv(index=False)
            st.download_button("✅ Descargar", csv, f"gastos_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
    else:
        st.info("No hay gastos")

st.divider()
st.caption("💰 Control Financiero PRO | 8 categorías | Subcategorías ampliadas")
