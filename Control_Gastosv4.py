import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

st.set_page_config(
    page_title="Control Gastos - Plan Maestro 2028", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Título
st.title("💰 CONTROL DE GASTOS")
st.markdown("**Plan Maestro 2028 · Presupuesto mensual: $13,100**")
st.divider()

# ============================================
# PRESUPUESTO DETALLADO
# ============================================

PRESUPUESTO = {
    "Alimentación - Desayuno/Almuerzo en casa": 2250,
    "Alimentación - Comida fuerte / Salidas": 4450,
    "Alimentación - Cena ligera": 1200,
    "Servicios - Internet": 600,
    "Servicios - Luz": 450,
    "Servicios - Agua": 200,
    "Servicios - Celular": 200,
    "Servicios - Gas": 100,
    "Vivienda - Mantenimiento casa": 1400,
    "Movilidad - Transporte": 750,
    "Ahorro - Fondo emergencia": 1500
}

RUBROS = list(PRESUPUESTO.keys())

# ============================================
# ARCHIVO DE PERSISTENCIA
# ============================================

ARCHIVO_DATOS = "gastos_plan_maestro.csv"

def cargar_gastos():
    """Carga los gastos desde el archivo CSV"""
    if os.path.exists(ARCHIVO_DATOS):
        df = pd.read_csv(ARCHIVO_DATOS)
        df["fecha"] = pd.to_datetime(df["fecha"])
        return df.to_dict('records')
    return []

def guardar_gastos(gastos):
    """Guarda los gastos en el archivo CSV"""
    df = pd.DataFrame(gastos)
    df.to_csv(ARCHIVO_DATOS, index=False)

# ============================================
# INICIALIZACIÓN
# ============================================

if "gastos" not in st.session_state:
    st.session_state.gastos = cargar_gastos()

# ============================================
# VERIFICAR CAMBIO DE MES
# ============================================

ahora = datetime.now()
mes_actual = ahora.strftime("%Y-%m")

mes_guardado = None
if st.session_state.gastos:
    primera_fecha = st.session_state.gastos[0]["fecha"]
    if isinstance(primera_fecha, str):
        primera_fecha = pd.to_datetime(primera_fecha)
    mes_guardado = primera_fecha.strftime("%Y-%m")

if mes_guardado and mes_guardado != mes_actual:
    st.session_state.gastos = []
    guardar_gastos([])
    st.rerun()

# ============================================
# ENTRADA DE GASTOS (con negativos)
# ============================================

st.subheader("📥 Registrar movimiento")

col1, col2, col3, col4 = st.columns([2, 3, 1, 1])

with col1:
    fecha = st.date_input("Fecha", datetime.now())

with col2:
    rubro = st.selectbox("Rubro", RUBROS)

with col3:
    monto = st.number_input("Monto ($)", value=0.0, step=10.0, format="%.2f")

with col4:
    st.write("")
    st.write("")
    if st.button("➕ Agregar", use_container_width=True):
        if monto != 0:
            nuevo_gasto = {
                "fecha": fecha.strftime("%Y-%m-%d"),
                "rubro": rubro,
                "monto": monto
            }
            st.session_state.gastos.append(nuevo_gasto)
            guardar_gastos(st.session_state.gastos)
            st.success("✅ Movimiento registrado")
            st.rerun()
        else:
            st.warning("El monto no puede ser cero")

st.divider()

# ============================================
# TABLA DE GASTOS
# ============================================

if st.session_state.gastos:
    df = pd.DataFrame(st.session_state.gastos)
    df["fecha"] = pd.to_datetime(df["fecha"])

    st.subheader("📋 Movimientos del mes")

    # Mostrar tabla
    df_display = df.copy()
    df_display["fecha"] = df_display["fecha"].dt.strftime("%d/%m")
    df_display["monto"] = df_display["monto"].apply(lambda x: f"${x:,.2f}")
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # Botones de acción
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        if st.button("🗑️ Reiniciar mes", use_container_width=True):
            st.session_state.gastos = []
            guardar_gastos([])
            st.rerun()
    
    with col_b2:
        if st.button("🔄 Recargar", use_container_width=True):
            st.rerun()

    st.divider()

# ============================================
# ANÁLISIS POR RUBRO
# ============================================

st.subheader("📊 Control por rubro")

if st.session_state.gastos:
    df = pd.DataFrame(st.session_state.gastos)
    resumen = df.groupby("rubro")["monto"].sum().reset_index()
    resumen["presupuesto"] = resumen["rubro"].map(PRESUPUESTO)
    resumen["disponible"] = resumen["presupuesto"] - resumen["monto"]
    resumen["% gastado"] = (resumen["monto"] / resumen["presupuesto"] * 100).round(1)

    # Tabla resumen
    resumen_display = resumen.copy()
    resumen_display["monto"] = resumen_display["monto"].apply(lambda x: f"${x:,.2f}")
    resumen_display["presupuesto"] = resumen_display["presupuesto"].apply(lambda x: f"${x:,.2f}")
    resumen_display["disponible"] = resumen_display["disponible"].apply(lambda x: f"${x:,.2f}")
    resumen_display["% gastado"] = resumen_display["% gastado"].apply(lambda x: f"{x}%")
    st.dataframe(resumen_display, use_container_width=True, hide_index=True)

    # Alertas
    alertas = False
    for i, row in resumen.iterrows():
        if row["disponible"] < 0:
            st.error(f"❌ Te pasaste en {row['rubro']} por ${-row['disponible']:,.2f}")
            alertas = True
        elif row["disponible"] < row["presupuesto"] * 0.1 and row["disponible"] > 0:
            st.warning(f"⚠️ En {row['rubro']} solo queda ${row['disponible']:,.2f}")
            alertas = True

    if not alertas:
        st.success("✅ Todo dentro del presupuesto")

    # Total general
    st.divider()
    total_gastado = df["monto"].sum()
    disponible_total = 13100 - total_gastado
    st.metric(
        "💰 Total gastado", 
        f"${total_gastado:,.2f}", 
        delta=f"${disponible_total:,.2f} disponible",
        delta_color="inverse" if disponible_total < 0 else "normal"
    )

else:
    st.info("Aún no hay movimientos este mes")

st.divider()

# ============================================
# RESPALDO DE DATOS (NUEVO)
# ============================================

st.subheader("📦 Respaldo y recuperación")

col_r1, col_r2 = st.columns(2)

with col_r1:
    if st.session_state.gastos:
        df_respaldo = pd.DataFrame(st.session_state.gastos)
        csv = df_respaldo.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar respaldo CSV",
            data=csv,
            file_name=f"gastos_{datetime.now().strftime('%Y%m')}.csv",
            mime="text/csv",
            use_container_width=True
        )

with col_r2:
    archivo_subido = st.file_uploader("📤 Cargar respaldo", type=['csv'])

if archivo_subido is not None:
    try:
        df_cargado = pd.read_csv(archivo_subido)
        nuevos_gastos = df_cargado.to_dict('records')
        st.session_state.gastos = nuevos_gastos
        guardar_gastos(st.session_state.gastos)
        st.success("✅ Datos cargados correctamente")
        st.rerun()
    except Exception as e:
        st.error(f"Error al cargar: {e}")

st.divider()

# ============================================
# RECORDATORIO DEL PLAN MAESTRO
# ============================================

st.subheader("🎯 Plan Maestro (aparte)")
st.markdown("""
- **Aportación mensual:** $3,500 (desde pensión)
- **Destino:** Inversión a 10% anual
- **Este dinero NO se toca para gastos diarios.**

> *"Control total, desde cualquier lugar."*
""")

st.caption(f"Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
