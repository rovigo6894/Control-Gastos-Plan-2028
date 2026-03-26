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

# Subcategorías ampliadas (más opciones)
SUBCATEGORIAS = {
    "Alimentación": ["Despensa supermercado", "Comida fuera", "Antojos", "Bebidas", "Café", "Panadería", "Carnes", "Verduras", "Fruta", "Botanas"],
    "Servicios": ["Luz", "Agua", "Gas", "Internet", "Teléfono móvil", "Teléfono fijo", "Netflix", "Spotify", "Prime Video", "Mantenimiento"],
    "Vivienda": ["Renta", "Hipoteca", "Mantenimiento", "Artículos hogar", "Limpiadores", "Muebles", "Electrodomésticos", "Decoración", "Jardinería"],
    "Transporte": ["Gasolina", "Mantenimiento auto", "Pasajes", "Estacionamiento", "Taxi/Uber", "Didi", "Renta de auto", "Lavado auto"],
    "Ahorro": ["Ahorro mensual", "Fondo emergencia", "Inversiones", "Meta específica", "Retiro", "Viajes", "Educación hijos"],
    "Salud": ["Farmacia", "Consultas médicas", "Dentista", "Terapias", "Medicamentos", "Seguro médico", "Gimnasio", "Nutrición"],
    "Educación": ["Colegiaturas", "Libros", "Material escolar", "Cursos", "Talleres", "Idiomas", "Computadora", "Software"],
    "Entretenimiento": ["Cine", "Conciertos", "Restaurantes", "Bares", "Hobbies", "Deportes", "Videojuegos", "Suscripciones"]
}

# Colores para gráficas
COLORES = px.colors.qualitative.Set3

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
    st.markdown("""
        <style>
            .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        </style>
    """, unsafe_allow_html=True)
    st.title("🔐 Control Financiero PRO")
    st.markdown("### Acceso seguro")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Entrar", use_container_width=True):
        if pwd == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("❌ Contraseña incorrecta")
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
st.markdown("""
    <style>
        .metric-card {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            color: #ffd700;
        }
        .metric-label {
            font-size: 0.9rem;
            color: #fff;
            opacity: 0.9;
        }
    </style>
""", unsafe_allow_html=True)

st.title("💰 Control Financiero PRO")
st.markdown("### Sistema inteligente de gestión de gastos")

