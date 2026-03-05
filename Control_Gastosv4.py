import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# ============================================
# CONFIGURACIÓN INICIAL
# ============================================
st.set_page_config(
    page_title="💰 Control de Gastos",
    page_icon="💰",
    layout="centered"
)

# Ocultar menús
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ============================================
# DATOS BÁSICOS
# ============================================
PRESUPUESTO_TOTAL = 13100
ARCHIVO_DATOS = "gastos.json"

# ============================================
# FUNCIONES
# ============================================
def cargar_gastos():
    if os.path.exists(ARCHIVO_DATOS):
        with open(ARCHIVO_DATOS, 'r') as f:
            return json.load(f)
    return []

def guardar_gastos(gastos):
    with open(ARCHIVO_DATOS, 'w') as f:
        json.dump(gastos, f, indent=2)

# ============================================
# INICIALIZAR
# ============================================
if 'gastos' not in st.session_state:
    st.session_state.gastos = cargar_gastos()

# ============================================
# TÍTULO
# ============================================
st.title("💰 Control de Gastos")
st.caption("Ing. Roberto Villarreal")

# ============================================
# MÉTRICAS PRINCIPALES
# ============================================
gastos_mes = [g for g in st.session_state.gastos]
total_gastado = sum(g['monto'] for g in gastos_mes) if gastos_mes else 0
restante = PRESUPUESTO_TOTAL - total_gastado
porcentaje = (total_gastado / PRESUPUESTO_TOTAL) * 100

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("PRESUPUESTO", f"${PRESUPUESTO_TOTAL:,.0f}")
with col2:
    st.metric("GASTADO", f"${total_gastado:,.0f}", f"{porcentaje:.1f}%")
with col3:
    st.metric("RESTANTE", f"${restante:,.0f}")

# ============================================
# FORMULARIO PARA AGREGAR GASTOS
# ============================================
with st.form("nuevo_gasto"):
    st.subheader("➕ Agregar gasto")
    
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Fecha", datetime.now())
        categoria = st.selectbox("Categoría", ["Alimentación", "Servicios", "Vivienda", "Transporte", "Otros"])
    with col2:
        monto = st.number_input("Monto ($)", min_value=1, step=10)
        descripcion = st.text_input("Descripción")
    
    if st.form_submit_button("Guardar gasto"):
        st.session_state.gastos.append({
            'fecha': fecha.strftime('%Y-%m-%d'),
            'categoria': categoria,
            'descripcion': descripcion,
            'monto': monto
        })
        guardar_gastos(st.session_state.gastos)
        st.success("✅ Gasto guardado")
        st.rerun()

# ============================================
# LISTA DE GASTOS
# ============================================
if st.session_state.gastos:
    st.subheader("📋 Últimos gastos")
    df = pd.DataFrame(st.session_state.gastos[-10:][::-1])
    st.dataframe(df, use_container_width=True)

# ============================================
# BOTÓN PARA REINICIAR
# ============================================
if st.button("🔄 Reinizar datos"):
    st.session_state.gastos = []
    guardar_gastos([])
    st.rerun()