if not df.empty:
    total = df["monto"].sum()
    dias = datetime.now().day
    proyeccion = (total / dias) * 30 if dias > 0 else 0
    restante = total_presupuesto - total
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">${total:,.0f}</div>
                <div class="metric-label">Gastado</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">${proyeccion:,.0f}</div>
                <div class="metric-label">Proyección mensual</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">${restante:,.0f}</div>
                <div class="metric-label">Presupuesto restante</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        porcentaje_uso = (total / total_presupuesto * 100) if total_presupuesto > 0 else 0
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{porcentaje_uso:.1f}%</div>
                <div class="metric-label">Uso del presupuesto</div>
            </div>
        """, unsafe_allow_html=True)

st.divider()

# =============================
# TABS PARA ORGANIZAR
# =============================
tab1, tab2, tab3, tab4 = st.tabs(["📝 Registrar gasto", "✏️ Editar presupuestos", "📊 Análisis", "📋 Historial"])

with tab1:
    st.subheader("➕ Nuevo gasto")
    
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("📅 Fecha", datetime.now())
        rubro = st.selectbox("📂 Categoría", list(presupuestos.keys()))
        
        # Subcategorías dinámicas
        subcategoria_opciones = SUBCATEGORIAS[rubro]
        subcategoria = st.selectbox("🏷️ Subcategoría", subcategoria_opciones)
    
    with col2:
        monto = st.number_input("💰 Monto ($)", step=10.0, min_value=0.0, format="%.2f")
        st.markdown("---")
        st.markdown("### 📝 Descripción opcional")
        descripcion = st.text_area("", placeholder="Ej: Compras del supermercado", height=68)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Guardar gasto", use_container_width=True, type="primary"):
            if monto > 0:
                guardar_gasto(fecha.strftime("%Y-%m-%d"), rubro, subcategoria, monto)
                st.success(f"✅ Guardado: {rubro} → {subcategoria} | ${monto:,.2f}")
                st.rerun()
            else:
                st.warning("⚠️ Ingresa un monto válido")
    with col2:
        if st.button("🗑️ Eliminar último gasto", use_container_width=True):
            eliminar_ultimo()
            st.warning("Último gasto eliminado")
            st.rerun()

with tab2:
    st.subheader("✏️ Ajustar presupuestos mensuales")
    st.caption("Modifica los valores según tus necesidades")
    
    nuevos_presupuestos = {}
    cols = st.columns(3)
    for i, (rubro, monto_actual) in enumerate(presupuestos.items()):
        with cols[i % 3]:
            nuevo = st.number_input(f"💰 {rubro}", value=float(monto_actual), step=100.0, key=f"pres_{rubro}", format="%.0f")
            nuevos_presupuestos[rubro] = nuevo
    
    if st.button("💾 Guardar todos los presupuestos", use_container_width=True, type="primary"):
        for rubro, monto in nuevos_presupuestos.items():
            guardar_presupuesto(rubro, monto)
        st.success("✅ Presupuestos actualizados correctamente")
        st.rerun()

with tab3:
    if not df.empty:
        # Resumen por rubro
        resumen = df.groupby("rubro")["monto"].sum().reset_index()
        resumen["presupuesto"] = resumen["rubro"].map(presupuestos)
        resumen["uso %"] = (resumen["monto"] / resumen["presupuesto"] * 100).fillna(0)
        
        # Alertas
        st.subheader("🚨 Alertas inteligentes")
        top = resumen.sort_values(by="uso %", ascending=False).iloc[0]
        
        if top["uso %"] > 100:
            st.error(f"⚠️ EXCESO en **{top['rubro']}** - Has superado el presupuesto en **{top['uso %']:.0f}%**")
        elif top["uso %"] > 80:
            st.warning(f"📌 ALERTA en **{top['rubro']}** - Has usado **{top['uso %']:.0f}%** de tu presupuesto")
        else:
            st.success("✅ Todo en orden. Buen control de gastos")
        
        # Gráficas
        st.subheader("📊 Distribución de gastos")
        
        col1, col2 = st.columns(2)
        with col1:
            fig_pie = px.pie(resumen, names="rubro", values="monto", title="Por categoría", color_discrete_sequence=COLORES)
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Gastos por día
            gastos_por_dia = df.groupby(df["fecha"])["monto"].sum().reset_index()
            fig_line = px.line(gastos_por_dia, x="fecha", y="monto", title="Evolución diaria")
            fig_line.update_layout(height=400)
            st.plotly_chart(fig_line, use_container_width=True)
        
        # Estado por categoría
        st.subheader("📊 Estado por categoría")
        for _, row in resumen.iterrows():
            porcentaje = row["uso %"]
            if porcentaje > 100:
                st.error(f"**{row['rubro']}**: ${row['monto']:,.0f} / ${row['presupuesto']:,.0f} ({porcentaje:.0f}%) 🔴 EXCEDIDO")
            elif porcentaje > 80:
                st.warning(f"**{row['rubro']}**: ${row['monto']:,.0f} / ${row['presupuesto']:,.0f} ({porcentaje:.0f}%) 🟡 CUIDADO")
            else:
                st.success(f"**{row['rubro']}**: ${row['monto']:,.0f} / ${row['presupuesto']:,.0f} ({porcentaje:.0f}%) 🟢 OK")
        
        # Detalle por subcategoría
        st.subheader("📋 Detalle por subcategoría")
        detalle_sub = df.groupby(["rubro", "subcategoria"])["monto"].sum().reset_index()
        detalle_sub = detalle_sub.sort_values("monto", ascending=False)
        st.dataframe(detalle_sub, use_container_width=True, height=300)
        
    else:
        st.info("📝 No hay gastos registrados aún. Agrega tu primer gasto en la pestaña 'Registrar gasto'")

with tab4:
    if not df.empty:
        st.subheader("📋 Historial completo de movimientos")
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.date_input("Desde", df["fecha"].min())
        with col2:
            fecha_fin = st.date_input("Hasta", df["fecha"].max())
        
        df_filtrado = df[(df["fecha"] >= pd.to_datetime(fecha_inicio)) & (df["fecha"] <= pd.to_datetime(fecha_fin))]
        st.dataframe(df_filtrado.sort_values(by="fecha", ascending=False), use_container_width=True, height=400)
        
        # Botón de respaldo
        if st.button("📁 Descargar respaldo completo (CSV)", use_container_width=True):
            csv = df.to_csv(index=False)
            st.download_button(
                label="✅ Haz clic para descargar",
                data=csv,
                file_name=f"gastos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("📝 No hay gastos registrados aún")

st.divider()
st.caption("💰 Control Financiero PRO v2.0 | 8 categorías | Subcategorías ampliadas | Alertas inteligentes | Diseño profesional")
